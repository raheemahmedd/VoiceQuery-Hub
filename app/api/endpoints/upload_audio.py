from ...services.speaker_verification_service import SpeakerVerfication
from fastapi import APIRouter,File, UploadFile , Depends
# from app.core.logger import logger
from ...services.ai.graph.graph_service import build_graph,AgentState
import os

from ...services.speech_service import SpeechService
import shutil
from fastapi import APIRouter

UPLOAD_DIR = "uploads"  # your specific location
os.makedirs(UPLOAD_DIR, exist_ok=True)  # create if not exists

router = APIRouter(prefix="/speech", tags=["Speech-to-Text"])
@router.post("/upload_audio")
async def speaker_verfication(file: UploadFile):
        # logger.info(f"📂 Received file: {file.filename} (Content-Type: {file.content_type})")

        speach_service = SpeechService(file.filename)
        speaker_verfication_service=SpeakerVerfication(speach_service)
    

        file_location = os.path.join(UPLOAD_DIR, file.filename)
        
        # Save file locally
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        app=build_graph(AgentState)
        initial_state = AgentState(audio_path = file_location, speaker_verfication_service=speaker_verfication_service,speach_service=speach_service)
        result=app.invoke(initial_state)
        
        
        if result['verified']:
            if len(result['query_type'])>1:
                print("Found more than question in one voice record! ") 
            return {"transcribed_text":result['transcribed_text'],"verification":{"verified":result['verified'],
            "speaker_name":result["speaker_verfication_service"].speaker_name if speaker_verfication_service else None,"speaker_role":result["speaker_verfication_service"].speaker_role if speaker_verfication_service else None,"similarity_score":int((result["speaker_verfication_service"].confidence_score)*100) if speaker_verfication_service else None,"user_id":result["user_id"],"final_response":result['tool_result'],"query_type":result['query_type']}}
        
        return {"transcribed_text":result['transcribed_text'],"verification":{"verified":result['verified'],
            "speaker_name":result["speaker_verfication_service"].speaker_name if speaker_verfication_service else None,"speaker_role":result["speaker_verfication_service"].speaker_role if speaker_verfication_service else None,"similarity_score":int((result["speaker_verfication_service"].confidence_score)*100) if speaker_verfication_service else None,"user_id":result["user_id"]}}
        


