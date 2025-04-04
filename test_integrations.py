"""
Test script for the DMac integrations.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from integrations.integration_manager import IntegrationManager
from integrations.voice.voice_interface import VoiceInterface
from integrations.cli.cli_interface import CLIInterface
from integrations.design.blender_interface import BlenderInterface
from integrations.design.ue5_interface import UE5Interface
from integrations.manufacturing.printing_interface import PrintingInterface
from integrations.manufacturing.cnc_interface import CNCInterface
from integrations.manufacturing.laser_interface import LaserInterface
from integrations.manufacturing.packaging_interface import PackagingInterface


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('test_integrations')


async def test_voice_interface(voice_interface: VoiceInterface):
    """Test the voice interface."""
    logger.info("Testing voice interface")
    
    # Test transcribing an audio file
    # In a real test, you would use an actual audio file
    # For now, we'll just log the method call
    logger.info("Testing audio transcription (simulated)")
    # result = await voice_interface.transcribe_audio_file("test.wav")
    # logger.info(f"Transcription result: {result}")
    
    logger.info("Voice interface test completed")


async def test_cli_interface(cli_interface: CLIInterface):
    """Test the CLI interface."""
    logger.info("Testing CLI interface")
    
    # Test executing a command
    logger.info("Testing command execution")
    result = await cli_interface.execute_command("echo Hello, DMac!")
    logger.info(f"Command execution result: {result}")
    
    logger.info("CLI interface test completed")


async def test_blender_interface(blender_interface: BlenderInterface):
    """Test the Blender interface."""
    logger.info("Testing Blender interface")
    
    # Test creating a 3D model
    # In a real test, you would create an actual 3D model
    # For now, we'll just log the method call
    logger.info("Testing 3D model creation (simulated)")
    # result = await blender_interface.create_3d_model(
    #     {"object_type": "cube", "size": 2.0, "name": "TestCube"},
    #     "test_cube.stl"
    # )
    # logger.info(f"3D model creation result: {result}")
    
    logger.info("Blender interface test completed")


async def test_ue5_interface(ue5_interface: UE5Interface):
    """Test the UE5 interface."""
    logger.info("Testing UE5 interface")
    
    # Test creating a Metahuman
    # In a real test, you would create an actual Metahuman
    # For now, we'll just log the method call
    logger.info("Testing Metahuman creation (simulated)")
    # result = await ue5_interface.create_metahuman(
    #     {"name": "TestHuman", "gender": "male", "age": 30},
    #     "test_metahuman"
    # )
    # logger.info(f"Metahuman creation result: {result}")
    
    logger.info("UE5 interface test completed")


async def test_printing_interface(printing_interface: PrintingInterface):
    """Test the 3D printing interface."""
    logger.info("Testing 3D printing interface")
    
    # Test getting printer status
    logger.info("Testing printer status")
    result = await printing_interface.get_printer_status()
    logger.info(f"Printer status: {result}")
    
    logger.info("3D printing interface test completed")


async def test_cnc_interface(cnc_interface: CNCInterface):
    """Test the CNC interface."""
    logger.info("Testing CNC interface")
    
    # Test getting CNC status
    logger.info("Testing CNC status")
    result = await cnc_interface.get_status()
    logger.info(f"CNC status: {result}")
    
    logger.info("CNC interface test completed")


async def test_laser_interface(laser_interface: LaserInterface):
    """Test the laser interface."""
    logger.info("Testing laser interface")
    
    # Test getting laser status
    logger.info("Testing laser status")
    result = await laser_interface.get_status()
    logger.info(f"Laser status: {result}")
    
    logger.info("Laser interface test completed")


async def test_packaging_interface(packaging_interface: PackagingInterface):
    """Test the packaging interface."""
    logger.info("Testing packaging interface")
    
    # Test getting Cricut status
    logger.info("Testing Cricut status")
    result = await packaging_interface.get_status()
    logger.info(f"Cricut status: {result}")
    
    logger.info("Packaging interface test completed")


async def main():
    """Main entry point for the test script."""
    logger.info("Initializing integration manager")
    integration_manager = IntegrationManager()
    
    try:
        # Initialize the integration manager
        if not await integration_manager.initialize():
            logger.warning("Some integrations failed to initialize")
        
        # Test voice interface
        await test_voice_interface(integration_manager.get_voice_interface())
        
        # Test CLI interface
        await test_cli_interface(integration_manager.get_cli_interface())
        
        # Test Blender interface
        await test_blender_interface(integration_manager.get_blender_interface())
        
        # Test UE5 interface
        await test_ue5_interface(integration_manager.get_ue5_interface())
        
        # Test 3D printing interface
        await test_printing_interface(integration_manager.get_printing_interface())
        
        # Test CNC interface
        await test_cnc_interface(integration_manager.get_cnc_interface())
        
        # Test laser interface
        await test_laser_interface(integration_manager.get_laser_interface())
        
        # Test packaging interface
        await test_packaging_interface(integration_manager.get_packaging_interface())
        
    except Exception as e:
        logger.exception(f"Error: {e}")
    finally:
        # Cleanup
        logger.info("Cleaning up")
        await integration_manager.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
