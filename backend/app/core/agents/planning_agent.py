"""
Legal Planning Agent

Top-level planning agent that coordinates specialized legal expert sub-agents.
Analyzes legal events, decomposes tasks, and synthesizes expert opinions.
"""

from typing import List, Dict, Any, Optional
import yaml
import os

from app.core.agents.multistep_agent import MultiStepAgent, PlanningStep, ActionStep
from app.core.agents.memory import ChatMessage, MessageRole
from app.core.llm.base import BaseLLM


class LegalPlanningAgent(MultiStepAgent):
    """
    Legal Planning Agent - coordinates legal expert team

    Responsibilities:
    1. Analyze legal event and determine required expertise
    2. Decompose complex legal analysis into sub-tasks
    3. Assign sub-tasks to appropriate legal expert agents
    4. Synthesize sub-agent results into coherent legal plan
    5. Update plan based on intermediate results
    """

    def __init__(
        self,
        model: BaseLLM,
        managed_agents: List[MultiStepAgent] = None,
        max_steps: int = 15,
        planning_interval: int = 5,
        prompt_template_path: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            model=model,
            max_steps=max_steps,
            planning_interval=planning_interval,
            name="legal_planning_agent",
            description="资深法律战略规划专家，协调20位专业法律专家团队",
            **kwargs
        )

        # Load prompt templates
        if prompt_template_path and os.path.exists(prompt_template_path):
            with open(prompt_template_path, 'r', encoding='utf-8') as f:
                self.prompt_templates = yaml.safe_load(f)
        else:
            self.prompt_templates = self._get_default_templates()

        # Add managed agents (legal experts)
        if managed_agents:
            for agent in managed_agents:
                self.add_managed_agent(agent)

    def initialize_system_prompt(self) -> str:
        """Initialize system prompt for legal planning"""
        return self.prompt_templates.get("system_prompt", self._get_default_system_prompt())

    def _get_default_system_prompt(self) -> str:
        """Default system prompt for legal planning agent"""
        return """你是一位资深的法律战略专家，负责协调一个由多位专业法律专家组成的律师团队。

你的职责：
1. 分析国际争议事件，识别涉及的法律领域
2. 将复杂的法律分析任务分解为子任务
3. 选择最合适的专家团队成员处理各个子任务
4. 协调专家之间的协作，确保分析的全面性和一致性
5. 综合所有专家意见，形成连贯的法律应对方案

可用的法律专家包括：
- 公司治理专家：公司法、董监高责任、股权治理
- 数据合规专家：个人信息保护法、数据安全法、网络安全法
- 领土法专家：领土主权、边界划定、历史条约
- 外交法专家：维也纳外交关系公约、外交特权与豁免
- 证据分析专家：证据规则、事实认定、举证路径
- 军事法顾问：武装冲突法、交战规则、海上意外相遇规则
- 国际经济法顾问：WTO规则、国际制裁法、投资争端解决
- 环境法专家：国际环境法、海洋环境保护、环境损害赔偿
- 人权法学者：国际人权公约、人道主义法
- 航空法专家：芝加哥公约、防空识别区、空中航行规则
- 网络法专家：网络主权、数据安全法、塔林手册
- 历史档案专家：历史文献考证、条约解释
- 国际仲裁律师：国际仲裁程序、管辖权异议
- 战略情报分析师：开源情报分析、战略误判评估
- 危机公关顾问：国际舆论法理斗争、信息传播
- 能源法专家：油气共同开发、跨界资源管理
- 渔业法专家：国际渔业协定、非法捕捞
- 刑法专家：国际刑法、海盗罪、管辖权
- 极地法专家：南极条约体系、北极理事会规则
- 比较法专家：普通法系、大陆法系、法律移植

工作流程：
1. 仔细分析事件描述，识别关键法律问题
2. 确定需要哪些领域的专家参与（通常3-8位）
3. 为每位专家分配具体的分析任务
4. 收集并综合专家意见
5. 识别专家意见之间的冲突或互补
6. 形成最终的法律应对方案

输出格式：
- 清晰的分析计划
- 选定的专家及其任务
- 综合的法律建议
- 风险评估和应对策略
"""

    def _get_default_templates(self) -> Dict[str, Any]:
        """Get default prompt templates"""
        return {
            "system_prompt": self._get_default_system_prompt(),
            "planning": {
                "initial_plan": """## 任务分析

事件描述：
{event_description}

事件类型：{event_type}

## 可用专家团队
{available_agents}

## 分析计划

请制定详细的法律分析计划：
1. 识别涉及的主要法律领域
2. 选择3-8位最相关的专家
3. 为每位专家分配具体任务
4. 说明分析的优先级和顺序

请以结构化的方式输出你的计划。""",

                "update_plan": """## 当前进展回顾

已完成的分析：
{completed_analysis}

## 更新分析计划

剩余步骤：{remaining_steps}

请基于当前进展更新分析计划：
1. 评估已获得的信息
2. 识别还需要哪些专家的意见
3. 调整后续分析重点
4. 确保分析的全面性"""
            },
            "synthesis": {
                "final_answer": """## 综合法律方案

基于以下专家的分析结果：
{expert_analyses}

请综合形成最终的法律应对方案，包括：
1. 法律立场和主张
2. 法律依据和论证
3. 可能的法律风险
4. 应对策略和建议
5. 优先级排序

请提供一个连贯、全面的法律方案。"""
            }
        }

    async def _generate_planning_step(self, task: str, step: int) -> PlanningStep:
        """
        Generate planning step for legal analysis

        Analyzes the task and determines which legal experts to involve
        """
        is_first_step = step == 1

        if is_first_step:
            # Initial planning
            prompt = self._format_initial_planning_prompt(task)
        else:
            # Update planning based on progress
            prompt = self._format_update_planning_prompt(task, step)

        # Generate plan using LLM
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=self.system_prompt),
            ChatMessage(role=MessageRole.USER, content=prompt)
        ]

        try:
            # Call LLM to generate plan
            plan_response = await self.model.generate(
                [{"role": msg.role.value, "content": msg.content} for msg in messages]
            )

            plan_text = plan_response if isinstance(plan_response, str) else plan_response.get("content", "")

            # Extract selected agents from plan (simple parsing)
            selected_agents = self._extract_selected_agents(plan_text)

            return PlanningStep(
                step_number=step,
                plan=plan_text,
                selected_agents=selected_agents,
                reasoning=f"{'Initial' if is_first_step else 'Updated'} planning for legal analysis"
            )

        except Exception as e:
            # Fallback planning
            return PlanningStep(
                step_number=step,
                plan=f"分析任务：{task}\n选择相关法律专家进行分析。",
                selected_agents=[],
                reasoning=f"Planning error: {str(e)}"
            )

    def _format_initial_planning_prompt(self, task: str) -> str:
        """Format initial planning prompt"""
        available_agents_text = "\n".join([
            f"- {name}: {agent.description}"
            for name, agent in self.managed_agents.items()
        ])

        template = self.prompt_templates.get("planning", {}).get("initial_plan", "")

        return template.format(
            event_description=task,
            event_type="国际争议事件",  # Could be extracted from task
            available_agents=available_agents_text or "暂无可用专家"
        )

    def _format_update_planning_prompt(self, task: str, step: int) -> str:
        """Format update planning prompt"""
        # Get completed analyses from memory
        completed = []
        for memory_step in self.memory.steps:
            if isinstance(memory_step, ActionStep) and memory_step.observation:
                completed.append(f"- {memory_step.agent_name}: {memory_step.observation[:200]}...")

        completed_text = "\n".join(completed) if completed else "暂无已完成分析"

        template = self.prompt_templates.get("planning", {}).get("update_plan", "")

        return template.format(
            completed_analysis=completed_text,
            remaining_steps=self.max_steps - step
        )

    def _extract_selected_agents(self, plan_text: str) -> List[str]:
        """
        Extract selected agent names from plan text

        Simple keyword matching - could be enhanced with better parsing
        """
        selected = []

        for agent_name in self.managed_agents.keys():
            if agent_name in plan_text or any(keyword in plan_text for keyword in agent_name.split("_")):
                selected.append(agent_name)

        return selected

    async def _execute_step(self, step_number: int) -> ActionStep:
        """
        Execute one step of legal analysis

        Calls selected legal expert agents and collects their analyses
        """
        # Get the latest planning step
        planning_steps = self.memory.get_planning_history()
        if not planning_steps:
            return ActionStep(
                step_number=step_number,
                error="No planning step found",
                is_final_answer=False
            )

        latest_plan = planning_steps[-1]
        selected_agents = latest_plan.selected_agents

        if not selected_agents:
            # No agents selected, provide final answer
            return ActionStep(
                step_number=step_number,
                observation="分析完成，准备生成最终方案",
                is_final_answer=True
            )

        # Call first selected agent (in real implementation, could call multiple in parallel)
        agent_name = selected_agents[0]

        if agent_name not in self.managed_agents:
            return ActionStep(
                step_number=step_number,
                error=f"Agent {agent_name} not found",
                is_final_answer=False
            )

        try:
            # Call the managed agent
            result = await self.call_managed_agent(
                agent_name=agent_name,
                task=self.task
            )

            return ActionStep(
                step_number=step_number,
                agent_name=agent_name,
                action="analyze",
                observation=str(result),
                is_final_answer=(len(selected_agents) == 1)  # Final if only one agent
            )

        except Exception as e:
            return ActionStep(
                step_number=step_number,
                agent_name=agent_name,
                error=f"Agent execution failed: {str(e)}",
                is_final_answer=False
            )

    async def _provide_final_answer(self, task: str, images: Optional[List[Any]] = None) -> str:
        """
        Synthesize final legal plan from all expert analyses
        """
        # Collect all expert analyses
        expert_analyses = []
        for step in self.memory.get_action_history():
            if step.observation and step.agent_name:
                expert_analyses.append(f"**{step.agent_name}**:\n{step.observation}\n")

        if not expert_analyses:
            return "无法生成法律方案：缺少专家分析结果"

        # Generate synthesis prompt
        synthesis_prompt = self.prompt_templates.get("synthesis", {}).get(
            "final_answer",
            "请综合以下专家意见形成最终法律方案：\n\n{expert_analyses}"
        ).format(expert_analyses="\n".join(expert_analyses))

        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=self.system_prompt),
            ChatMessage(role=MessageRole.USER, content=synthesis_prompt)
        ]

        try:
            final_response = await self.model.generate(
                [{"role": msg.role.value, "content": msg.content} for msg in messages]
            )

            return final_response if isinstance(final_response, str) else final_response.get("content", "")

        except Exception as e:
            return f"综合分析失败：{str(e)}\n\n专家意见：\n" + "\n".join(expert_analyses)
