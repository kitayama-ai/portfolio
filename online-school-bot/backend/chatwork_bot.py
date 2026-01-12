import requests
from config import Config
from typing import Dict, Optional
import json
import base64

class ChatworkBotService:
    """Chatwork API連携"""
    
    API_BASE_URL = "https://api.chatwork.com/v2"
    
    def __init__(self, course_id: str):
        self.course_id = course_id
        self.api_token = Config.get_chatwork_token(course_id)
        
        if not self.api_token:
            raise ValueError(f"コース {course_id} のChatwork APIトークンが設定されていません")
        
        self.headers = {
            "X-ChatWorkToken": self.api_token
        }
    
    def verify_webhook(self, body: str, signature: str = None) -> bool:
        """Webhook署名を検証（Chatworkは署名検証なし）"""
        # ChatworkのWebhookは署名検証がないため、常にTrueを返す
        # 必要に応じて、IPアドレス制限などでセキュリティを確保
        return True
    
    def handle_webhook(self, body: dict, callback):
        """Webhookを処理"""
        try:
            # ChatworkのWebhook形式を処理
            # bodyはJSON形式で、以下のような構造:
            # {
            #   "webhook_setting_id": "...",
            #   "webhook_event_type": "message_created",
            #   "webhook_event_time": 1234567890,
            #   "webhook_event": {
            #     "from_account_id": 12345,
            #     "to_account_id": 67890,
            #     "room_id": 123456,
            #     "message_id": "1234567890",
            #     "body": "メッセージ内容",
            #     "send_time": 1234567890,
            #     "update_time": 1234567890
            #   }
            # }
            
            event_type = body.get("webhook_event_type", "")
            webhook_event = body.get("webhook_event", {})
            
            if event_type == "message_created":
                # メッセージ作成イベント
                callback("message", webhook_event)
            elif event_type == "room_member_added":
                # ルームメンバー追加イベント（初回DM時など）
                callback("member_added", webhook_event)
            
        except Exception as e:
            print(f"Chatwork Webhook処理エラー: {e}")
            raise ValueError(f"Webhook処理に失敗しました: {e}")
    
    def send_message(self, room_id: int, message: str) -> bool:
        """メッセージを送信（DMまたはグループチャット）"""
        try:
            url = f"{self.API_BASE_URL}/rooms/{room_id}/messages"
            data = {
                "body": message
            }
            
            response = requests.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Chatwork送信エラー: {e}")
            return False
    
    def get_user_info(self, account_id: int) -> Optional[Dict]:
        """ユーザー情報を取得"""
        try:
            url = f"{self.API_BASE_URL}/users/{account_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            user_data = response.json()
            return {
                "user_id": str(account_id),
                "account_id": account_id,
                "name": user_data.get("name", ""),
                "chatwork_id": user_data.get("chatwork_id", ""),
                "organization_id": user_data.get("organization_id"),
                "organization_name": user_data.get("organization_name", ""),
                "department": user_data.get("department", ""),
                "avatar_image_url": user_data.get("avatar_image_url")
            }
        except requests.exceptions.RequestException as e:
            print(f"Chatworkユーザー情報取得エラー: {e}")
            return None
    
    def get_my_info(self) -> Optional[Dict]:
        """自分の情報を取得"""
        try:
            url = f"{self.API_BASE_URL}/me"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            user_data = response.json()
            return {
                "account_id": user_data.get("account_id"),
                "name": user_data.get("name", ""),
                "chatwork_id": user_data.get("chatwork_id", ""),
                "organization_id": user_data.get("organization_id"),
                "organization_name": user_data.get("organization_name", ""),
                "department": user_data.get("department", ""),
                "avatar_image_url": user_data.get("avatar_image_url")
            }
        except requests.exceptions.RequestException as e:
            print(f"Chatwork自分の情報取得エラー: {e}")
            return None
    
    def upload_file(self, room_id: int, file_path: str, message: str = "") -> Optional[str]:
        """ファイルをアップロード"""
        try:
            url = f"{self.API_BASE_URL}/rooms/{room_id}/files"
            
            with open(file_path, "rb") as f:
                files = {
                    "file": (file_path.split("/")[-1], f)
                }
                data = {
                    "message": message
                }
                
                response = requests.post(url, headers=self.headers, files=files, data=data)
                response.raise_for_status()
                
                result = response.json()
                return result.get("file_id")
        except Exception as e:
            print(f"Chatworkファイルアップロードエラー: {e}")
            return None
    
    def download_file(self, room_id: int, file_id: int) -> Optional[bytes]:
        """ファイルをダウンロード"""
        try:
            url = f"{self.API_BASE_URL}/rooms/{room_id}/files/{file_id}"
            params = {
                "create_download_url": True
            }
            
            # ダウンロードURLを取得
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            download_url = response.json().get("download_url")
            if not download_url:
                return None
            
            # ファイルをダウンロード
            file_response = requests.get(download_url)
            file_response.raise_for_status()
            
            return file_response.content
        except Exception as e:
            print(f"Chatworkファイルダウンロードエラー: {e}")
            return None
