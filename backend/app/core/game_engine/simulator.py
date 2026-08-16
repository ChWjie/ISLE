import random
from typing import Dict, Any, List
from threading import Lock
from .rules import GameRuleEngine, GameState
from app.core.llm.factory import LLMFactory

class GameSimulator:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(GameSimulator, cls).__new__(cls)
                    cls._instance.rule_engine = GameRuleEngine()
                    # 初始化LLM，默认尝试OpenAI，如果无Key则内部Adapter会打印警告并返回错误字符串，我们可以在Simulater里处理fallback
                    cls._instance.llm = LLMFactory.create()
        return cls._instance

    def initialize_state(self, session_id: str) -> GameState:
        # 初始状态 (模拟)
        return GameState(
            round_count=0,
            tension_level=50.0,
            diplomatic_progress=20.0,
            evidence_strength=60.0,
            public_opinion=50.0
        )

    async def simulate_round(self, current_state: GameState, plan_context: str,
                            our_agent_config=None, opponent_agent_config=None) -> Dict[str, Any]:
        """
        执行一轮博弈推演
        支持双方智能体配置和方案数据集成
        """

        # 1. 增加回合数
        current_state.round_count += 1

        # 2. 尝试使用LLM生成我方行动
        # 使用自定义提示词或默认提示词
        if our_agent_config and our_agent_config.custom_prompt:
            system_prompt = our_agent_config.custom_prompt
        else:
            system_prompt = """
你是企业法律顾问团队的首席专家，精通公司治理、合同争议、劳动用工、数据合规与监管应对等领域。你的任务是在复杂争议博弈中，为委托方制定下一步的法律与合规策略。

你的专业背景：
- 深刻理解公司法、劳动合同法、个人信息保护法、数据安全法等法律框架
- 熟悉监管问询、行政处罚、仲裁诉讼和内部治理的处置逻辑
- 擅长运用法律论据、历史证据和外交手段维护国家利益

输出格式要求：
请按以下格式输出，用"---"分隔两部分：

第一部分：我方主张（50-80字）
简明扼要地说明我方的具体行动和立场

---

第二部分：法律依据（30-50字）
列出支持该主张的具体法律条款或历史证据，如：
- 依据相关法律法规、合同条款和证据链...
- 根据《中越北部湾划界协定》...
- 历史文献证明...
"""

        # 构建用户提示词，包含方案内容
        plan_section = ""
        if plan_context:
            plan_section = f"""
【参考方案】
以下是我方制定的应对方案，请在此基础上提出具体行动：
{plan_context[:500]}...（方案摘要）
"""

        user_prompt = f"""
【当前博弈态势】
紧张等级: {current_state.tension_level}/100 {'（局势紧张，需谨慎应对）' if current_state.tension_level > 70 else '（局势可控）'}
外交回旋余地: {current_state.diplomatic_progress}/100
证据链强度: {current_state.evidence_strength}/100

【对方上一轮行动】
{current_state.last_their_action if current_state.last_their_action else '对方尚未行动'}

{plan_section}

【任务】
请提出我方的下一步行动方案（包含主张和法律依据两部分）。
"""

        # 并行准备提示词 (虽然有依赖，但在真正发出请求前可以先准备一部分)
        # 为了提高响应速度，我们将尝试并发生成"初步行动意图"，或者暂时改为"互不干涉"的并发模式？
        # 不，为了逻辑连贯性，必须串行。但我们可以设置更短的超时和更简短的回复要求。

        # 优化1：设置更严格的 max_tokens，强制LLM输出短文
        # 优化2：添加 try-except 捕获超时

        # 调用LLM生成我方行动
        try:
            print(f"[Simulator] Requesting Our Action...")
            our_action = await self.llm.generate(user_prompt, system_prompt=system_prompt)
            print(f"[Simulator] Our Action received: {our_action[:20]}...")
        except Exception as e:
            print(f"Our Action LLM Error: {e}")
            our_action = "提升戒备，密切关注局势发展 (系统自动生成)"

        # 检查行动许可 (Rule Engine)
        allowed, reason = self.rule_engine.check_action(current_state, our_action)
        if not allowed:
            our_action = f"原计划被系统阻断。转为：保持战略定力，收集更多证据。"

        # 3. 模拟对方反制
        # 使用对方智能体配置的自定义提示词或默认提示词
        if opponent_agent_config and opponent_agent_config.custom_prompt:
            their_system_prompt = opponent_agent_config.custom_prompt
        else:
            their_system_prompt = """
你是争议对手一方的法律与策略顾问团队负责人。在当前的企业争议或合规冲突中，你需要为委托方制定反制策略。

你的立场和策略：
- 挑战中国的主权主张，质疑其法律依据的有效性
- 寻求国际支持，争取域外大国介入
- 利用国际舆论和法律程序施压
- 在必要时采取实际控制措施

输出格式要求：
请按以下格式输出，用"---"分隔两部分：

第一部分：反制主张（50-80字）
简明扼要地说明对中国行动的反制措施

---

第二部分：法律依据（30-50字）
列出支持该反制的法律论据或规则解释，如：
- 根据合同条款、监管规则或司法解释...
- 援引相关裁判观点或处罚口径...
- 基于实际控制原则...
"""

        their_prompt = f"""
        【中国最新行动】
        {our_action}

        【当前局势】
        紧张度: {current_state.tension_level}/100
        外交空间: {current_state.diplomatic_progress}/100

        【任务】
        请提出针对性的反制方案（包含反制主张和法律依据两部分）。
        """

        try:
            their_action = await self.llm.generate(their_prompt, system_prompt=their_system_prompt)
        except Exception as e:
            print(f"Opponent LLM Error: {e}")
            their_action = "表示严重关切，保留进一步反应权利 (系统自动生成)"

        if "Error" in their_action or "Warning" in their_action:
            their_actions = [
                "表示强烈抗议并拒绝接受我方主张",
                "派遣公务船只进入争议水域",
                "寻求域外大国的介入和支持",
                "威胁暂停双边经贸合作项目"
            ]
            their_action = random.choice(their_actions)

        # 4. 风险检查
        risks = self.rule_engine.check_risks(current_state, our_action + their_action)
        current_state.active_risks.extend(risks)

        # 5. 更新状态 (简单的数值模拟，完善的话也应该用LLM评估)
        # 紧张局势变化
        tension_change = random.randint(-5, 15)
        if "演习" in our_action or "军事" in their_action:
            tension_change += 10
        if "外交" in our_action:
            tension_change -= 5

        current_state.tension_level = max(0, min(100, current_state.tension_level + tension_change))

        # 外交进展变化
        diplo_change = random.randint(-5, 10)
        current_state.diplomatic_progress = max(0, min(100, current_state.diplomatic_progress + diplo_change))

        # 舆论变化
        op_change = random.randint(-5, 10)
        current_state.public_opinion = max(0, min(100, current_state.public_opinion + op_change))

        # 6. 终止检查
        is_terminated, reason = self.rule_engine.check_termination(current_state)
        current_state.is_terminated = is_terminated
        current_state.termination_reason = reason

        # 7. 更新状态以供下一轮使用
        current_state.last_their_action = their_action

        return {
            "round": current_state.round_count,
            "our_action": our_action,
            "their_action": their_action,
            "risks": risks,
            "state": {
                "tension_level": current_state.tension_level,
                "diplomatic_progress": current_state.diplomatic_progress,
                "evidence_strength": current_state.evidence_strength,
                "last_their_action": their_action
            },
            "is_terminated": is_terminated,
            "termination_reason": reason
        }

    def evaluate_result(self, state: GameState) -> Dict[str, Any]:
        """
        评估最终结果
        """
        risk_score = state.tension_level / 10.0 + len(state.active_risks) * 1.5
        risk_score = min(10.0, risk_score)

        if state.is_terminated and "博弈胜利" in state.termination_reason:
            outcome = "success"
        elif state.is_terminated and "博弈失败" in state.termination_reason:
             outcome = "failure"
        elif risk_score > 7:
            outcome = "failure"
        elif risk_score < 4:
            outcome = "success"
        else:
            outcome = "uncertain"

        return {
            "risk_score": risk_score,
            "outcome": outcome,
            "details": state.termination_reason
        }
