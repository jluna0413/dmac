"""
Voice interface for DMac using CoquiSST/py3SST.
"""

import asyncio
import logging
import os
import tempfile
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from config.config import config

logger = logging.getLogger('dmac.integrations.voice')


class VoiceEngine(Enum):
    """Enum representing the voice engine to use."""
    COQUI_STT = "CoquiSST"
    PY3_STT = "py3SST"


class VoiceInterface:
    """Voice interface for DMac using CoquiSST/py3SST."""
    
    def __init__(self, engine: Optional[VoiceEngine] = None):
        """Initialize the voice interface.
        
        Args:
            engine: The voice engine to use. If not provided, the engine from the configuration will be used.
        """
        self.engine_name = engine or VoiceEngine(config.get('integrations.voice.engine', 'CoquiSST'))
        self.enabled = config.get('integrations.voice.enabled', True)
        self.engine = None
        self.is_listening = False
        self.listen_thread = None
        self.callbacks = []
        self.logger = logging.getLogger('dmac.integrations.voice')
    
    async def initialize(self) -> bool:
        """Initialize the voice interface.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            self.logger.info("Voice interface is disabled in the configuration")
            return False
        
        self.logger.info(f"Initializing voice interface with engine: {self.engine_name.value}")
        
        try:
            if self.engine_name == VoiceEngine.COQUI_STT:
                await self._initialize_coqui_stt()
            elif self.engine_name == VoiceEngine.PY3_STT:
                await self._initialize_py3_stt()
            else:
                self.logger.error(f"Unknown voice engine: {self.engine_name}")
                return False
            
            self.logger.info("Voice interface initialized")
            return True
        except Exception as e:
            self.logger.exception(f"Error initializing voice interface: {e}")
            return False
    
    async def _initialize_coqui_stt(self) -> None:
        """Initialize the CoquiSST engine."""
        try:
            # Import CoquiSTT
            import stt
            
            # Load the model
            model_path = config.get('integrations.voice.coqui_model_path', '')
            if not model_path:
                self.logger.warning("CoquiSTT model path not specified, using default model")
                self.engine = stt.Model()
            else:
                self.logger.info(f"Loading CoquiSTT model from: {model_path}")
                self.engine = stt.Model(model_path)
            
            self.logger.info("CoquiSTT engine initialized")
        except ImportError:
            self.logger.error("CoquiSTT not installed. Please install it with: pip install coqui-stt")
            raise
        except Exception as e:
            self.logger.exception(f"Error initializing CoquiSTT: {e}")
            raise
    
    async def _initialize_py3_stt(self) -> None:
        """Initialize the py3SST engine."""
        try:
            # Import py3SST
            import speech_recognition as sr
            
            # Initialize the recognizer
            self.engine = sr.Recognizer()
            
            self.logger.info("py3SST engine initialized")
        except ImportError:
            self.logger.error("py3SST not installed. Please install it with: pip install py3stt")
            raise
        except Exception as e:
            self.logger.exception(f"Error initializing py3SST: {e}")
            raise
    
    async def start_listening(self, callback: Callable[[str], None]) -> bool:
        """Start listening for voice commands.
        
        Args:
            callback: Function to call when a voice command is recognized.
            
        Returns:
            True if listening was started successfully, False otherwise.
        """
        if not self.enabled:
            self.logger.warning("Voice interface is disabled")
            return False
        
        if not self.engine:
            self.logger.error("Voice engine not initialized")
            return False
        
        if self.is_listening:
            self.logger.warning("Already listening")
            return True
        
        self.callbacks.append(callback)
        
        # Start listening in a separate thread
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_thread)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        self.logger.info("Started listening for voice commands")
        return True
    
    async def stop_listening(self) -> None:
        """Stop listening for voice commands."""
        if not self.is_listening:
            return
        
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1.0)
            self.listen_thread = None
        
        self.logger.info("Stopped listening for voice commands")
    
    def _listen_thread(self) -> None:
        """Thread function for listening to voice commands."""
        if self.engine_name == VoiceEngine.COQUI_STT:
            self._listen_coqui_stt()
        elif self.engine_name == VoiceEngine.PY3_STT:
            self._listen_py3_stt()
    
    def _listen_coqui_stt(self) -> None:
        """Listen for voice commands using CoquiSTT."""
        import stt
        import numpy as np
        import pyaudio
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Open stream
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        
        # Create a streaming context
        context = self.engine.createStream()
        
        try:
            while self.is_listening:
                # Read audio data
                data = stream.read(1024, exception_on_overflow=False)
                
                # Convert to numpy array
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Feed data to the model
                context.feedAudioContent(audio_data)
                
                # Check if we have a result
                text = context.intermediateDecode()
                if text:
                    # Check if the text ends with a period or question mark
                    if text.endswith('.') or text.endswith('?') or text.endswith('!'):
                        # Get the final result
                        text = context.finishStream()
                        self.logger.info(f"Recognized: {text}")
                        
                        # Call the callbacks
                        for callback in self.callbacks:
                            try:
                                callback(text)
                            except Exception as e:
                                self.logger.exception(f"Error in voice callback: {e}")
                        
                        # Create a new streaming context
                        context = self.engine.createStream()
        finally:
            # Clean up
            stream.stop_stream()
            stream.close()
            audio.terminate()
    
    def _listen_py3_stt(self) -> None:
        """Listen for voice commands using py3SST."""
        import speech_recognition as sr
        
        # Create a microphone instance
        mic = sr.Microphone()
        
        try:
            with mic as source:
                # Adjust for ambient noise
                self.engine.adjust_for_ambient_noise(source)
                
                while self.is_listening:
                    try:
                        # Listen for audio
                        self.logger.debug("Listening...")
                        audio = self.engine.listen(source, timeout=5.0, phrase_time_limit=10.0)
                        
                        # Recognize speech
                        text = self.engine.recognize_google(audio)
                        self.logger.info(f"Recognized: {text}")
                        
                        # Call the callbacks
                        for callback in self.callbacks:
                            try:
                                callback(text)
                            except Exception as e:
                                self.logger.exception(f"Error in voice callback: {e}")
                    except sr.WaitTimeoutError:
                        # Timeout, continue listening
                        pass
                    except sr.UnknownValueError:
                        # Speech was unintelligible
                        self.logger.debug("Could not understand audio")
                    except Exception as e:
                        self.logger.exception(f"Error in speech recognition: {e}")
        except Exception as e:
            self.logger.exception(f"Error in py3SST listening thread: {e}")
    
    async def transcribe_audio_file(self, file_path: str) -> str:
        """Transcribe an audio file.
        
        Args:
            file_path: Path to the audio file.
            
        Returns:
            The transcribed text.
        """
        if not self.enabled:
            self.logger.warning("Voice interface is disabled")
            return ""
        
        if not self.engine:
            self.logger.error("Voice engine not initialized")
            return ""
        
        self.logger.info(f"Transcribing audio file: {file_path}")
        
        try:
            if self.engine_name == VoiceEngine.COQUI_STT:
                return await self._transcribe_coqui_stt(file_path)
            elif self.engine_name == VoiceEngine.PY3_STT:
                return await self._transcribe_py3_stt(file_path)
            else:
                self.logger.error(f"Unknown voice engine: {self.engine_name}")
                return ""
        except Exception as e:
            self.logger.exception(f"Error transcribing audio file: {e}")
            return ""
    
    async def _transcribe_coqui_stt(self, file_path: str) -> str:
        """Transcribe an audio file using CoquiSTT.
        
        Args:
            file_path: Path to the audio file.
            
        Returns:
            The transcribed text.
        """
        # This is a simplified implementation
        # In a real implementation, you would need to handle different audio formats
        # and possibly convert the audio to the format expected by CoquiSTT
        
        try:
            # Use the model to transcribe the audio file
            text = self.engine.stt(file_path)
            return text
        except Exception as e:
            self.logger.exception(f"Error transcribing with CoquiSTT: {e}")
            return ""
    
    async def _transcribe_py3_stt(self, file_path: str) -> str:
        """Transcribe an audio file using py3SST.
        
        Args:
            file_path: Path to the audio file.
            
        Returns:
            The transcribed text.
        """
        import speech_recognition as sr
        
        try:
            # Load the audio file
            with sr.AudioFile(file_path) as source:
                # Record the audio
                audio = self.engine.record(source)
                
                # Recognize speech
                text = self.engine.recognize_google(audio)
                return text
        except Exception as e:
            self.logger.exception(f"Error transcribing with py3SST: {e}")
            return ""
    
    async def cleanup(self) -> None:
        """Clean up resources used by the voice interface."""
        self.logger.info("Cleaning up voice interface")
        
        # Stop listening
        await self.stop_listening()
        
        # Clean up engine resources
        self.engine = None
        
        self.logger.info("Voice interface cleaned up")
