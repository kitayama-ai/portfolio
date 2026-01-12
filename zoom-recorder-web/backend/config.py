import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Slack
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#meeting-notes")
    
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Whisper API
    WHISPER_MODEL = "whisper-1"
    GPT_MODEL = "gpt-4o-mini"
    MAX_FILE_SIZE_MB = 25
    
    # デフォルトパス
    DEFAULT_RECORDING_FOLDER = str(Path.home() / "Documents" / "ZoomRecordings")
    DEFAULT_DOCUMENT_FOLDER = str(Path.home() / "Documents" / "MeetingNotes")
    CONFIG_DIR = Path.home() / ".zoom_recorder"
    CONFIG_FILE = CONFIG_DIR / "config.json"
