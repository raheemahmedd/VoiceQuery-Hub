# main.py
from fastapi import FastAPI
import logging
from app.api.endpoints.main_api import api_router
from .core import config


app = FastAPI(title="AI Assistant")

# Routers
app.include_router(api_router, prefix="/api/v1")
