"""
Test script for the DMac learning system.

This script tests the enhanced learning system for DeepSeek-RL,
which allows it to learn from interactions with all models and improve over time.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from models.model_manager import ModelManager, ModelType
from models.learning_system import LearningSystem


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('test_learning_system')


async def test_learning_from_all_models():
    """Test learning from interactions with all models."""
    logger.info("Testing learning from all models")
    
    # Initialize the model manager
    model_manager = ModelManager()
    if not await model_manager.initialize():
        logger.error("Failed to initialize model manager")
        return False
    
    try:
        # Test prompts
        prompts = [
            "Explain the concept of reinforcement learning.",
            "What is the difference between supervised and unsupervised learning?",
            "How does a neural network work?",
            "What are the applications of AI in manufacturing?",
            "Explain the concept of transfer learning."
        ]
        
        # Generate responses with different models
        logger.info("Generating responses with different models")
        
        # Gemini
        logger.info("Testing with Gemini model")
        gemini_response = await model_manager.generate_text(prompts[0], ModelType.GEMINI)
        logger.info(f"Gemini response: {gemini_response[:100]}...")
        
        # DeepSeek
        logger.info("Testing with DeepSeek model")
        deepseek_response = await model_manager.generate_text(prompts[1], ModelType.DEEPSEEK)
        logger.info(f"DeepSeek response: {deepseek_response[:100]}...")
        
        # Local model
        logger.info("Testing with local model")
        local_response = await model_manager.generate_text(prompts[2], ModelType.LOCAL)
        logger.info(f"Local model response: {local_response[:100]}...")
        
        # Auto-selected model
        logger.info("Testing with auto-selected model")
        auto_response = await model_manager.generate_text(prompts[3])
        logger.info(f"Auto-selected model response: {auto_response[:100]}...")
        
        # Check if learning data was saved
        learning_system = model_manager.learning_system
        logger.info(f"Number of learning examples: {len(learning_system.learning_data)}")
        
        # The learning system should have saved examples from all models
        if len(learning_system.learning_data) >= 4:
            logger.info("Learning system successfully saved examples from all models")
        else:
            logger.warning("Learning system did not save examples from all models")
        
        logger.info("Learning from all models test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing learning from all models: {e}")
        return False
    finally:
        # Clean up
        await model_manager.cleanup()


async def test_feedback_system():
    """Test the feedback system."""
    logger.info("Testing feedback system")
    
    # Initialize the model manager
    model_manager = ModelManager()
    if not await model_manager.initialize():
        logger.error("Failed to initialize model manager")
        return False
    
    try:
        # Generate a response
        prompt = "What is the future of AI?"
        response = await model_manager.generate_text(prompt)
        
        # Provide feedback
        logger.info("Providing feedback")
        feedback = "The response was informative but could include more specific examples."
        rating = 4
        feedback_success = await model_manager.provide_feedback(prompt, response, feedback, rating)
        
        if feedback_success:
            logger.info("Feedback provided successfully")
        else:
            logger.warning("Failed to provide feedback")
        
        # Check if feedback was saved
        learning_system = model_manager.learning_system
        logger.info(f"Number of feedback examples: {len(learning_system.feedback_data)}")
        
        if len(learning_system.feedback_data) > 0:
            logger.info("Feedback system successfully saved feedback")
        else:
            logger.warning("Feedback system did not save feedback")
        
        logger.info("Feedback system test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing feedback system: {e}")
        return False
    finally:
        # Clean up
        await model_manager.cleanup()


async def test_training_process():
    """Test the training process."""
    logger.info("Testing training process")
    
    # Initialize the model manager
    model_manager = ModelManager()
    if not await model_manager.initialize():
        logger.error("Failed to initialize model manager")
        return False
    
    try:
        # Generate some responses to create learning data
        prompts = [
            "Explain the concept of reinforcement learning.",
            "What is the difference between supervised and unsupervised learning?",
            "How does a neural network work?",
            "What are the applications of AI in manufacturing?",
            "Explain the concept of transfer learning."
        ]
        
        logger.info("Generating responses to create learning data")
        for prompt in prompts:
            await model_manager.generate_text(prompt)
        
        # Train the model
        logger.info("Training the model")
        training_success = await model_manager.train_deepseek()
        
        if training_success:
            logger.info("Training completed successfully")
        else:
            logger.warning("Training failed")
        
        # Check if metrics were saved
        learning_system = model_manager.learning_system
        if learning_system.metrics['training_loss']:
            logger.info(f"Training metrics: {learning_system.metrics}")
        else:
            logger.warning("No training metrics were saved")
        
        logger.info("Training process test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing training process: {e}")
        return False
    finally:
        # Clean up
        await model_manager.cleanup()


async def test_model_evaluation():
    """Test the model evaluation."""
    logger.info("Testing model evaluation")
    
    # Initialize the learning system directly
    learning_system = LearningSystem()
    if not await learning_system.initialize():
        logger.error("Failed to initialize learning system")
        return False
    
    try:
        # Test prompts for evaluation
        test_prompts = [
            "What is the role of attention in transformer models?",
            "How can reinforcement learning be applied to robotics?",
            "Explain the concept of few-shot learning."
        ]
        
        # Evaluate the model
        logger.info("Evaluating the model")
        evaluation_results = await learning_system.evaluate_model(test_prompts)
        
        logger.info(f"Evaluation results: {evaluation_results}")
        
        if 'accuracy' in evaluation_results:
            logger.info("Model evaluation completed successfully")
        else:
            logger.warning("Model evaluation failed")
        
        logger.info("Model evaluation test completed")
        return True
    except Exception as e:
        logger.exception(f"Error testing model evaluation: {e}")
        return False
    finally:
        # Clean up
        await learning_system.cleanup()


async def main():
    """Main entry point for the test script."""
    logger.info("Starting learning system tests")
    
    # Test learning from all models
    learning_success = await test_learning_from_all_models()
    logger.info(f"Learning from all models test {'succeeded' if learning_success else 'failed'}")
    
    # Test feedback system
    feedback_success = await test_feedback_system()
    logger.info(f"Feedback system test {'succeeded' if feedback_success else 'failed'}")
    
    # Test training process
    training_success = await test_training_process()
    logger.info(f"Training process test {'succeeded' if training_success else 'failed'}")
    
    # Test model evaluation
    evaluation_success = await test_model_evaluation()
    logger.info(f"Model evaluation test {'succeeded' if evaluation_success else 'failed'}")
    
    # Overall result
    overall_success = (
        learning_success and
        feedback_success and
        training_success and
        evaluation_success
    )
    
    logger.info(f"Learning system tests {'succeeded' if overall_success else 'failed'}")


if __name__ == '__main__':
    asyncio.run(main())
