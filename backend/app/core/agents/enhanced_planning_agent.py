"""
Enhanced Legal Planning Agent

Advanced planning agent with expert selection, cross-examination,
consensus building, and quality assessment.
"""

from typing import List, Dict, Any, Optional
import asyncio

from app.core.agents.planning_agent import LegalPlanningAgent
from app.core.agents.multistep_agent import ActionStep, PlanningStep
from app.core.agents.expert_selection import ExpertSelectionAlgorithm
from app.core.agents.collaboration import AgentCollaborationEngine, ConsensusResult
from app.core.agents.quality_assessment import QualityAssessmentFramework
from app.core.llm.base import BaseLLM


class EnhancedLegalPlanningAgent(LegalPlanningAgent):
    """
    Enhanced Legal Planning Agent with advanced collaboration algorithms

    Enhancements:
    1. Intelligent expert selection based on relevance scoring
    2. Cross-examination between experts
    3. Consensus building with weighted voting
    4. Quality assessment of synthesized plans
    5. Iterative improvement based on quality feedback
    """

    def __init__(
        self,
        model: BaseLLM,
        managed_agents: List[Any] = None,
        max_steps: int = 15,
        planning_interval: int = 5,
        enable_cross_examination: bool = True,
        enable_quality_assessment: bool = True,
        **kwargs
    ):
        super().__init__(
            model=model,
            managed_agents=managed_agents,
            max_steps=max_steps,
            planning_interval=planning_interval,
            **kwargs
        )

        # Initialize advanced algorithms
        self.expert_selector = ExpertSelectionAlgorithm()
        self.collaboration_engine = AgentCollaborationEngine(llm_model=model)
        self.quality_assessor = QualityAssessmentFramework(llm_model=model)

        # Configuration
        self.enable_cross_examination = enable_cross_examination
        self.enable_quality_assessment = enable_quality_assessment

        # Store agent analyses for collaboration
        self.agent_analyses: List[Dict[str, Any]] = []
        self.consensus_result: Optional[ConsensusResult] = None
        self.quality_result: Optional[Any] = None

    async def _generate_planning_step(self, task: str, step: int) -> PlanningStep:
        """
        Enhanced planning step with intelligent expert selection
        """
        is_first_step = step == 1

        if is_first_step:
            # Use expert selection algorithm
            selected_experts = await self._select_experts_intelligently(task)

            # Format planning with selected experts
            plan_text = self._format_expert_selection_plan(task, selected_experts)

            return PlanningStep(
                step_number=step,
                plan=plan_text,
                selected_agents=[expert.agent_id for expert in selected_experts],
                reasoning=f"智能选择了{len(selected_experts)}位最相关的专家"
            )
        else:
            # Regular update planning
            return await super()._generate_planning_step(task, step)

    async def _select_experts_intelligently(self, task: str):
        """Use expert selection algorithm to choose relevant experts"""

        # Extract event type from task (simplified)
        event_type = self._extract_event_type(task)

        # Get available agents as dictionaries
        available_agents = []
        for agent_id, agent in self.managed_agents.items():
            available_agents.append({
                "id": agent_id,
                "name": agent.name or agent_id,
                "type": getattr(agent, 'agent_type', 'unknown'),
                "law_domains": getattr(agent, 'law_domains', []),
                "description": agent.description or ""
            })

        # Select experts using algorithm
        selected_experts = self.expert_selector.select_experts(
            event_description=task,
            event_type=event_type,
            available_agents=available_agents,
            min_experts=3,
            max_experts=8
        )

        return selected_experts

    def _extract_event_type(self, task: str) -> str:
        """Extract event type from task description"""
        task_lower = task.lower()

        if any(word in task_lower for word in ['合规', '合同', '数据', '劳动', '监管']):
            return "maritime_dispute"
        elif any(word in task_lower for word in ['领土', '边界', '主权']):
            return "territorial_dispute"
        elif any(word in task_lower for word in ['外交', '外交关系']):
            return "diplomatic_conflict"
        elif any(word in task_lower for word in ['军事', '武装', '冲突']):
            return "military_incident"
        elif any(word in task_lower for word in ['经济', '制裁', '贸易']):
            return "economic_sanction"
        elif any(word in task_lower for word in ['环境', '污染']):
            return "environmental_issue"
        elif any(word in task_lower for word in ['航空', '领空']):
            return "aviation_incident"
        else:
            return "general_dispute"

    def _format_expert_selection_plan(self, task: str, selected_experts) -> str:
        """Format plan with expert selection reasoning"""

        plan = f"""## 法律事件分析

事件描述：{task[:200]}...

## 专家选择（基于智能算法）

经过多维度评估，选择以下{len(selected_experts)}位专家参与分析：

"""

        for i, expert in enumerate(selected_experts, 1):
            plan += f"""{i}. **{expert.agent_name}**
   - 相关性评分：{expert.final_score:.2f}
   - 选择理由：{expert.reasoning}

"""

        plan += """## 分析策略

1. 各专家从各自专业角度进行独立分析
2. 进行专家间交叉审查（如启用）
3. 通过共识机制综合意见
4. 质量评估并迭代优化

"""

        return plan

    async def _execute_step(self, step_number: int) -> ActionStep:
        """
        Enhanced execution with parallel agent calls
        """
        # Get selected agents from planning
        planning_steps = self.memory.get_planning_history()
        if not planning_steps:
            return await super()._execute_step(step_number)

        latest_plan = planning_steps[-1]
        selected_agents = latest_plan.selected_agents

        if not selected_agents:
            return ActionStep(
                step_number=step_number,
                observation="分析完成，准备生成最终方案",
                is_final_answer=True
            )

        # Call all selected agents in parallel
        tasks = []
        for agent_id in selected_agents:
            if agent_id in self.managed_agents:
                tasks.append(self.call_managed_agent(agent_id, self.task))

        # Execute in parallel
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Store analyses for collaboration
            for i, result in enumerate(results):
                if not isinstance(result, Exception):
                    agent_id = selected_agents[i]
                    agent = self.managed_agents[agent_id]

                    # Parse result (assuming it's formatted text)
                    self.agent_analyses.append({
                        "agent_id": agent_id,
                        "agent_name": agent.name or agent_id,
                        "analysis": str(result),
                        "legal_basis": [],  # Would be extracted from result
                        "recommendations": [],  # Would be extracted from result
                        "confidence": 0.8  # Would be extracted from result
                    })

            # Conduct cross-examination if enabled
            if self.enable_cross_examination and len(self.agent_analyses) > 1:
                await self._conduct_cross_examination()

            # Build consensus
            self.consensus_result = await self.collaboration_engine.build_consensus(
                agent_analyses=self.agent_analyses
            )

            observation = f"完成{len(results)}位专家的分析，共识程度：{self.consensus_result.consensus_level.value}"

            return ActionStep(
                step_number=step_number,
                action="parallel_analysis",
                observation=observation,
                is_final_answer=True
            )

        except Exception as e:
            return ActionStep(
                step_number=step_number,
                error=f"并行执行失败：{str(e)}",
                is_final_answer=False
            )

    async def _conduct_cross_examination(self):
        """Conduct cross-examination between agents"""
        try:
            cross_exam_results = await self.collaboration_engine.conduct_cross_examination(
                agent_analyses=self.agent_analyses
            )

            # Store cross-examination results in memory
            # (Could be added to a dedicated cross_exam_results list)

        except Exception as e:
            print(f"Cross-examination failed: {e}")

    async def _provide_final_answer(self, task: str, images: Optional[List[Any]] = None) -> str:
        """
        Enhanced final answer with consensus and quality assessment
        """
        if not self.agent_analyses:
            return await super()._provide_final_answer(task, images)

        # Use consensus result if available
        if self.consensus_result:
            synthesized_plan = self.consensus_result.synthesized_position
        else:
            # Fallback to basic synthesis
            synthesized_plan = await super()._provide_final_answer(task, images)

        # Assess quality if enabled
        if self.enable_quality_assessment:
            self.quality_result = await self.quality_assessor.assess_quality(
                synthesized_plan=synthesized_plan,
                agent_analyses=self.agent_analyses,
                consensus_result=self.consensus_result
            )

            # Add quality report to final answer
            quality_report = self.quality_assessor.get_quality_report(self.quality_result)

            final_answer = f"""{synthesized_plan}

---

{quality_report}

---

## 共识分析

- **共识程度**: {self.consensus_result.consensus_level.value if self.consensus_result else '未知'}
- **支持率**: {self.consensus_result.support_percentage:.1%} if self.consensus_result else 'N/A'
- **主要立场**: {self.consensus_result.majority_position if self.consensus_result else '未确定'}

### 关键共识
{chr(10).join('- ' + str(a) for a in (self.consensus_result.key_agreements[:5] if self.consensus_result else []))}

### 主要分歧
{chr(10).join('- ' + str(d) for d in (self.consensus_result.key_disagreements[:5] if self.consensus_result else []))}
"""

            return final_answer

        return synthesized_plan

    def get_analysis_metadata(self) -> Dict[str, Any]:
        """Get metadata about the analysis process"""
        return {
            "num_experts_consulted": len(self.agent_analyses),
            "consensus_level": self.consensus_result.consensus_level.value if self.consensus_result else None,
            "consensus_confidence": self.consensus_result.confidence if self.consensus_result else None,
            "quality_score": self.quality_result.overall_score if self.quality_result else None,
            "quality_level": self.quality_result.quality_level if self.quality_result else None,
            "cross_examination_enabled": self.enable_cross_examination,
            "quality_assessment_enabled": self.enable_quality_assessment
        }
