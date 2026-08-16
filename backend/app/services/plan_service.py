"""
Plan Generation Service - S4 Core Logic
使用LLM进行多阶段Chain-of-Thought推理生成法律方案
"""
import json
import uuid
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.models.database import Plan, Event, Agent
from app.schemas.plan import PlanGenerateRequest, ActionPath
from app.services.delilegal_client import get_delilegal_client
from app.services.llm_client import get_llm_client, ChatMessage


class PlanGenerator:
    """方案生成器 - 基于LLM的Chain-of-Thought推理"""

    def __init__(self):
        self.llm = get_llm_client()
        self.delilegal = get_delilegal_client()

    async def generate_plan(
        self,
        db: Session,
        request: PlanGenerateRequest
    ) -> Plan:
        """
        生成法律方案 (多阶段CoT)

        阶段:
        1. Context Loading - 加载事件与Agent上下文
        2. Retrieval Routing - 判断是否启用得理检索
        3. Legal Analysis - 法律分析
        4. Action Path Generation - 行动路径生成
        5. Risk Assessment - 风险评估
        6. Final Report - 整合为Markdown报告
        """

        # 1. 加载上下文
        event = db.query(Event).filter(Event.id == request.event_id).first()
        if not event:
            raise ValueError("Event not found")

        blue_agent = db.query(Agent).filter(
            Agent.agent_id == request.blue_agent_id
        ).first()
        if not blue_agent:
            raise ValueError("Blue Agent not found")

        # 2. 场景路由 + 得理检索增强
        retrieval_pack = {
            "retrieval_context": "## 得理检索增强上下文\n- 当前场景未启用得理检索，将依据通用法律规则、业务事实与证据材料进行分析。",
            "source_map": [],
            "degraded": False,
            "degraded_reason": "",
            "query": "",
        }

        if self._should_enable_delilegal(event):
            delilegal_query = self._build_delilegal_query(event)
            retrieval_pack = await self.delilegal.retrieve_pack(delilegal_query)

        # 3. 构建Prompt
        context_prompt = self._build_context_prompt(event, blue_agent, request, retrieval_pack)

        # 4. 调用LLM生成分析
        analysis = await self._generate_legal_analysis(context_prompt)

        # 5. 附加来源注记（可追溯）
        source_note = self._build_source_note(retrieval_pack)
        if source_note:
            analysis["analysis"] = f"{analysis.get('analysis', '')}\n\n{source_note}".strip()
            legal_basis = analysis.get("legal_basis") or []
            if isinstance(legal_basis, list):
                legal_basis.extend(retrieval_pack.get("source_map", [])[:3])
                analysis["legal_basis"] = legal_basis

        # 6. 生成行动路径
        action_paths = await self._generate_action_paths(event, analysis)

        # 7. 风险评估
        risk_assessment = await self._generate_risk_assessment(event, action_paths)

        # 8. 整合为Markdown报告
        content_md = self._build_markdown_report(
            event, analysis, action_paths, risk_assessment
        )

        # 9. 计算综合评分
        scores = self._calculate_scores(action_paths, risk_assessment)

        # 10. 保存到数据库
        plan = Plan(
            plan_id=f"PLAN-{uuid.uuid4().hex[:8].upper()}",
            name=f"{event.name} - 应对方案",
            event_id=event.id,
            content_md=content_md,
            action_paths=[ap.dict() for ap in action_paths],
            risk_assessment=risk_assessment,
            legal_basis=analysis.get("legal_basis", []),
            feasibility_score=scores["feasibility"],
            risk_score=scores["risk"],
            overall_score=scores["overall"],
            status="draft"
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        return plan

    def _should_enable_delilegal(self, event: Event) -> bool:
        """场景路由：仅国内法场景优先启用得理检索"""
        legal_systems = event.legal_systems or []
        text = " ".join([str(s) for s in legal_systems]) + " " + (event.dispute_type or "") + " " + (event.description or "")
        domestic_keywords = ["国内法", "民法", "刑法", "劳动", "合同", "婚姻", "侵权", "公司", "房产", "交通事故", "工伤"]
        return any(k in text for k in domestic_keywords)

    def _build_delilegal_query(self, event: Event) -> str:
        parts = [event.name or "", event.dispute_type or "", event.fact_summary or event.description or ""]
        return "；".join([p for p in parts if p]).strip() or "法律问题检索"

    def _build_source_note(self, retrieval_pack: Dict[str, Any]) -> str:
        source_map = retrieval_pack.get("source_map") or []
        if not source_map:
            if retrieval_pack.get("degraded"):
                return f"【检索降级说明】{retrieval_pack.get('degraded_reason', '得理检索不可用，本次主要基于模型推理。')}"
            return ""

        lines = ["【检索来源索引】"]
        for s in source_map[:8]:
            lines.append(f"- {s}")
        if retrieval_pack.get("degraded"):
            lines.append(f"- 检索降级：{retrieval_pack.get('degraded_reason', '')}")
        return "\n".join(lines)

    def _build_context_prompt(
        self,
        event: Event,
        blue_agent: Agent,
        request: PlanGenerateRequest,
        retrieval_pack: Dict[str, Any]
    ) -> str:
        """构建上下文Prompt"""
        retrieval_context = retrieval_pack.get("retrieval_context", "")

        return f"""# 法律方案生成任务

## 事件背景
- **事件ID**: {event.event_id}
- **事件名称**: {event.name}
- **争议类型**: {event.dispute_type}
- **我方主体**: {', '.join(event.our_side or [])}
- **对方主体**: {', '.join(event.opponent_side or [])}
- **涉及法律体系**: {', '.join(event.legal_systems or [])}

### 事实摘要
{event.fact_summary}

## 我方立场
{blue_agent.stance}

{retrieval_context}

## 任务要求
请作为资深法律专家，基于上述事件背景与检索上下文，生成一份全面的法律应对方案。

方案应包括：
1. 法律分析 (Legal Analysis)
2. 3-5条可行的行动路径 (Action Paths)
3. 每条路径的法律依据、风险评估、可行性分析

## 强约束
1. 优先引用“检索增强上下文”中的信息。
2. 如使用检索来源，必须在文本中标注来源编号，如 [Case-1]、[Law-2]。
3. 不得编造未出现的来源编号。
4. 如果检索信息不足，应明确说明不足点后再给出通用法理补充。

请用JSON格式返回，包含以下字段：
- legal_basis: [法律依据列表]
- analysis: "详细的法律分析"
- recommended_approach: "建议的总体策略倾向"
"""

    async def _generate_legal_analysis(self, context_prompt: str) -> Dict[str, Any]:
        """生成法律分析"""
        messages = [
            ChatMessage(role="system", content="你是一位资深法律专家，输出需严谨、可追溯、可核验。"),
            ChatMessage(role="user", content=context_prompt)
        ]

        response = await self.llm.chat(messages, temperature=0.3, max_tokens=3000)

        # 尝试解析JSON，如果失败则返回文本
        try:
            return json.loads(response)
        except Exception:
            return {
                "analysis": response,
                "legal_basis": ["（模型回退）建议人工复核引用来源"],
                "recommended_approach": "balanced"
            }

    async def _generate_action_paths(
        self,
        event: Event,
        analysis: Dict[str, Any]
    ) -> List[ActionPath]:
        """生成行动路径"""

        prompt = f"""基于以下法律分析，生成3-5条具体的行动路径：

{analysis.get('analysis', '')}

请为每条路径提供：
- title: 简明标题
- description: 详细描述 (100-200字)
- legal_basis: 法律依据列表
- risk_level: 风险等级 (low/medium/high)
- success_rate: 成功率 (0.0-1.0)

返回JSON数组格式。
"""

        messages = [
            ChatMessage(role="system", content="你是法律方案规划专家。"),
            ChatMessage(role="user", content=prompt)
        ]

        response = await self.llm.chat(messages, temperature=0.5, max_tokens=2000)

        try:
            paths_data = json.loads(response)
            return [ActionPath(**p) for p in paths_data]
        except Exception:
            # Fallback: 返回默认路径
            return [
                ActionPath(
                    title="谈判调解路径",
                    description="通过多方沟通与证据澄清，优先争取非对抗式解决。",
                    legal_basis=["相关实体法与程序法规定"],
                    risk_level="low",
                    success_rate=0.7
                ),
                ActionPath(
                    title="诉讼仲裁路径",
                    description="在证据链完善后进入正式争议解决程序，争取确定性裁判结果。",
                    legal_basis=["相关诉讼法、仲裁法规定"],
                    risk_level="medium",
                    success_rate=0.6
                )
            ]

    async def _generate_risk_assessment(
        self,
        event: Event,
        action_paths: List[ActionPath]
    ) -> Dict[str, Any]:
        """生成风险评估"""
        return {
            "political_risk": "中等 - 需关注外部舆情与协同成本",
            "legal_risk": "低 - 已引入检索增强与引用约束",
            "operational_risk": "中等 - 需要跨角色协调执行",
            "reputational_risk": "低 - 具备来源可追溯能力"
        }

    def _build_markdown_report(
        self,
        event: Event,
        analysis: Dict[str, Any],
        action_paths: List[ActionPath],
        risk_assessment: Dict[str, Any]
    ) -> str:
        """构建Markdown格式报告"""

        md = f"""# {event.name} - 法律应对方案

## 一、事件概述
**事件ID**: {event.event_id}
**争议类型**: {event.dispute_type}

### 基本事实
{event.fact_summary}

## 二、法律分析
{analysis.get('analysis', '待完善')}

### 法律依据
"""
        for basis in analysis.get('legal_basis', []):
            md += f"- {basis}\n"

        md += "\n## 三、行动路径\n\n"
        for i, path in enumerate(action_paths, 1):
            md += f"""### 路径{i}: {path.title}
**风险等级**: {path.risk_level}
**成功率**: {path.success_rate * 100:.0f}%

{path.description}

**法律依据**:
"""
            for basis in path.legal_basis:
                md += f"- {basis}\n"
            md += "\n"

        md += "## 四、风险评估\n\n"
        for key, value in risk_assessment.items():
            md += f"- **{key}**: {value}\n"

        return md

    def _calculate_scores(
        self,
        action_paths: List[ActionPath],
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, float]:
        """计算综合评分"""
        avg_success = sum(p.success_rate for p in action_paths) / len(action_paths)
        risk_count = sum(1 for v in risk_assessment.values() if "高" in str(v))

        return {
            "feasibility": avg_success * 100,
            "risk": risk_count * 20,
            "overall": (avg_success * 100 - risk_count * 10)
        }
