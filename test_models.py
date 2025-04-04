"""
Test script for the DMac model manager.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from models.model_manager import ModelManager, ModelType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('test_models')


async def main():
    """Main entry point for the test script."""
    logger.info("Initializing model manager")
    model_manager = ModelManager()
    
    try:
        # Initialize the model manager
        if not await model_manager.initialize():
            logger.error("Failed to initialize model manager")
            return
        
        # Test generating text with different models
        prompt = "Explain the concept of reinforcement learning in simple terms."
        
        # Test with Gemini
        logger.info("Testing Gemini model")
        gemini_response = await model_manager.generate_text(prompt, ModelType.GEMINI)
        logger.info(f"Gemini response: {gemini_response}")
        
        # Test with DeepSeek
        logger.info("Testing DeepSeek model")
        deepseek_response = await model_manager.generate_text(prompt, ModelType.DEEPSEEK)
        logger.info(f"DeepSeek response: {deepseek_response}")
        
        # Test with local model
        logger.info("Testing local model")
        local_response = await model_manager.generate_text(prompt, ModelType.LOCAL)
        logger.info(f"Local response: {local_response}")
        
        # Test automatic model selection
        logger.info("Testing automatic model selection")
        auto_response = await model_manager.generate_text(prompt)
        logger.info(f"Auto-selected model response: {auto_response}")
        
        # Test training DeepSeek
        logger.info("Testing DeepSeek training")
        training_success = await model_manager.train_deepseek()
        logger.info(f"DeepSeek training {'succeeded' if training_success else 'failed'}")
        
    except Exception as e:
        logger.exception(f"Error: {e}")
    finally:
        # Cleanup
        logger.info("Cleaning up")
        await model_manager.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
