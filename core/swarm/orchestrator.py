"""
Orchestrator for the DMac agent swarm.
"""

import asyncio
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Union

from config.config import config
from core.openmanus_rl.integration import OpenManusRLIntegration
from core.swarm.agent import BaseAgent, AgentState
from models.model_manager import ModelManager, ModelType
from integrations.integration_manager import IntegrationManager

logger = logging.getLogger('dmac.orchestrator')


class Task:
    """Represents a task to be executed by the agent swarm."""

    def __init__(self, prompt: str, task_id: Optional[str] = None):
        """Initialize a task.

        Args:
            prompt: The prompt that describes the task.
            task_id: Unique identifier for the task. If not provided, a UUID will be generated.
        """
        self.task_id = task_id or str(uuid.uuid4())
        self.prompt = prompt
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.status = "created"
        self.result = None
        self.steps = []
        self.agent_assignments = {}
        self.error = None

    def update_status(self, status: str) -> None:
        """Update the status of the task.

        Args:
            status: The new status.
        """
        self.status = status
        self.updated_at = time.time()

    def add_step(self, step: Dict[str, Any]) -> None:
        """Add a step to the task.

        Args:
            step: The step to add.
        """
        self.steps.append(step)
        self.updated_at = time.time()

    def assign_agent(self, agent_id: str, subtask: str) -> None:
        """Assign an agent to a subtask.

        Args:
            agent_id: The ID of the agent.
            subtask: The subtask to assign.
        """
        self.agent_assignments[subtask] = agent_id
        self.updated_at = time.time()

    def set_result(self, result: Any) -> None:
        """Set the result of the task.

        Args:
            result: The result of the task.
        """
        self.result = result
        self.updated_at = time.time()

    def set_error(self, error: str) -> None:
        """Set an error for the task.

        Args:
            error: The error message.
        """
        self.error = error
        self.status = "error"
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary.

        Returns:
            A dictionary representation of the task.
        """
        return {
            "task_id": self.task_id,
            "prompt": self.prompt,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "result": self.result,
            "steps": self.steps,
            "agent_assignments": self.agent_assignments,
            "error": self.error,
        }


class Orchestrator:
    """Orchestrator for the DMac agent swarm."""

    def __init__(self, openmanus_integration: OpenManusRLIntegration, model_manager: ModelManager = None, integration_manager: IntegrationManager = None):
        """Initialize the orchestrator.

        Args:
            openmanus_integration: Integration with OpenManus-RL.
            model_manager: Manager for AI models. If not provided, a new instance will be created.
            integration_manager: Manager for external tool integrations. If not provided, a new instance will be created.
        """
        self.openmanus_integration = openmanus_integration
        self.model_manager = model_manager or ModelManager()
        self.integration_manager = integration_manager or IntegrationManager()
        self.agents = {}
        self.tasks = {}
        self.logger = logging.getLogger('dmac.orchestrator')
        self.versioning = config.get('orchestration.versioning', True)
        self.max_agents = config.get('orchestration.max_agents', 10)

    async def initialize(self) -> bool:
        """Initialize the orchestrator.

        Returns:
            True if initialization was successful, False otherwise.
        """
        self.logger.info("Initializing orchestrator")

        # Initialize agents
        await self._initialize_agents()

        self.logger.info("Orchestrator initialized")
        return True

    async def _initialize_agents(self) -> None:
        """Initialize all agents."""
        # Import agent implementations
        from agents.coding.agent import CodingAgent
        from agents.manufacturing.agent import ManufacturingAgent
        from agents.design.agent import DesignAgent
        from agents.ui.agent import UIAgent
        from agents.iot.agent import IoTAgent

        # Create agent instances based on configuration
        agent_configs = {
            'coding': {'class': CodingAgent, 'enabled': config.get('agents.coding.enabled', True)},
            'manufacturing': {'class': ManufacturingAgent, 'enabled': config.get('agents.manufacturing.enabled', True)},
            'design': {'class': DesignAgent, 'enabled': config.get('agents.design.enabled', True)},
            'ui': {'class': UIAgent, 'enabled': config.get('agents.ui.enabled', True)},
            'iot': {'class': IoTAgent, 'enabled': config.get('agents.iot.enabled', False)},
        }

        # Initialize enabled agents
        for agent_name, agent_config in agent_configs.items():
            if agent_config['enabled']:
                try:
                    agent = agent_config['class']()
                    success = await agent.initialize()
                    if success:
                        self.agents[agent_name] = agent
                        self.logger.info(f"Initialized agent: {agent_name}")
                    else:
                        self.logger.error(f"Failed to initialize agent: {agent_name}")
                except Exception as e:
                    self.logger.exception(f"Error initializing agent {agent_name}: {e}")

    async def process(self, prompt: str, model_type: Optional[ModelType] = None) -> str:
        """Process a prompt using the agent swarm.

        Args:
            prompt: The prompt to process.
            model_type: The type of model to use. If not provided, the best available model will be used.

        Returns:
            The result of processing the prompt.
        """
        self.logger.info(f"Processing prompt: {prompt}")

        # Create a new task
        task = Task(prompt)
        self.tasks[task.task_id] = task
        task.update_status("planning")

        try:
            # Generate initial response using the model manager
            self.logger.info(f"Generating initial response for task {task.task_id}")
            initial_response = await self.model_manager.generate_text(prompt, model_type)
            task.add_step({"type": "initial_response", "content": initial_response})

            # Plan the task execution
            plan = await self._plan_task(task, initial_response)
            task.add_step({"type": "plan", "content": plan})

            # Execute the plan
            result = await self._execute_plan(task, plan)
            task.set_result(result)
            task.update_status("completed")

            # If we used Gemini, train DeepSeek-RL with the results
            if model_type == ModelType.GEMINI or (model_type is None and self.model_manager._should_use_gemini()):
                self.logger.info(f"Training DeepSeek-RL with results from task {task.task_id}")
                asyncio.create_task(self.model_manager.train_deepseek())

            return result
        except Exception as e:
            self.logger.exception(f"Error processing task {task.task_id}: {e}")
            task.set_error(str(e))
            return f"Error: {e}"

    async def _plan_task(self, task: Task, initial_response: Optional[str] = None) -> Dict[str, Any]:
        """Plan the execution of a task.

        Args:
            task: The task to plan.
            initial_response: Initial response from the model manager, if available.

        Returns:
            A plan for executing the task.
        """
        self.logger.info(f"Planning task {task.task_id}")

        # Use OpenManus-RL to create a plan, incorporating the initial response if available
        if initial_response:
            self.logger.info(f"Using initial response to help plan task {task.task_id}")
            plan = await self.openmanus_integration.create_plan(task.prompt, initial_response=initial_response)
        else:
            plan = await self.openmanus_integration.create_plan(task.prompt)

        # Assign agents to subtasks
        for subtask in plan.get('subtasks', []):
            agent_type = subtask.get('agent_type')
            if agent_type in self.agents:
                task.assign_agent(self.agents[agent_type].agent_id, subtask['id'])
            else:
                self.logger.warning(f"No agent available for type: {agent_type}")

        return plan

    async def _execute_plan(self, task: Task, plan: Dict[str, Any]) -> str:
        """Execute a plan for a task.

        Args:
            task: The task to execute.
            plan: The plan to execute.

        Returns:
            The result of executing the plan.
        """
        self.logger.info(f"Executing plan for task {task.task_id}")

        # Execute each subtask in the plan
        results = []
        for subtask in plan.get('subtasks', []):
            subtask_id = subtask['id']
            agent_id = task.agent_assignments.get(subtask_id)

            if agent_id:
                # Find the agent by ID
                agent = next((a for a in self.agents.values() if a.agent_id == agent_id), None)
                if agent:
                    # Execute the subtask
                    subtask_result = await agent.process(subtask)
                    results.append(subtask_result)
                    task.add_step({
                        "type": "subtask",
                        "subtask_id": subtask_id,
                        "agent_id": agent_id,
                        "result": subtask_result
                    })
                else:
                    self.logger.warning(f"Agent {agent_id} not found for subtask {subtask_id}")
            else:
                self.logger.warning(f"No agent assigned for subtask {subtask_id}")

        # Combine the results
        final_result = await self._combine_results(task, results)
        return final_result

    async def _combine_results(self, task: Task, results: List[Dict[str, Any]]) -> str:
        """Combine the results of multiple subtasks.

        Args:
            task: The task being executed.
            results: The results of the subtasks.

        Returns:
            The combined result.
        """
        self.logger.info(f"Combining results for task {task.task_id}")

        # Use OpenManus-RL to combine the results
        combined_result = await self.openmanus_integration.combine_results(task.prompt, results)
        return combined_result

    async def cleanup(self) -> None:
        """Clean up resources used by the orchestrator."""
        self.logger.info("Cleaning up orchestrator")

        # Clean up all agents
        for agent_name, agent in self.agents.items():
            try:
                await agent.cleanup()
                self.logger.info(f"Cleaned up agent: {agent_name}")
            except Exception as e:
                self.logger.exception(f"Error cleaning up agent {agent_name}: {e}")

        # Clean up the model manager
        if hasattr(self, 'model_manager') and self.model_manager:
            try:
                await self.model_manager.cleanup()
                self.logger.info("Cleaned up model manager")
            except Exception as e:
                self.logger.exception(f"Error cleaning up model manager: {e}")

        # Clean up the integration manager
        if hasattr(self, 'integration_manager') and self.integration_manager:
            try:
                await self.integration_manager.cleanup()
                self.logger.info("Cleaned up integration manager")
            except Exception as e:
                self.logger.exception(f"Error cleaning up integration manager: {e}")

        self.logger.info("Orchestrator cleaned up")
