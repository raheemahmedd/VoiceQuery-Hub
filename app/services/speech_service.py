
from google import genai
from dotenv import load_dotenv
import os
from google.genai.types import GenerateContentConfig
from ..schemas.speech_schema import SpeechRequest, SpeechResponse
from ..core.config import GEMINI_API_KEY

class SpeechService:
    def __init__(self,audio_file_name='demo'):
        self.api_key = GEMINI_API_KEY
       
        self.audio_path=r""
        self.audio_file_name=audio_file_name
    
    def transcribe(self,audio_path:SpeechRequest):
        self.audio_path=audio_path
        
        client = genai.Client(api_key=self.api_key)
        myfile = client.files.upload(file=audio_path)
        prompt = """
        Generate a transcript of the speech. in the same language of speaking , as you are llm for Voice-Enabled Agentic Predictive Maintenance with Biometric Alerts,
        the inputs speech for you will always about the state of machines (may be machine name or id mentioned), report of the work needed or a general question .  
"""
        response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, myfile],
        config=GenerateContentConfig(temperature=0)
        )
   

        return SpeechResponse(text=response.text)
    
    def set_audio_path(self,audio_path):
        self.audio_path=audio_path

    
if __name__ == "__main__":
    service = SpeechService("demo")
    transcript = service.transcribe("ai_assistant_project\\tests\\samples\\sample_voice_1.m4a")
    print("Transcript:", transcript)

