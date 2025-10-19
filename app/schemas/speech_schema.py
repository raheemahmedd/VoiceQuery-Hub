from pydantic import BaseModel

class SpeechRequest(BaseModel):
    audio_path: str  
    
class SpeechResponse(BaseModel):
    text: str
