# App settings
from dotenv import load_dotenv
import os

# Load .env once at startup
load_dotenv(r"E:\projects-in-army\1\Voice-Enabled Agentic Predictive Maintenance with Biometric Alerts\ai_assistant_project\.env",override=True)  

# Read variables
GEMINI_API_KEY = os.getenv("google_api_key")
host=os.getenv("host")

## database credentials
database=os.getenv("database")
user=os.getenv("user")
password=os.getenv("password")
port=os.getenv("port")
