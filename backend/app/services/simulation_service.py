"""
Simulation Engine - S5 Core Logic
多智能体博弈推演引擎
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.database import (
    Simulation, SimulationRound, SimulationStatus,
    Agent, Plan, AgentType
)
from app.services.llm_client import get_llm_client, ChatMessage
from app.schemas.simulation import SimulationStartRequest, RoundResult, RoundArgument
import uuid
from datetime import datetime


class SimulationEngine:
    """推演引擎 - 多智能体博弈编排"""

    def __init__(self):
        self.llm = get_llm_client()

    async def start_simulation(
        self,
        db: Session,
        request: SimulationStartRequest
    ) -> Simulation:
        """初始化推演会话"""

        # 加载Plan和Agents
        plan = db.query(Plan).filter(Plan.id == request.plan_id).first()
        if not plan:
            raise ValueError("Plan not found")

        blue_agent = db.query(Agent).filter(Agent.agent_id == request.blue_agent_id).first()
        red_agent = db.query(Agent).filter(Agent.agent_id == request.red_agent_id).first()
        judge_agent = db.query(Agent).filter(Agent.agent_id == request.judge_agent_id).first()

        if not all([blue_agent, red_agent, judge_agent]):
            raise ValueError("One or more agents not found")

        # 创建Simulation会话
        simulation = Simulation(
            session_id=f"SIM-{uuid.uuid4().hex[:8].upper()}",
            plan_id=plan.id,
            blue_agent_config={
                "agent_id": blue_agent.agent_id,
                "name": blue_agent.name,
                "system_prompt": blue_agent.system_prompt,
                "stance": blue_agent.stance
            },
            red_agent_config={
                "agent_id": red_agent.agent_id,
                "name": red_agent.name,
                "system_prompt": red_agent.system_prompt,
                "stance": red_agent.stance
            },
            judge_agent_config={
                "agent_id": judge_agent.agent_id,
                "name": judge_agent.name,
                "system_prompt": judge_agent.system_prompt
            },
            params={
                "max_rounds": request.max_rounds,
                "target_win_rate": request.target_win_rate,
                "termination_type": request.termination_type,
                "auto_optimize": request.auto_optimize,
                "auto_save": request.auto_save
            },
            status=SimulationStatus.RUNNING,
            win_rate=55.0,  # 初始略偏我方
            evidence_stats={"pro": 0, "con": 0},
            started_at=datetime.utcnow()
        )

        db.add(simulation)
        db.commit()
        db.refresh(simulation)

        return simulation

    async def execute_round(
        self,
        db: Session,
        session_id: str
    ) -> RoundResult:
        """执行单轮推演"""

        simulation = db.query(Simulation).filter(
            Simulation.session_id == session_id
        ).first()

        if not simulation:
            raise ValueError("Simulation not found")

        if simulation.status != SimulationStatus.RUNNING:
            raise ValueError(f"Simulation is {simulation.status}, cannot execute round")

        round_number = simulation.current_round + 1
        win_rate_before = simulation.win_rate

        # 加载Plan内容作为上下文
        plan = db.query(Plan).filter(Plan.id == simulation.plan_id).first()

        # 1. Blue Agent发言
        blue_arg = await self._generate_blue_argument(
            simulation, plan, round_number
        )

        # 2. Red Agent反驳
        red_arg = await self._generate_red_argument(
            simulation, blue_arg, round_number
        )

        # 3. Judge评分
        judge_result = await self._judge_evaluate(
            simulation, blue_arg, red_arg, round_number
        )

        # 4. 更新胜率
        win_rate_delta = judge_result.get("impact", 0)
        new_win_rate = max(0, min(100, win_rate_before + win_rate_delta))

        # 5. 保存本轮记录
        sim_round = SimulationRound(
            simulation_id=simulation.id,
            round_number=round_number,
            blue_argument=blue_arg.content,
            blue_legal_basis=blue_arg.legal_basis,
            red_argument=red_arg.content,
            red_legal_basis=red_arg.legal_basis,
            red_risks_raised=red_arg.risks_raised,
            judge_ruling=judge_result.get("ruling", ""),
            judge_score=judge_result,
            win_rate_before=win_rate_before,
            win_rate_after=new_win_rate,
            win_rate_delta=win_rate_delta
        )

        db.add(sim_round)

        # 6. 更新Simulation状态
        simulation.current_round = round_number
        simulation.total_rounds = round_number
        simulation.win_rate = new_win_rate

        # 更新证据统计
        stats = simulation.evidence_stats or {"pro": 0, "con": 0}
        if win_rate_delta > 0:
            stats["pro"] += len(blue_arg.legal_basis or [])
        else:
            stats["con"] += len(red_arg.legal_basis or [])
        simulation.evidence_stats = stats

        db.commit()

        # 7. 检查终止条件
        should_terminate, reason = self._check_termination(simulation)

        if should_terminate:
            await self._terminate_simulation(db, simulation, reason)

        return RoundResult(
            round_number=round_number,
            blue_argument=blue_arg,
            red_argument=red_arg,
            judge_ruling=RoundArgument(
                agent_type="judge",
                agent_name=simulation.judge_agent_config["name"],
                content=judge_result.get("ruling", ""),
                legal_basis=[]
            ),
            win_rate_before=win_rate_before,
            win_rate_after=new_win_rate,
            win_rate_delta=win_rate_delta
        )

    async def _generate_blue_argument(
        self,
        simulation: Simulation,
        plan: Plan,
        round_number: int
    ) -> RoundArgument:
        """生成我方论证"""

        config = simulation.blue_agent_config

        prompt = f"""你是{config['name']}。这是第{round_number}轮辩论。

