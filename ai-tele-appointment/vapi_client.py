import os
import requests
from typing import Optional, Dict, Any
from tools_definition import ALL_TOOLS

class VapiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"

    def make_call(self, phone_number: str, customer_name: str, server_url: Optional[str] = None) -> Dict[str, Any]:
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

        # 日本語での自然な会話を実現するためのアシスタント設定
        assistant_config = {
            "firstMessage": f"もしもし、{customer_name}さんでしょうか？ 無料動画をご覧いただきありがとうございます。",
            "model": {
                "provider": "openai",
                "model": "gpt-4-turbo",  # または gpt-4o。高速で賢いモデルを選択
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_system_prompt(customer_name)
                    }
                ],
                "language": "ja", # 言語設定
                "tools": ALL_TOOLS # 定義したツールを追加
            },
            "voice": {
                # 日本語対応の高品質な音声プロバイダーを選択
                "provider": "openai",
                "voiceId": "alloy",
                "speed": 1.1, 
            },
             "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "ja", 
                "smartFormat": True, 
            },
            "silenceTimeoutSeconds": 30, 
            "responseDelaySeconds": 0.4, 
            "llmRequestDelaySeconds": 0.1,
            "numWordsToInterrupt": 1, 
            "backgroundSound": "office" 
        }

        # サーバーURL（Webhook用）が指定されていれば設定
        if server_url:
            assistant_config["serverUrl"] = server_url

        payload = {
            "phoneNumber": {
                "number": phone_number
            },
            "assistant": assistant_config,
            "customer": {
                "name": customer_name
            }
        }

        try:
            response = requests.post(f"{self.base_url}/call/phone", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error calling Vapi API: {e}")
            return {"status": "error", "message": str(e)}

    def _get_system_prompt(self, customer_name: str) -> str:
        """
        AIアポインターの振る舞いを定義するシステムプロンプト
        """
        return f"""
        あなたはプロのアポイントメントセッターです。
        相手の名前は「{customer_name}」さんです。
        
        【目的】
        相手が現在抱えている課題をヒアリングし、解決策としてZoom無料相談（専門家との通話）のアポイントメントを確定させること。

        【話し方のルール】
        - 自然な日本語で話してください。
        - 敬語は崩しすぎず、しかし親しみやすい「丁寧語（です・ます）」を使ってください。
        - 相槌を打ってください（「なるほど」「ええ」「そうですよね」など）。
        - 相手が話しているときは絶対に遮らず、最後まで聞いてください。
        - 一度に長く話しすぎないでください。会話のキャッチボールを意識してください。
        
        【会話の流れ】
        1. 挨拶と本人確認
        2. 動画を見たきっかけや、現在困っていることのヒアリング
        3. 課題への共感
        4. 解決策の提示（Zoom相談への誘導）
        5. 日程調整と確定
           - 具体的な日時（例: 2026-01-23T14:00:00+09:00 のような形式）を確定させたら、必ず `bookAppointment` ツールを呼び出してください。
           - ツール呼び出しが成功したら、「ありがとうございます。今、詳細とMeetリンクをSMSで送りましたので、確認してください」と伝えてください。
           - もし相手が資料を欲しがったり、会話終了時にリンクを送る必要がある場合は `sendSmsInfo` ツールを使ってください。
        
        【禁止事項】
        - 押し売りをしてはいけません。相手が嫌がったら引いてください。
        - 嘘をついてはいけません。
        - ロボットのような機械的な口調にならないようにしてください。
        - カレンダー予約やSMS送信は、必ず提供されているツール（function）を使用してください。自分で「送りました」と嘘をつかないでください。
        """
