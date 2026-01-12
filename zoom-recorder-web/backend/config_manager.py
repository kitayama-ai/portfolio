import json
import os
from pathlib import Path
from typing import Optional, Dict
from config import Config

class ConfigManager:
    """設定管理クラス"""
    
    @staticmethod
    def load_config() -> Dict:
        """設定を読み込む"""
        Config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        default_config = {
            "recording_folder": Config.DEFAULT_RECORDING_FOLDER,
            "document_folder": Config.DEFAULT_DOCUMENT_FOLDER,
            "google_docs_enabled": False,
            "google_credentials": None,
            "default_mode": "recording_and_transcription"
        }
        
        if Config.CONFIG_FILE.exists():
            try:
                with open(Config.CONFIG_FILE, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    return {**default_config, **user_config}
            except:
                return default_config
        
        return default_config
    
    @staticmethod
    def save_config(config: Dict):
        """設定を保存"""
        Config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(Config.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def get_recording_folder(username: Optional[str] = None) -> Path:
        """録画フォルダを取得"""
        config = ConfigManager.load_config()
        folder = Path(config["recording_folder"])
        if username:
            folder = folder / username
        folder.mkdir(parents=True, exist_ok=True)
        return folder
    
    @staticmethod
    def get_document_folder(username: Optional[str] = None) -> Path:
        """ドキュメントフォルダを取得"""
        config = ConfigManager.load_config()
        folder = Path(config["document_folder"])
        if username:
            folder = folder / username
        folder.mkdir(parents=True, exist_ok=True)
        return folder
