"""
Agent Memory Management System

Tracks conversation history, planning steps, and action execution for multi-agent orchestration.
Adapted from AgentOrchestra's memory system for legal domain.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role in conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """Chat message structure"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class SystemPromptStep(BaseModel):
    """System prompt step"""
    system_prompt: str

    def to_messages(self, summary_mode: bool = False) -> List[ChatMessage]:
        """Convert to chat messages"""
        if summary_mode:
            return []
        return [ChatMessage(role=MessageRole.SYSTEM, content=self.system_prompt)]


class TaskStep(BaseModel):
    """User task/query step"""
    task: str
    task_images: Optional[List[Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    def to_messages(self, summary_mode: bool = False) -> List[ChatMessage]:
        """Convert to chat messages"""
        return [ChatMessage(role=MessageRole.USER, content=self.task)]


class PlanningStep(BaseModel):
    """Planning agent output step"""
    step_number: Optional[int] = None
    plan: str
    selected_agents: List[str] = Field(default_factory=list)
    reasoning: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    token_usage: Optional[Dict[str, int]] = None

    def to_messages(self, summary_mode: bool = False) -> List[ChatMessage]:
        """Convert to chat messages"""
        if summary_mode:
            # In summary mode, only include the plan without full details
            return [ChatMessage(role=MessageRole.ASSISTANT, content=f"Plan: {self.plan[:200]}...")]
        return [ChatMessage(role=MessageRole.ASSISTANT, content=self.plan)]


class ActionStep(BaseModel):
    """Agent action execution step"""
    step_number: int
    agent_name: Optional[str] = None
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    error: Optional[str] = None
    is_final_answer: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    token_usage: Optional[Dict[str, int]] = None

    def to_messages(self, summary_mode: bool = False) -> List[ChatMessage]:
        """Convert to chat messages"""
        messages = []

        if self.action:
            action_text = f"Action: {self.action}"
            if self.action_input:
                action_text += f"\nInput: {self.action_input}"
            messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=action_text))

        if self.observation:
            obs_text = self.observation if not summary_mode else self.observation[:200] + "..."
            messages.append(ChatMessage(role=MessageRole.USER, content=f"Observation: {obs_text}"))

        if self.error:
            messages.append(ChatMessage(role=MessageRole.USER, content=f"Error: {self.error}"))

        return messages


class FinalAnswerStep(BaseModel):
    """Final answer step"""
    output: Any
    timestamp: datetime = Field(default_factory=datetime.now)

    def to_messages(self, summary_mode: bool = False) -> List[ChatMessage]:
        """Convert to chat messages"""
        return [ChatMessage(role=MessageRole.ASSISTANT, content=str(self.output))]


class AgentMemory:
    """
    Agent memory management system

    Stores conversation history including:
    - System prompts
    - User tasks
    - Planning steps
    - Action executions
    - Final answers
    """

    def __init__(self, system_prompt: Optional[str] = None, user_prompt: Optional[str] = None):
        self.system_prompt = SystemPromptStep(system_prompt=system_prompt or "")
        self.user_prompt = user_prompt
        self.steps: List[Any] = []

    def reset(self):
        """Reset memory, keeping only system prompt"""
        self.steps = []

    def add_task(self, task: str, images: Optional[List[Any]] = None):
        """Add a user task"""
        self.steps.append(TaskStep(task=task, task_images=images))

    def add_planning_step(self, plan: str, selected_agents: List[str] = None, reasoning: str = ""):
        """Add a planning step"""
        step_number = len([s for s in self.steps if isinstance(s, PlanningStep)]) + 1
        self.steps.append(PlanningStep(
            step_number=step_number,
            plan=plan,
            selected_agents=selected_agents or [],
            reasoning=reasoning
        ))

    def add_action_step(self, step_number: int, agent_name: str = None,
                       action: str = None, observation: str = None, error: str = None):
        """Add an action step"""
        self.steps.append(ActionStep(
            step_number=step_number,
            agent_name=agent_name,
            action=action,
            observation=observation,
            error=error
        ))

    def add_final_answer(self, output: Any):
        """Add final answer"""
        self.steps.append(FinalAnswerStep(output=output))

    def to_messages(self, summary_mode: bool = False) -> List[ChatMessage]:
        """
        Convert entire memory to chat messages

        Args:
            summary_mode: If True, condense history for context window management
        """
        messages = self.system_prompt.to_messages(summary_mode=summary_mode)

        for step in self.steps:
            messages.extend(step.to_messages(summary_mode=summary_mode))

        return messages

    def get_full_steps(self) -> List[Dict[str, Any]]:
        """Get all steps as dictionaries"""
        return [
            {
                "type": type(step).__name__,
                "data": step.model_dump()
            }
            for step in self.steps
        ]

    def get_planning_history(self) -> List[PlanningStep]:
        """Get all planning steps"""
        return [step for step in self.steps if isinstance(step, PlanningStep)]

    def get_action_history(self) -> List[ActionStep]:
        """Get all action steps"""
        return [step for step in self.steps if isinstance(step, ActionStep)]

    def __len__(self) -> int:
        """Return number of steps"""
        return len(self.steps)

    def __repr__(self) -> str:
        return f"AgentMemory(steps={len(self.steps)})"
