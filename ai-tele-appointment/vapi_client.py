import os
import requests
from typing import Optional, Dict, Any

class VapiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"  # 仮のURL、実際のエンドポイントを確認する必要あり
        
    def make_call(self, phone_number: str, customer_name: str, context: str = "") -> Dict[str, Any]:
        """
        Vapi APIを使用して電話をかける
        """
        if not self.api_key:
            print("Warning: VAPI_API_KEY is not set. Mocking call.")
            return {"status": "mock_success", "message": f"Calling {phone_number} (Mock)"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # VapiのAPI仕様に基づいてペイロードを構築
        # Note: これは想定されるスキーマです。実際のAPI仕様に合わせて調整が必要です。
        payload = {
            "phoneNumber": {
                "number": phone_number
            },
            "assistant": {
                "firstMessage": f"もしもし、{customer_name}さんですか？ 無料動画を請求していただきありがとうございます。",
                # アシスタントIDを指定するか、動的に設定を渡す
                # "assistantId": "your-assistant-id"
            },
            "customer": {
                "name": customer_name
            }
        }
        
        try:
            # 実際のエンドポイントは /call/phone など
            response = requests.post(f"{self.base_url}/call/phone", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling Vapi API: {e}")
            return {"status": "error", "message": str(e)}
