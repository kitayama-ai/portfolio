import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google Calendar
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
    CALENDAR_EMAIL = os.getenv("CALENDAR_EMAIL", "")  # チェックするカレンダーのメールアドレス
    
    # Asana
    ASANA_ACCESS_TOKEN = os.getenv("ASANA_ACCESS_TOKEN", "")
    ASANA_WORKSPACE_GID = os.getenv("ASANA_WORKSPACE_GID", "")
    
    # 設定ディレクトリ
    CONFIG_DIR = Path.home() / ".calendar_to_asana"
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