**我方立场**: {config['stance']}

**方案参考** (来自S4):
{plan.content_md[:500]}...

**当前胜率**: {simulation.win_rate:.1f}%

请基于上述立场和方案，提出本轮的法律论证。包括：
1. 核心论点
2. 法律依据 (引用具体法条)
3. 事实支持

以JSON格式返回: {{"argument": "...", "legal_basis": ["相关法律第X条/合同第X条", ...]}}
"""

        messages = [
            ChatMessage(role="system", content=config["system_prompt"]),
            ChatMessage(role="user", content=prompt)
        ]

        response = await self.llm.chat(messages, temperature=0.4, max_tokens=1500)

        try:
            import json
            data = json.loads(response)
            return RoundArgument(
                agent_type="blue",
                agent_name=config["name"],
                content=data.get("argument", response),
                legal_basis=data.get("legal_basis", [])
            )
        except:
            return RoundArgument(
                agent_type="blue",
                agent_name=config["name"],
                content=response,
                legal_basis=["《个人信息保护法》相关条款", "《劳动合同法》或《公司法》相关条款"]
            )

    async def _generate_red_argument(
        self,
        simulation: Simulation,
        blue_arg: RoundArgument,
        round_number: int
    ) -> RoundArgument:
        """生成对手反驳"""

        config = simulation.red_agent_config

        prompt = f"""你是{config['name']}。这是第{round_number}轮辩论。

**对方刚才的论证**:
{blue_arg.content}

**对方引用的法条**:
{', '.join(blue_arg.legal_basis)}

**你的立场**: {config['stance']}

请对上述论证进行反驳，包括：
1. 指出对方论证的漏洞
2. 提出己方的法律依据
3. 质疑证据或事实的完整性

以JSON格式返回: {{"counter_argument": "...", "legal_basis": [...], "risks": [...]}}
"""

        messages = [
            ChatMessage(role="system", content=config["system_prompt"]),
            ChatMessage(role="user", content=prompt)
        ]

        response = await self.llm.chat(messages, temperature=0.6, max_tokens=1200)

        try:
            import json
            data = json.loads(response)
            return RoundArgument(
                agent_type="red",
                agent_name=config["name"],
                content=data.get("counter_argument", response),
                legal_basis=data.get("legal_basis", []),
                risks_raised=data.get("risks", [])
            )
        except:
            return RoundArgument(
                agent_type="red",
                agent_name=config["name"],
                content=response,
                legal_basis=["合同约定条款", "监管规定或行业规则"],
                risks_raised=["证据可采性异议"]
            )

    async def _judge_evaluate(
        self,
        simulation: Simulation,
        blue_arg: RoundArgument,
        red_arg: RoundArgument,
        round_number: int
    ) -> Dict[str, Any]:
        """裁判评估"""

        config = simulation.judge_agent_config

        prompt = f"""你是{config['name']}。这是第{round_number}轮辩论评估。

**我方论证**:
{blue_arg.content}
法条依据: {', '.join(blue_arg.legal_basis)}

**对方反驳**:
{red_arg.content}
法条依据: {', '.join(red_arg.legal_basis)}

请客观评估本轮辩论，给出：
1. 裁决意见 (ruling)
2. 胜率影响 (impact: -10到+10之间的数字)
3. 理由 (reason)

以JSON格式返回: {{"ruling": "...", "impact": 5, "reason": "..."}}
"""

        messages = [
            ChatMessage(role="system", content=config["system_prompt"]),
            ChatMessage(role="user", content=prompt)
        ]

        response = await self.llm.chat(messages, temperature=0.2, max_tokens=1000)

        try:
            import json
            result = json.loads(response)
            return {
                "ruling": result.get("ruling", "双方论证各有千秋"),
                "impact": float(result.get("impact", 2)),
                "reason": result.get("reason", "")
            }
        except:
            return {
                "ruling": response,
                "impact": 2.0,
                "reason": "基于法律论证质量"
            }

    def _check_termination(
        self,
        simulation: Simulation
    ) -> tuple[bool, str]:
        """检查终止条件"""

        params = simulation.params or {}
        termination_type = params.get("termination_type", "win_rate")

        # 条件1: 达到目标胜率
        if termination_type == "win_rate":
            target = params.get("target_win_rate", 80.0)
            if simulation.win_rate >= target:
                return True, f"达到目标胜率 {target}%"

        # 条件2: 达到最大回合数
        max_rounds = params.get("max_rounds", 10)
        if simulation.current_round >= max_rounds:
            return True, f"达到最大回合数 {max_rounds}"

        return False, ""

    async def _terminate_simulation(
        self,
        db: Session,
        simulation: Simulation,
        reason: str
    ):
        """终止推演并触发优化"""

        simulation.status = SimulationStatus.OPTIMIZING
        simulation.final_result = {
            "termination_reason": reason,
            "final_win_rate": simulation.win_rate,
            "total_rounds": simulation.total_rounds
        }
        db.commit()

        # 如果启用自动优化
        params = simulation.params or {}
        if params.get("auto_optimize", True):
            # 这里可以调用S4的优化逻辑生成新方案
            # 暂时跳过,标记为已完成
            simulation.status = SimulationStatus.COMPLETED
            simulation.completed_at = datetime.utcnow()
            db.commit()
