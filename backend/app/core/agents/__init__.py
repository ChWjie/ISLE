"""
Multi-Agent Orchestration Framework

Core components for hierarchical multi-agent coordination in legal analysis.
"""

from app.core.agents.memory import (
    AgentMemory,
    ChatMessage,
    MessageRole,
    SystemPromptStep,
    TaskStep,
    PlanningStep,
    ActionStep,
    FinalAnswerStep
)

from app.core.agents.multistep_agent import (
    MultiStepAgent,
    RunResult,
    AgentError,
    AgentMaxStepsError,
    AgentParsingError
)

__all__ = [
    # Memory
    "AgentMemory",
    "ChatMessage",
    "MessageRole",
    "SystemPromptStep",
    "TaskStep",
    "PlanningStep",
    "ActionStep",
    "FinalAnswerStep",

    # Agents
    "MultiStepAgent",
    "RunResult",

    # Exceptions
    "AgentError",
    "AgentMaxStepsError",
    "AgentParsingError",
]
