import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # LINE Messaging API（コースごとに設定）
    # 環境変数は LINE_CHANNEL_ACCESS_TOKEN_{COURSE_ID} の形式で設定
    # 例: LINE_CHANNEL_ACCESS_TOKEN_course1=xxx
    # 例: LINE_CHANNEL_SECRET_course1=yyy
    
    # Slack
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#school-support")
    
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # OpenAI Models
    GPT_MODEL = "gpt-4o-mini"
    EMBEDDING_MODEL = "text-embedding-3-small"
    
    # Google Sheets
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")
    
    # デフォルトパス
    CONFIG_DIR = Path.home() / ".online_school_bot"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    PDF_STORAGE_DIR = CONFIG_DIR / "pdfs"
    VECTOR_STORAGE_DIR = CONFIG_DIR / "vectors"
    
    # 満足度判定の閾値
    SATISFACTION_THRESHOLD = 0.3  # 0.3以下で不満と判定
    
    @staticmethod
    def get_line_token(course_id: str) -> str:
        """コースIDからLINEチャネルアクセストークンを取得"""
        return os.getenv(f"LINE_CHANNEL_ACCESS_TOKEN_{course_id}", "")
    
    @staticmethod
    def get_line_secret(course_id: str) -> str:
        """コースIDからLINEチャネルシークレットを取得"""
        return os.getenv(f"LINE_CHANNEL_SECRET_{course_id}", "")
    
    # Chatwork API（コースごとに設定）
    # 環境変数は CHATWORK_API_TOKEN_{COURSE_ID} の形式で設定
    # 例: CHATWORK_API_TOKEN_course1=xxx
    
    @staticmethod
    def get_chatwork_token(course_id: str) -> str:
        """コースIDからChatwork APIトークンを取得"""
        return os.getenv(f"CHATWORK_API_TOKEN_{course_id}", "")
