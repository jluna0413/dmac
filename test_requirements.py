"""
Test script to verify that the system meets the requirements.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from config.config import config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('test_requirements')


def check_requirement(name, condition, message=None):
    """Check if a requirement is met.
    
    Args:
        name: The name of the requirement.
        condition: The condition to check.
        message: Optional message to display if the condition is not met.
    
    Returns:
        True if the requirement is met, False otherwise.
    """
    if condition:
        logger.info(f"✅ {name}: Requirement met")
        return True
    else:
        logger.error(f"❌ {name}: Requirement not met{' - ' + message if message else ''}")
        return False


async def check_requirements():
    """Check if the system meets the requirements."""
    logger.info("Checking system requirements")
    
    requirements_met = []
    
    # Check Python version
    python_version = sys.version_info
    requirements_met.append(
        check_requirement(
            "Python version",
            python_version.major >= 3 and python_version.minor >= 8,
            f"Python 3.8+ required, found {python_version.major}.{python_version.minor}"
        )
    )
    
    # Check required modules
    required_modules = [
        "asyncio",
        "logging",
        "json",
        "yaml",
        "aiohttp",
        "numpy",
        "httpx",
    ]
    
    for module_name in required_modules:
        try:
            __import__(module_name)
            requirements_met.append(check_requirement(f"Module {module_name}", True))
        except ImportError:
            requirements_met.append(check_requirement(f"Module {module_name}", False, f"Module {module_name} not found"))
    
    # Check required directories
    required_dirs = [
        "config",
        "core",
        "models",
        "agents",
        "integrations",
        "ui",
    ]
    
    for dir_name in required_dirs:
        requirements_met.append(
            check_requirement(
                f"Directory {dir_name}",
                Path(dir_name).exists() and Path(dir_name).is_dir(),
                f"Directory {dir_name} not found"
            )
        )
    
    # Check required files
    required_files = [
        "main.py",
        "config/config.py",
        "models/model_manager.py",
        "models/learning_system.py",
        "core/swarm/orchestrator.py",
        "core/swarm/agent.py",
        "core/openmanus_rl/integration.py",
    ]
    
    for file_name in required_files:
        requirements_met.append(
            check_requirement(
                f"File {file_name}",
                Path(file_name).exists() and Path(file_name).is_file(),
                f"File {file_name} not found"
            )
        )
    
    # Check configuration
    requirements_met.append(
        check_requirement(
            "Configuration",
            hasattr(config, "get") and callable(config.get),
            "Configuration object does not have a 'get' method"
        )
    )
    
    # Check model configuration
    requirements_met.append(
        check_requirement(
            "Model configuration",
            config.get("models.gemini") is not None,
            "Gemini model configuration not found"
        )
    )
    
    requirements_met.append(
        check_requirement(
            "DeepSeek configuration",
            config.get("models.deepseek") is not None,
            "DeepSeek model configuration not found"
        )
    )
    
    requirements_met.append(
        check_requirement(
            "Local model configuration",
            config.get("models.local") is not None,
            "Local model configuration not found"
        )
    )
    
    # Check UI configuration
    requirements_met.append(
        check_requirement(
            "UI configuration",
            config.get("ui") is not None,
            "UI configuration not found"
        )
    )
    
    # Check integration configuration
    requirements_met.append(
        check_requirement(
            "Integration configuration",
            config.get("integrations") is not None,
            "Integration configuration not found"
        )
    )
    
    # Calculate overall result
    total_requirements = len(requirements_met)
    met_requirements = sum(requirements_met)
    
    logger.info(f"Requirements check completed: {met_requirements}/{total_requirements} requirements met")
    
    return all(requirements_met)


async def main():
    """Main entry point for the test script."""
    logger.info("Starting requirements check")
    
    # Check requirements
    requirements_met = await check_requirements()
    
    if requirements_met:
        logger.info("✅ All requirements are met")
    else:
        logger.error("❌ Some requirements are not met")


if __name__ == '__main__':
    asyncio.run(main())
