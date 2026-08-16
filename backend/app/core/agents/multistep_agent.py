"""
Base Multi-Step Agent

Core agent class that executes tasks step-by-step using the ReAct framework.
Adapted from AgentOrchestra for legal domain analysis.
"""

from typing import List, Dict, Any, Optional, AsyncGenerator, Callable
from abc import ABC, abstractmethod
from datetime import datetime
import asyncio
import uuid

from app.core.agents.memory import (
    AgentMemory,
    PlanningStep,
    ActionStep,
    FinalAnswerStep,
    ChatMessage,
    MessageRole
)
from app.core.llm.base import BaseLLM


class AgentError(Exception):
    """Base exception for agent errors"""
    pass


class AgentMaxStepsError(AgentError):
    """Raised when agent reaches maximum steps"""
    pass


class AgentParsingError(AgentError):
    """Raised when agent fails to parse LLM output"""
    pass


class RunResult:
    """Result of an agent run"""

    def __init__(
        self,
        output: Any,
        state: str,  # "success" or "max_steps_error"
        messages: List[Dict],
        token_usage: Optional[Dict[str, int]] = None,
        timing: Optional[Dict[str, Any]] = None
    ):
        self.output = output
        self.state = state
        self.messages = messages
        self.token_usage = token_usage
        self.timing = timing or {}


class MultiStepAgent(ABC):
    """
    Base multi-step agent that solves tasks step by step

    Uses ReAct framework: agent performs cycles of action and observation
    until the objective is reached.

    Args:
        tools: List of tools the agent can use
        model: LLM model for generating actions
        max_steps: Maximum number of steps before stopping
        planning_interval: Interval for re-planning (None = no planning)
        name: Agent name (required for managed agents)
        description: Agent description (required for managed agents)
    """

    def __init__(
        self,
        tools: List[Any] = None,
        model: BaseLLM = None,
        max_steps: int = 20,
        planning_interval: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        provide_run_summary: bool = False,
        return_full_result: bool = False,
    ):
        self.agent_name = self.__class__.__name__
        self.model = model
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.max_steps = max_steps
        self.planning_interval = planning_interval
        self.name = name
        self.description = description
        self.provide_run_summary = provide_run_summary
        self.return_full_result = return_full_result

        self.step_number = 0
        self.task: Optional[str] = None
        self.state: Dict[str, Any] = {}

        # Initialize memory
        self.memory = AgentMemory(system_prompt=self.system_prompt)

        # Managed agents (sub-agents this agent can call)
        self.managed_agents: Dict[str, 'MultiStepAgent'] = {}

    @property
    def system_prompt(self) -> str:
        """Get system prompt - must be implemented by subclasses"""
        return self.initialize_system_prompt()

    @abstractmethod
    def initialize_system_prompt(self) -> str:
        """Initialize system prompt - implement in subclasses"""
        raise NotImplementedError("Subclasses must implement initialize_system_prompt()")

    async def run(
        self,
        task: str,
        stream: bool = False,
        reset: bool = True,
        images: Optional[List[Any]] = None,
        additional_args: Optional[Dict] = None,
        max_steps: Optional[int] = None,
    ):
        """
        Run the agent for the given task

        Args:
            task: Task to perform
            stream: Whether to stream results
            reset: Whether to reset memory
            images: Optional images
            additional_args: Additional arguments
            max_steps: Override default max_steps

        Returns:
            Final answer or RunResult if return_full_result=True
        """
        max_steps = max_steps or self.max_steps
        self.task = task

        if additional_args:
            self.state.update(additional_args)

        if reset:
            self.memory.reset()

        # Add task to memory
        self.memory.add_task(task, images)

        if stream:
            return self._run_stream(task=task, max_steps=max_steps, images=images)

        # Non-streaming execution
        run_start_time = datetime.now()
        steps = []

        async for step in self._run_stream(task=task, max_steps=max_steps, images=images):
            steps.append(step)

        # Get final answer
        final_step = steps[-1] if steps else None
        output = final_step.output if isinstance(final_step, FinalAnswerStep) else None

        if self.return_full_result:
            # Calculate token usage
            total_input_tokens = 0
            total_output_tokens = 0

            for step in self.memory.steps:
                if isinstance(step, (ActionStep, PlanningStep)) and step.token_usage:
                    total_input_tokens += step.token_usage.get("input_tokens", 0)
                    total_output_tokens += step.token_usage.get("output_tokens", 0)

            token_usage = {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens
            } if total_input_tokens > 0 else None

            state = "max_steps_error" if self.step_number > max_steps else "success"

            return RunResult(
                output=output,
                state=state,
                messages=self.memory.get_full_steps(),
                token_usage=token_usage,
                timing={
                    "start_time": run_start_time,
                    "end_time": datetime.now()
                }
            )

        return output

    async def _run_stream(
        self,
        task: str,
        max_steps: int,
        images: Optional[List[Any]] = None
    ) -> AsyncGenerator[Any, None]:
        """
        Stream execution of agent steps

        Yields planning steps, action steps, and final answer
        """
        self.step_number = 1
        returned_final_answer = False

        while not returned_final_answer and self.step_number <= max_steps:
            # Run planning step if scheduled
            if self.planning_interval and (
                self.step_number == 1 or (self.step_number - 1) % self.planning_interval == 0
            ):
                planning_step = await self._generate_planning_step(task, self.step_number)
                self.memory.steps.append(planning_step)
                yield planning_step

            # Execute action step
            action_step = await self._execute_step(self.step_number)
            self.memory.steps.append(action_step)
            yield action_step

            if action_step.is_final_answer:
                returned_final_answer = True
                final_answer = action_step.observation

            self.step_number += 1

        # Handle max steps reached
        if not returned_final_answer:
            final_answer = await self._provide_final_answer(task, images)
            action_step = ActionStep(
                step_number=self.step_number,
                error="Reached maximum steps",
                observation=final_answer
            )
            self.memory.steps.append(action_step)
            yield action_step

        # Yield final answer
        final_step = FinalAnswerStep(output=final_answer)
        yield final_step

    async def _generate_planning_step(self, task: str, step: int) -> PlanningStep:
        """
        Generate a planning step

        Override in subclasses to implement custom planning logic
        """
        # Default: simple planning
        plan = f"Analyzing task: {task}"

        return PlanningStep(
            step_number=step,
            plan=plan,
            selected_agents=[],
            reasoning="Default planning step"
        )

    async def _execute_step(self, step_number: int) -> ActionStep:
        """
        Execute one action step

        Override in subclasses to implement custom execution logic
        """
        # Default: simple execution
        return ActionStep(
            step_number=step_number,
            action="analyze",
            observation="Analysis complete",
            is_final_answer=True
        )

    async def _provide_final_answer(self, task: str, images: Optional[List[Any]] = None) -> str:
        """
        Provide final answer when max steps reached

        Override in subclasses for custom final answer generation
        """
        return "Task completed (max steps reached)"

    def add_managed_agent(self, agent: 'MultiStepAgent'):
        """Add a managed sub-agent"""
        if not agent.name:
            raise ValueError("Managed agent must have a name")
        self.managed_agents[agent.name] = agent

    async def call_managed_agent(self, agent_name: str, task: str, **kwargs) -> Any:
        """Call a managed sub-agent"""
        if agent_name not in self.managed_agents:
            raise ValueError(f"Unknown managed agent: {agent_name}")

        agent = self.managed_agents[agent_name]
        result = await agent.run(task=task, reset=True, **kwargs)

        return result

    def __repr__(self) -> str:
        return f"{self.agent_name}(name={self.name}, steps={self.step_number})"
