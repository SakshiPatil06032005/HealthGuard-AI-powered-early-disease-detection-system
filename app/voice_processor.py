"""
Voice Processing Module for Speech-to-Text and Symptom Recognition
Handles audio input, language detection, and speech recognition
"""
import os
import io
import tempfile
from gtts import gTTS
from langdetect import detect, LangDetectException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceProcessor:
    """Handles speech-to-text conversion and language validation"""
    
    def __init__(self, use_google_cloud=False):
        """
        Initialize voice processor
        
        Args:
            use_google_cloud: If True, use Google Cloud Speech API (requires credentials)
                             If False, use speech_recognition library (free, works offline)
        """
        self.use_google_cloud = use_google_cloud
        self.google_client = None
        
        if use_google_cloud:
            try:
                from google.cloud import speech
                # Check if credentials are set
                if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                    self.google_client = speech.SpeechClient()
                    logger.info("✅ Google Cloud Speech API initialized")
                else:
                    logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS not set, falling back to speech_recognition")
                    self.use_google_cloud = False
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize Google Cloud Speech: {e}")
                self.use_google_cloud = False
        
        if not self.use_google_cloud:
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
                logger.info("✅ Speech Recognition (free) initialized")
            except ImportError:
                logger.error("⚠️ speech_recognition not installed. Voice input will not work.")
                logger.error("   Install with: pip install SpeechRecognition")
                self.recognizer = None
    
    def transcribe_audio_google_cloud(self, audio_bytes):
        """
        Transcribe audio using Google Cloud Speech-to-Text API
        
        Args:
            audio_bytes: Audio file content in bytes
            
        Returns:
            tuple: (transcript_text, language_code, confidence)
        """
        try:
            from google.cloud import speech
            
            # Configure audio and recognition settings
            audio = speech.RecognitionAudio(content=audio_bytes)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code="en-US",
                alternative_language_codes=["hi-IN", "mr-IN"],  # Hindi, Marathi
                enable_automatic_punctuation=True,
            )
            
            # Perform recognition
            response = self.google_client.recognize(config=config, audio=audio)
            
            if not response.results:
                return None, None, 0.0
            
            # Get the best result
            result = response.results[0]
            alternative = result.alternatives[0]
            
            transcript = alternative.transcript
            confidence = alternative.confidence
            language_code = result.language_code if hasattr(result, 'language_code') else 'en-US'
            
            logger.info(f"Transcription: {transcript} (confidence: {confidence})")
            
            return transcript, language_code, confidence
            
        except Exception as e:
            logger.error(f"Error in Google Cloud transcription: {e}")
            raise
    
    def transcribe_audio_free(self, audio_file_path):
        """
        Transcribe audio using free speech_recognition library (Google Speech Recognition API - free tier)
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            tuple: (transcript_text, language_code, confidence)
        """
        try:
            if not self.recognizer:
                raise Exception("Speech recognition not available. Please install SpeechRecognition package.")
            
            import speech_recognition as sr
            
            # Load audio file
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)
            
            # Try recognition with English
            try:
                transcript = self.recognizer.recognize_google(audio_data, language='en-US', show_all=False)
                logger.info(f"Transcription: {transcript}")
                return transcript, 'en-US', 0.9  # Approximate confidence
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return None, None, 0.0
            except sr.RequestError as e:
                logger.error(f"API request error: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Error in free transcription: {e}")
            raise
    
    def detect_language(self, text):
        """
        Detect the language of transcribed text
        
        Args:
            text: Transcribed text
            
        Returns:
            str: Language code ('en', 'hi', 'mr', etc.)
        """
        try:
            if not text or len(text.strip()) < 3:
                return 'unknown'
            
            lang_code = detect(text)
            logger.info(f"Detected language: {lang_code}")
            return lang_code
        except LangDetectException:
            logger.warning("Could not detect language")
            return 'unknown'
    
    def is_english(self, text):
        """
        Check if text is in English
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if English, False otherwise
        """
        try:
            lang = self.detect_language(text)
            return lang == 'en'
        except:
            return False
    
    def generate_voice_feedback(self, message, lang='en'):
        """
        Generate voice feedback using Google Text-to-Speech
        
        Args:
            message: Text message to convert to speech
            lang: Language code ('en', 'hi', etc.)
            
        Returns:
            bytes: Audio file content
        """
        try:
            tts = gTTS(text=message, lang=lang, slow=False)
            
            # Save to bytes buffer
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            logger.info(f"Generated voice feedback: {message[:50]}...")
            return fp.read()
            
        except Exception as e:
            logger.error(f"Error generating voice feedback: {e}")
            raise
    
    def process_audio_file(self, audio_file_path):
        """
        Process uploaded audio file: transcribe and validate language
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            dict: {
                'success': bool,
                'transcript': str,
                'language': str,
                'confidence': float,
                'error_message': str (if failed)
            }
        """
        wav_path = None
        try:
            logger.info(f"Processing audio file: {audio_file_path}")
            
            # Convert audio to WAV format for compatibility
            try:
                wav_path = self._convert_to_wav(audio_file_path)
                logger.info(f"Audio converted to: {wav_path}")
            except Exception as conv_error:
                error_msg = str(conv_error)
                logger.error(f"Audio conversion failed: {conv_error}")
                
                # Provide user-friendly error message
                if 'ffmpeg' in error_msg.lower():
                    user_message = (
                        "Audio conversion requires ffmpeg. "
                        "Please download and install ffmpeg from https://ffmpeg.org/download.html, "
                        "or contact your system administrator for assistance."
                    )
                else:
                    user_message = "Could not process audio file. Please try recording again or use a different browser."
                
                return {
                    'success': False,
                    'error_message': user_message,
                    'transcript': None,
                    'language': None,
                    'confidence': 0.0,
                    'technical_error': error_msg
                }
            
            # Transcribe
            if self.use_google_cloud:
                with open(wav_path, 'rb') as f:
                    audio_bytes = f.read()
                transcript, lang_code, confidence = self.transcribe_audio_google_cloud(audio_bytes)
            else:
                transcript, lang_code, confidence = self.transcribe_audio_free(wav_path)
            
            # Clean up temporary WAV file
            if wav_path and wav_path != audio_file_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                    logger.info(f"Cleaned up temporary file: {wav_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not clean up temp file: {cleanup_error}")
            
            if not transcript:
                return {
                    'success': False,
                    'error_message': 'No speech detected in audio. Please speak clearly and try again.',
                    'transcript': None,
                    'language': None,
                    'confidence': 0.0
                }
            
            # Detect language
            detected_lang = self.detect_language(transcript)
            logger.info(f"Detected language: {detected_lang}")
            
            # Check if English
            if detected_lang != 'en':
                return {
                    'success': False,
                    'error_message': 'Please speak in English',
                    'transcript': transcript,
                    'language': detected_lang,
                    'confidence': confidence,
                    'requires_english_prompt': True
                }
            
            return {
                'success': True,
                'transcript': transcript,
                'language': detected_lang,
                'confidence': confidence,
                'error_message': None
            }
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            
            # Clean up on error
            if wav_path and wav_path != audio_file_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except:
                    pass
            
            return {
                'success': False,
                'error_message': f'Error processing audio: {str(e)}',
                'transcript': None,
                'language': None,
                'confidence': 0.0
            }
    
    def _convert_to_wav(self, input_path):
        """
        Convert audio file to WAV format for compatibility
        
        Args:
            input_path: Path to input audio file
            
        Returns:
            str: Path to WAV file
        """
        try:
            # Check if already WAV
            if input_path.lower().endswith('.wav'):
                logger.info("Audio is already in WAV format")
                return input_path
            
            # Try to convert using pydub
            try:
                from pydub import AudioSegment
                import tempfile
                
                logger.info(f"Converting {input_path} to WAV format...")
                
                # Load audio - pydub can handle WebM with ffmpeg/avconv
                try:
                    audio = AudioSegment.from_file(input_path, format="webm")
                except Exception as load_error:
                    logger.warning(f"Could not load as WebM, trying generic load: {load_error}")
                    audio = AudioSegment.from_file(input_path)
                
                # Convert to mono and set sample rate for better compatibility
                audio = audio.set_channels(1)  # Mono
                audio = audio.set_frame_rate(16000)  # 16kHz sample rate
                audio = audio.set_sample_width(2)  # 16-bit
                
                # Create temporary WAV file
                wav_path = input_path.rsplit('.', 1)[0] + '_converted.wav'
                
                # Export as WAV with proper format
                audio.export(
                    wav_path,
                    format='wav',
                    parameters=["-ac", "1", "-ar", "16000"]  # Mono, 16kHz
                )
                
                logger.info(f"✅ Converted audio to WAV: {wav_path}")
                return wav_path
                
            except FileNotFoundError as fnf:
                logger.error("⚠️ ffmpeg/avconv not found for audio conversion")
                logger.error("   ffmpeg is required to convert WebM audio to WAV")
                logger.error("   Please install ffmpeg from: https://ffmpeg.org/download.html")
                logger.error("   Or record audio in WAV format directly")
                raise Exception("Audio conversion requires ffmpeg. Please install ffmpeg or use a different audio format.")
                
            except ImportError as ie:
                logger.error("⚠️ pydub not available for audio conversion")
                raise Exception("Audio conversion not available. Please install pydub.")
                
            except Exception as conv_error:
                logger.error(f"❌ Error converting audio with pydub: {conv_error}")
                # For now, return original path and let speech recognition try to handle it
                logger.warning("Attempting to use original file without conversion...")
                return input_path
                
        except Exception as e:
            logger.error(f"❌ Error in audio conversion: {e}")
            raise

# Global instance
voice_processor = VoiceProcessor(use_google_cloud=False)  # Use free version by default
