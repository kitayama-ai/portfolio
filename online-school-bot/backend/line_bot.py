from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
from config import Config
from typing import Dict, Optional
import json

class LineBotService:
    """LINE Messaging API連携"""
    
    def __init__(self, course_id: str):
        self.course_id = course_id
        self.channel_access_token = Config.get_line_token(course_id)
        self.channel_secret = Config.get_line_secret(course_id)
        
        if not self.channel_access_token:
            raise ValueError(f"コース {course_id} のLINEチャネルアクセストークンが設定されていません")
        
        self.line_bot_api = LineBotApi(self.channel_access_token)
        self.handler = WebhookHandler(self.channel_secret)
    
    def verify_signature(self, body: str, signature: str) -> bool:
        """署名を検証"""
        try:
            self.handler.parser.parse(body, signature)
            return True
        except InvalidSignatureError:
            return False
    
    def handle_webhook(self, body: str, signature: str, callback):
        """Webhookを処理"""
        try:
            events = self.handler.parser.parse(body, signature)
            
            for event in events:
                if isinstance(event, FollowEvent):
                    # 友だち追加時
                    callback("follow", event)
                elif isinstance(event, MessageEvent):
                    if isinstance(event.message, TextMessage):
                        # テキストメッセージ
                        callback("message", event)
        except InvalidSignatureError:
            raise ValueError("署名検証に失敗しました")
    
    def send_message(self, user_id: str, message: str) -> bool:
        """メッセージを送信"""
        try:
            self.line_bot_api.push_message(
                user_id,
                TextSendMessage(text=message)
            )
            return True
        except LineBotApiError as e:
            print(f"LINE送信エラー: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """ユーザープロフィールを取得"""
        try:
            profile = self.line_bot_api.get_profile(user_id)
            return {
                "user_id": user_id,
                "display_name": profile.display_name,
                "picture_url": profile.picture_url
            }
        except LineBotApiError as e:
            print(f"プロフィール取得エラー: {e}")
            return None
