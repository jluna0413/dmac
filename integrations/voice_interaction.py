"""
Voice Interaction for DMac.

This module provides functionality for two-way voice interaction.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any

logger = logging.getLogger('dmac.integrations.voice_interaction')

class VoiceInteraction:
    """Client for voice interaction."""
    
    def __init__(self):
        """Initialize the voice interaction client."""
        self.initialized = False
        logger.info("Voice interaction client initialized")
    
    async def initialize(self) -> bool:
        """Initialize the client.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        try:
            # Check if required packages are installed
            try:
                import speech_recognition
                import pyttsx3
                self.initialized = True
                logger.info("Voice interaction dependencies found")
            except ImportError:
                logger.warning("Voice interaction dependencies not found. Install with: pip install SpeechRecognition pyttsx3 pyaudio")
                self.initialized = False
            
            return self.initialized
        except Exception as e:
            logger.exception(f"Error initializing voice interaction: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the client."""
        logger.info("Voice interaction cleaned up")
    
    async def speech_to_text(self, audio_file: Optional[str] = None, timeout: int = 5) -> Dict[str, Any]:
        """Convert speech to text.
        
        Args:
            audio_file: Path to an audio file to transcribe. If None, will listen from microphone.
            timeout: Timeout in seconds for listening (only used when audio_file is None).
            
        Returns:
            A dictionary containing the transcribed text and metadata.
        """
        if not self.initialized:
            success = await self.initialize()
            if not success:
                return {
                    'success': False,
                    'error': "Voice interaction not initialized",
                    'text': "",
                    'timestamp': time.time()
                }
        
        try:
            # Import here to avoid errors if dependencies aren't installed
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            if audio_file:
                # Transcribe from file
                logger.info(f"Transcribing audio file: {audio_file}")
                
                with sr.AudioFile(audio_file) as source:
                    audio_data = recognizer.record(source)
                    
                    # Use Google's speech recognition
                    text = recognizer.recognize_google(audio_data)
                    
                    logger.info(f"Transcribed text: {text}")
                    return {
                        'success': True,
                        'text': text,
                        'source': 'file',
                        'file_path': audio_file,
                        'timestamp': time.time()
                    }
            else:
                # Transcribe from microphone
                logger.info(f"Listening for speech (timeout: {timeout}s)")
                
                with sr.Microphone() as source:
                    # Adjust for ambient noise
                    recognizer.adjust_for_ambient_noise(source)
                    
                    # Listen for audio
                    audio_data = recognizer.listen(source, timeout=timeout)
                    
                    # Use Google's speech recognition
                    text = recognizer.recognize_google(audio_data)
                    
                    logger.info(f"Transcribed text: {text}")
                    return {
                        'success': True,
                        'text': text,
                        'source': 'microphone',
                        'timestamp': time.time()
                    }
        except ImportError as e:
            logger.warning(f"Speech recognition dependencies not installed: {e}")
            return {
                'success': False,
                'error': f"Speech recognition dependencies not installed: {e}",
                'text': "",
                'timestamp': time.time()
            }
        except Exception as e:
            logger.exception(f"Error in speech to text: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': "",
                'timestamp': time.time()
            }
    
    async def text_to_speech(self, text: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Convert text to speech.
        
        Args:
            text: The text to convert to speech.
            output_file: Path to save the audio file. If None, will play the audio.
            
        Returns:
            A dictionary containing metadata about the speech synthesis.
        """
        if not self.initialized:
            success = await self.initialize()
            if not success:
                return {
                    'success': False,
                    'error': "Voice interaction not initialized",
                    'timestamp': time.time()
                }
        
        try:
            # Import here to avoid errors if dependencies aren't installed
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Get available voices
            voices = engine.getProperty('voices')
            
            # Set properties
            engine.setProperty('rate', 150)  # Speed of speech
            
            # Use a female voice if available
            for voice in voices:
                if 'female' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            if output_file:
                # Save to file
                logger.info(f"Saving speech to file: {output_file}")
                engine.save_to_file(text, output_file)
                engine.runAndWait()
                
                return {
                    'success': True,
                    'text': text,
                    'output_file': output_file,
                    'timestamp': time.time()
                }
            else:
                # Play the audio
                logger.info(f"Speaking: {text}")
                engine.say(text)
                engine.runAndWait()
                
                return {
                    'success': True,
                    'text': text,
                    'timestamp': time.time()
                }
        except ImportError as e:
            logger.warning(f"Text to speech dependencies not installed: {e}")
            return {
                'success': False,
                'error': f"Text to speech dependencies not installed: {e}",
                'timestamp': time.time()
            }
        except Exception as e:
            logger.exception(f"Error in text to speech: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def voice_conversation(self, prompt: str, model: str) -> Dict[str, Any]:
        """Have a voice conversation with a model.
        
        Args:
            prompt: The initial prompt to start the conversation.
            model: The model to use for the conversation.
            
        Returns:
            A dictionary containing the conversation results.
        """
        if not self.initialized:
            success = await self.initialize()
            if not success:
                return {
                    'success': False,
                    'error': "Voice interaction not initialized",
                    'timestamp': time.time()
                }
        
        try:
            # Import here to avoid circular imports
            from integrations import ollama_client
            
            # Speak the prompt
            await self.text_to_speech(prompt)
            
            # Listen for a response
            speech_result = await self.speech_to_text()
            
            if not speech_result['success']:
                return speech_result
            
            user_input = speech_result['text']
            
            # Generate a response using the model
            response = await ollama_client.generate(model, user_input)
            
            if 'error' in response:
                return {
                    'success': False,
                    'error': response['error'],
                    'timestamp': time.time()
                }
            
            response_text = response.get('text', "I'm sorry, I couldn't generate a response.")
            
            # Speak the response
            await self.text_to_speech(response_text)
            
            return {
                'success': True,
                'user_input': user_input,
                'model_response': response_text,
                'model': model,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.exception(f"Error in voice conversation: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }


# Create a singleton instance
voice_interaction = VoiceInteraction()
