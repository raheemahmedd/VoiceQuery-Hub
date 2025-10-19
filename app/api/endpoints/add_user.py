from ...services.speaker_verification_service import SpeakerVerfication
from fastapi import APIRouter,File, UploadFile , Depends

from ...db.users import add_user as user_add
import os

from ...services.speech_service import SpeechService

import shutil

UPLOAD_DIR = r"ai_assistant_project\uploads\add_user_uploads"  # your specific location
os.makedirs(UPLOAD_DIR, exist_ok=True)  # create if not exists

router = APIRouter(prefix="/users", tags=["user-to-db"])
@router.post("/add_user")
async def add_user(file: UploadFile,name:str,role:str):
     try:   
        # logger.info(f"📂 Received file: {file.filename} (Content-Type: {file.content_type})")

        speach_service=SpeechService(file.filename)

        file_location = os.path.join(UPLOAD_DIR, file.filename)
        # Save file locally
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # logger.debug(f"File saved at: {file_location}")

        
        speaker_verfication_service=SpeakerVerfication(speach_service)
        
        speach_service.set_audio_path(file_location)
      
        speaker_verfication_service.audio_resample()
 
        emb=speaker_verfication_service.audio_embedding(speaker_verfication_service.fixed_path)
        user_add(embedding=emb,name=name,role=role)
        return f"user named {name} added to db successfully!"
     except Exception as e:
            print(f"An unexpected error occurred: {e}")

     


