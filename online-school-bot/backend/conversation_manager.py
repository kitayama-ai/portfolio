from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
from config import Config

class ConversationManager:
    """会話履歴の管理"""
    
    def __init__(self):
        self.conversations_dir = Config.CONFIG_DIR / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
    
    def get_conversation_file(self, conversation_id: str) -> Path:
        """会話ファイルのパスを取得"""
        return self.conversations_dir / f"{conversation_id}.json"
    
    def create_conversation(self, user_id: str, course_id: str) -> str:
        """新しい会話を作成"""
        conversation_id = f"{course_id}_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        conversation = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "course_id": course_id,
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.save_conversation(conversation)
        return conversation_id
    
    def save_conversation(self, conversation: Dict):
        """会話を保存"""
        conversation["updated_at"] = datetime.now().isoformat()
        conversation_file = self.get_conversation_file(conversation["conversation_id"])
        with open(conversation_file, "w", encoding="utf-8") as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)
    
    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """会話を読み込み"""
        conversation_file = self.get_conversation_file(conversation_id)
        if conversation_file.exists():
            try:
                with open(conversation_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def get_or_create_conversation(self, user_id: str, course_id: str) -> str:
        """会話を取得または作成"""
        # 最新の会話を検索
        conversation_files = sorted(
            self.conversations_dir.glob(f"{course_id}_{user_id}_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if conversation_files:
            # 最新の会話を読み込み
            latest_file = conversation_files[0]
            conversation = json.loads(latest_file.read_text(encoding="utf-8"))
            
            # 24時間以内なら同じ会話を使用
            from datetime import timedelta
            updated_at = datetime.fromisoformat(conversation.get("updated_at", ""))
            if datetime.now() - updated_at < timedelta(hours=24):
                return conversation["conversation_id"]
        
        # 新しい会話を作成
        return self.create_conversation(user_id, course_id)
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """メッセージを追加"""
        conversation = self.load_conversation(conversation_id)
        if not conversation:
            return
        
        conversation["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        self.save_conversation(conversation)
    
    def get_conversation_history(self, conversation_id: str, limit: int = 20) -> List[Dict]:
        """会話履歴を取得"""
        conversation = self.load_conversation(conversation_id)
        if not conversation:
            return []
        
        messages = conversation.get("messages", [])
        return messages[-limit:] if len(messages) > limit else messages
