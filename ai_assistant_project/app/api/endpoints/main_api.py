from fastapi import APIRouter
from app.api.endpoints import upload_audio,add_user,delete_user


api_router = APIRouter()
 
api_router.include_router(upload_audio.router)  
api_router.include_router(add_user.router)  
api_router.include_router(delete_user.router)  
