"""
Test script for the DMac core system.

This script tests the core components of the DMac system:
- Orchestrator
- Agent coordination
- Model switching
- Task processing
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from config.config import config
from core.swarm.orchestrator import Orchestrator
from core.openmanus_rl.integration import OpenManusRLIntegration
from models.model_manager import ModelManager, ModelType
from integrations.integration_manager import IntegrationManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('test_core_system')


async def test_model_switching():
    """Test the model switching functionality."""
    logger.info("Testing model switching")
    
    # Initialize the model manager
    model_manager = ModelManager()
    if not await model_manager.initialize():
        logger.error("Failed to initialize model manager")
        return False
    
    try:
        # Test generating text with different models
        prompt = "Explain the concept of agent swarms in AI."
        
        # Test with automatic model selection (should use Gemini if available)
        logger.info("Testing automatic model selection")
        auto_response = await model_manager.generate_text(prompt)
        logger.info(f"Auto-selected model response: {auto_response[:100]}...")
        
        # Test with explicit Gemini model
        logger.info("Testing Gemini model")
        gemini_response = await model_manager.generate_text(prompt, ModelType.GEMINI)
        logger.info(f"Gemini response: {gemini_response[:100]}...")
        
        # Test with explicit local model
        logger.info("Testing local model")
        local_response = await model_manager.generate_text(prompt, ModelType.LOCAL)
        logger.info(f"Local model response: {local_response[:100]}...")
        
        # Test with explicit DeepSeek model
        logger.info("Testing DeepSeek model")
        deepseek_response = await model_manager.generate_text(prompt, ModelType.DEEPSEEK)
        logger.info(f"DeepSeek response: {deepseek_response[:100]}...")
        
        # Simulate reaching the usage cap
        logger.info("Simulating reaching Gemini usage cap")
        model_manager.gemini_usage['daily_requests'] = model_manager.gemini_usage_cap
        
        # Test automatic model selection again (should use local model now)
        logger.info("Testing automatic model selection after reaching cap")
        cap_response = await model_manager.generate_text(prompt)
        logger.info(f"Auto-selected model after cap response: {cap_response[:100]}...")
        
        # Reset the usage counter
        model_manager.gemini_usage['daily_requests'] = 0
        
        logger.info("Model switching test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing model switching: {e}")
        return False
    finally:
        # Clean up
        await model_manager.cleanup()


async def test_orchestrator():
    """Test the orchestrator functionality."""
    logger.info("Testing orchestrator")
    
    # Initialize the components
    model_manager = ModelManager()
    if not await model_manager.initialize():
        logger.error("Failed to initialize model manager")
        return False
    
    integration_manager = IntegrationManager()
    if not await integration_manager.initialize():
        logger.warning("Some integrations failed to initialize")
    
    openmanus_integration = OpenManusRLIntegration()
    await openmanus_integration.initialize()
    
    # Initialize the orchestrator
    orchestrator = Orchestrator(openmanus_integration, model_manager, integration_manager)
    await orchestrator.initialize()
    
    try:
        # Test processing a simple prompt
        logger.info("Testing prompt processing")
        prompt = "Generate a simple Python function to calculate the factorial of a number."
        result = await orchestrator.process(prompt)
        logger.info(f"Prompt processing result: {result[:100]}...")
        
        # Test processing a more complex prompt
        logger.info("Testing complex prompt processing")
        complex_prompt = "Design a 3D model of a simple gear and prepare it for 3D printing."
        complex_result = await orchestrator.process(complex_prompt)
        logger.info(f"Complex prompt processing result: {complex_result[:100]}...")
        
        logger.info("Orchestrator test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing orchestrator: {e}")
        return False
    finally:
        # Clean up
        await orchestrator.cleanup()
        await openmanus_integration.cleanup()
        await integration_manager.cleanup()
        await model_manager.cleanup()


async def test_agent_coordination():
    """Test the agent coordination functionality."""
    logger.info("Testing agent coordination")
    
    # Initialize the components
    model_manager = ModelManager()
    if not await model_manager.initialize():
        logger.error("Failed to initialize model manager")
        return False
    
    integration_manager = IntegrationManager()
    if not await integration_manager.initialize():
        logger.warning("Some integrations failed to initialize")
    
    openmanus_integration = OpenManusRLIntegration()
    await openmanus_integration.initialize()
    
    # Initialize the orchestrator
    orchestrator = Orchestrator(openmanus_integration, model_manager, integration_manager)
    await orchestrator.initialize()
    
    try:
        # Test a prompt that requires multiple agents
        logger.info("Testing multi-agent coordination")
        prompt = "Create a simple website design and generate the HTML/CSS code for it."
        result = await orchestrator.process(prompt)
        logger.info(f"Multi-agent coordination result: {result[:100]}...")
        
        # Check the tasks and agent assignments
        tasks = orchestrator.tasks
        logger.info(f"Number of tasks: {len(tasks)}")
        
        for task_id, task in tasks.items():
            logger.info(f"Task ID: {task_id}")
            logger.info(f"Task prompt: {task.prompt}")
            logger.info(f"Task status: {task.status}")
            logger.info(f"Agent assignments: {task.agent_assignments}")
        
        logger.info("Agent coordination test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing agent coordination: {e}")
        return False
    finally:
        # Clean up
        await orchestrator.cleanup()
        await openmanus_integration.cleanup()
        await integration_manager.cleanup()
        await model_manager.cleanup()


async def test_learning_mechanism():
    """Test the learning mechanism."""
    logger.info("Testing learning mechanism")
    
    # Initialize the model manager
    model_manager = ModelManager()
    if not await model_manager.initialize():
        logger.error("Failed to initialize model manager")
        return False
    
    try:
        # Generate some responses with Gemini to create learning data
        prompts = [
            "Explain the concept of reinforcement learning.",
            "What is the difference between supervised and unsupervised learning?",
            "How does a neural network work?",
            "What are the applications of AI in manufacturing?",
            "Explain the concept of transfer learning."
        ]
        
        logger.info("Generating responses with Gemini to create learning data")
        for prompt in prompts:
            response = await model_manager.generate_text(prompt, ModelType.GEMINI)
            logger.info(f"Generated response for prompt: {prompt[:30]}...")
        
        # Train DeepSeek-RL with the learning data
        logger.info("Training DeepSeek-RL with the learning data")
        training_success = await model_manager.train_deepseek()
        logger.info(f"DeepSeek-RL training {'succeeded' if training_success else 'failed'}")
        
        # Test generating text with DeepSeek-RL after training
        logger.info("Testing DeepSeek-RL after training")
        test_prompt = "What is the future of AI?"
        deepseek_response = await model_manager.generate_text(test_prompt, ModelType.DEEPSEEK)
        logger.info(f"DeepSeek-RL response after training: {deepseek_response[:100]}...")
        
        logger.info("Learning mechanism test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing learning mechanism: {e}")
        return False
    finally:
        # Clean up
        await model_manager.cleanup()


async def main():
    """Main entry point for the test script."""
    logger.info("Starting core system tests")
    
    # Test model switching
    model_switching_success = await test_model_switching()
    logger.info(f"Model switching test {'succeeded' if model_switching_success else 'failed'}")
    
    # Test orchestrator
    orchestrator_success = await test_orchestrator()
    logger.info(f"Orchestrator test {'succeeded' if orchestrator_success else 'failed'}")
    
    # Test agent coordination
    agent_coordination_success = await test_agent_coordination()
    logger.info(f"Agent coordination test {'succeeded' if agent_coordination_success else 'failed'}")
    
    # Test learning mechanism
    learning_mechanism_success = await test_learning_mechanism()
    logger.info(f"Learning mechanism test {'succeeded' if learning_mechanism_success else 'failed'}")
    
    # Overall result
    overall_success = (
        model_switching_success and
        orchestrator_success and
        agent_coordination_success and
        learning_mechanism_success
    )
    
    logger.info(f"Core system tests {'succeeded' if overall_success else 'failed'}")


if __name__ == '__main__':
    asyncio.run(main())
