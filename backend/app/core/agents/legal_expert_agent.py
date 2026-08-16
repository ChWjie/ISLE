"""
Legal Expert Agent

Wrapper for specialized legal expert agents to work as managed sub-agents.
Each expert has specific legal domain knowledge and analysis capabilities.
"""

from typing import List, Dict, Any, Optional
import json

from app.core.agents.multistep_agent import MultiStepAgent, ActionStep
from app.core.agents.memory import ChatMessage, MessageRole
from app.core.llm.base import BaseLLM


class LegalExpertAgent(MultiStepAgent):
    """
    Legal Expert Agent - specialized legal domain expert

    Wraps existing legal expert templates to work within the multi-agent framework.
    Each expert analyzes events from their specialized perspective.
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        law_domains: List[str],
        description: str,
        model: BaseLLM,
        max_steps: int = 3,  # Legal experts typically need fewer steps
        **kwargs
    ):
        super().__init__(
            model=model,
            max_steps=max_steps,
            name=agent_id,
            description=description,
            provide_run_summary=True,  # Provide summary when called as managed agent
            **kwargs
        )

        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.law_domains = law_domains
        self.expert_description = description

    def initialize_system_prompt(self) -> str:
        """Initialize system prompt for legal expert"""
        return f"""你是一个顶尖的{self.agent_name} ({self.agent_type})，拥有30年以上法律与合规实务经验和深厚的专业积累。

你的核心专业领域: {', '.join(self.law_domains)}。

{self.expert_description}

你的任务是：基于你的专业视角，对复杂的企业合规与争议事件进行**“白皮书级”的详尽法理推演**。不仅要给出结论，更要展示完整的论证过程。

**分析原则（必须严格遵守）：**
1. **详尽与深度**：拒绝任何形式的简略。每一个论点都必须展开论述，说明理由、依据及逻辑关联。分析内容应具有相当的篇幅和厚度。
2. **多维视角**：不仅分析条文本身，还要结合立法原意、国家实践、监管口径、裁判规则、行业惯例以及业务背景。
3. **精确引用**：必须具体到特定的法律文件、条款号（例如“《个人信息保护法》第13条”）。
4. **对抗性推演**：必须预判对手不仅会如何反驳，还会引用哪些具体条款，并针对性地构建再反驳逻辑。
5. **实务落地**：分析结果必须能够转化为具体的外交或法律行动指南。

输出必须展现出法律权威的严谨性与全面性。每一个字都应经得起推敲。
"""

    async def _execute_step(self, step_number: int) -> ActionStep:
        """
        Execute legal analysis step

        Calls LLM to generate structured legal analysis
        """
        if step_number > 1:
            # Legal experts typically complete in one step
            return ActionStep(
                step_number=step_number,
                observation="分析已完成",
                is_final_answer=True
            )

        # Prepare analysis prompt
        analysis_prompt = f"""【待分析事件】：
{self.task}

作为{self.agent_name}，请撰写一份**详尽的法律分析意见书**。

请严格按照以下结构进行深度思考和长文本输出（JSON格式）：

1. **核心争点识别 (key_issues)**: 详细列出本事件在法律层面的3-5个核心争议焦点，并简述理由。
2. **深度法理分析 (analysis)**: 这是报告的核心。针对每个争点进行长篇幅的论证。必须包含：
   - 法理依据的详细拆解
   - 事实与法律的涵摄过程
   - 类似历史先例的类比分析
3. **精准法律依据 (legal_basis)**: 列出至少5条确切的条文、判例或习惯法规则。
4. **对手观点预判 (counter_arguments)**: 站在对手角度，预测他们最强有力的2-3个法律反击点。
5. **我方反驳策略 (rebuttals)**: 针对上述对手观点，提供具体的法理回击逻辑。
6. **实务建议 (recommendations)**: 提出具体的外交声明措辞建议或法律行动步骤。
7. **战略影响评估 (strategic_impact)**: 分析该法律立场对长远地缘政治格局的影响。
8. **置信度 (confidence)**: 0.0-1.0。

