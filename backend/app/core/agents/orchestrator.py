"""
Agent Orchestration Service

Service layer for creating and managing multi-agent orchestration.
"""

from typing import List, Dict, Any, Optional
import asyncio

from app.core.agents.enhanced_planning_agent import EnhancedLegalPlanningAgent
from app.core.agents.legal_expert_agent import LegalExpertAgent, create_legal_expert_from_template
from app.core.llm.factory import LLMFactory
from app.config import get_settings


class AgentOrchestrator:
    """
    Agent Orchestrator - manages multi-agent legal analysis

    Creates and coordinates planning agent and legal expert sub-agents.
    """

    def __init__(self, llm_provider: Optional[str] = None):
        settings = get_settings()
        self.llm_provider = llm_provider or settings.LLM_PROVIDER
        self.llm = LLMFactory.create(provider=self.llm_provider)

        self.planning_agent: Optional[LegalPlanningAgent] = None
        self.expert_agents: Dict[str, LegalExpertAgent] = {}

    def create_expert_agents(self, agent_templates: List[Dict[str, Any]]) -> List[LegalExpertAgent]:
        """
        Create legal expert agents from templates

        Args:
            agent_templates: List of agent template dictionaries

        Returns:
            List of LegalExpertAgent instances
        """
        experts = []

        for template in agent_templates:
            expert = create_legal_expert_from_template(template, self.llm)
            experts.append(expert)
            self.expert_agents[expert.agent_id] = expert

        return experts

    def create_planning_agent(
        self,
        expert_agents: List[LegalExpertAgent],
        max_steps: int = 15,
        planning_interval: int = 5,
        enable_cross_examination: bool = True,
        enable_quality_assessment: bool = True
    ) -> EnhancedLegalPlanningAgent:
        """
        Create enhanced planning agent with managed expert agents

        Args:
            expert_agents: List of expert agents to manage
            max_steps: Maximum steps for planning agent
            planning_interval: Interval for re-planning
            enable_cross_examination: Enable cross-examination between experts
            enable_quality_assessment: Enable quality assessment of final plan

        Returns:
            EnhancedLegalPlanningAgent instance
        """
        self.planning_agent = EnhancedLegalPlanningAgent(
            model=self.llm,
            managed_agents=expert_agents,
            max_steps=max_steps,
            planning_interval=planning_interval,
            enable_cross_examination=enable_cross_examination,
            enable_quality_assessment=enable_quality_assessment
        )

        return self.planning_agent

    async def orchestrate_analysis(
        self,
        event_description: str,
        agent_templates: List[Dict[str, Any]],
        max_steps: int = 15,
        planning_interval: int = 5,
        stream: bool = False
    ) -> Any:
        """
        Orchestrate legal analysis using planning agent and experts

        Args:
            event_description: Description of the legal event to analyze
            agent_templates: Available expert agent templates
            max_steps: Maximum steps for analysis
            planning_interval: Interval for re-planning
            stream: Whether to stream results

        Returns:
            Analysis result or async generator if streaming
        """
        # Create expert agents
        experts = self.create_expert_agents(agent_templates)

        # Create planning agent
        planning_agent = self.create_planning_agent(
            expert_agents=experts,
            max_steps=max_steps,
            planning_interval=planning_interval
        )

        # Run orchestrated analysis
        result = await planning_agent.run(
            task=event_description,
            stream=stream,
            reset=True,
            return_full_result=True
        )

        return result

    async def get_agent_by_id(self, agent_id: str) -> Optional[LegalExpertAgent]:
        """Get expert agent by ID"""
        return self.expert_agents.get(agent_id)

    def reset(self):
        """Reset orchestrator state"""
        self.planning_agent = None
        self.expert_agents = {}


# Global orchestrator instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