输出JSON格式如下（**确保内容丰富、详实**）：
{{
    "key_issues": ["争点1...", "争点2..."],
    "analysis": "（此处需要生成长文本，包含分段论述）...",
    "legal_basis": ["依据1...", "依据2..."],
    "counter_arguments": ["对手观点1...", "对手观点2..."],
    "rebuttals": ["反驳1...", "反驳2..."],
    "recommendations": ["建议1...", "建议2..."],
    "strategic_impact": "战略影响分析...",
    "risks": ["风险1...", "风险2..."],
    "confidence": 0.95
}}
"""

        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=self.system_prompt),
            ChatMessage(role=MessageRole.USER, content=analysis_prompt)
        ]

        try:
            # Call LLM to generate analysis
            response = await self.model.generate_json(
                analysis_prompt,
                self.system_prompt
            )

            # Format result
            result = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "agent_type": self.agent_type,
                "law_domains": self.law_domains,
                "key_issues": response.get("key_issues", []),
                "analysis": response.get("analysis", ""),
                "legal_basis": response.get("legal_basis", []),
                "counter_arguments": response.get("counter_arguments", []),
                "rebuttals": response.get("rebuttals", []),
                "recommendations": response.get("recommendations", []),
                "strategic_impact": response.get("strategic_impact", ""),
                "risks": response.get("risks", []),
                "confidence": response.get("confidence", 0.5)
            }

            # Format as readable text
            observation = self._format_analysis_result(result)

            return ActionStep(
                step_number=step_number,
                agent_name=self.agent_name,
                action="legal_analysis",
                action_input={"task": self.task},
                observation=observation,
                is_final_answer=True
            )

        except Exception as e:
            # Fallback if JSON generation fails
            error_msg = f"分析失败: {str(e)}"

            return ActionStep(
                step_number=step_number,
                agent_name=self.agent_name,
                error=error_msg,
                observation=f"无法完成分析：{error_msg}",
                is_final_answer=True
            )

    def _format_analysis_result(self, result: Dict[str, Any]) -> str:
        """Format analysis result as readable text"""
        formatted = f"""## {result['agent_name']} 深度法律分析报告

**专业领域**: {', '.join(result['law_domains'])}

### 1. 核心争议焦点
"""
        for i, issue in enumerate(result.get('key_issues', []), 1):
            formatted += f"{i}. {issue}\n"

        formatted += f"""
### 2. 深度法理分析
{result['analysis']}

### 3. 法理博弈推演
**对手主要抗辩预判**：
"""
        for i, arg in enumerate(result.get('counter_arguments', []), 1):
            formatted += f"- [对手] {arg}\n"

        formatted += "\n**我方回击策略**：\n"
        for i, reb in enumerate(result.get('rebuttals', []), 1):
            formatted += f"- [我方] {reb}\n"

        formatted += "\n### 4. 精准法律依据\n"
        for i, basis in enumerate(result.get('legal_basis', []), 1):
            formatted += f"{i}. {basis}\n"

        formatted += "\n### 5. 实务建议与行动\n"
        for i, rec in enumerate(result.get('recommendations', []), 1):
            formatted += f"{i}. {rec}\n"

        if result.get('strategic_impact'):
            formatted += f"\n### 6. 战略影响评估\n{result.get('strategic_impact')}\n"

        if result.get('risks'):
            formatted += "\n### 7. 潜在风险\n"
            for i, risk in enumerate(result['risks'], 1):
                formatted += f"{i}. {risk}\n"

        formatted += f"\n**置信度**: {result.get('confidence', 0.5):.2f}\n"

        return formatted

    async def _provide_final_answer(self, task: str, images: Optional[List[Any]] = None) -> str:
        """Provide final answer (fallback)"""
        return f"{self.agent_name} 分析完成"


def create_legal_expert_from_template(template: Dict[str, Any], model: BaseLLM) -> LegalExpertAgent:
    """
    Create a LegalExpertAgent from an agent template

    Args:
        template: Agent template dictionary with id, name, type, law_domains, description
        model: LLM model to use

    Returns:
        LegalExpertAgent instance
    """
    return LegalExpertAgent(
        agent_id=template["id"],
        agent_name=template["name"],
        agent_type=template["type"],
        law_domains=template["law_domains"],
        description=template["description"],
        model=model
    )
