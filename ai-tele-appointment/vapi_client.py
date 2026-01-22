import os
import requests
from typing import Optional, Dict, Any

class VapiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"

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
                "language": "ja" # 言語設定（モデルによっては効かない場合もあるが明示）
            },
            "voice": {
                # 日本語対応の高品質な音声プロバイダーを選択（例: 11Labs, OpenAI, Azure）
                # ここでは汎用性の高いOpenAIのalloyを仮設定。実際は11LabsのMultilingual v2などが日本語には強い。
                "provider": "openai",
                "voiceId": "alloy",
                "speed": 1.1, # 少し早口の方が自然に聞こえる場合がある
            },
             "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "ja", # 日本語の書き起こし精度を最大化
                "smartFormat": True, # 句読点などを自動補完
            },
            # 自然な割り込みとフィラーの設定
            # 注: VapiのAPI仕様変更によりパラメータ名は変更される可能性があるため要確認
            "silenceTimeoutSeconds": 30, # 長めの無言許容
            "responseDelaySeconds": 0.4, # 即答しすぎず、少し間を置く（人間らしさ）
            "llmRequestDelaySeconds": 0.1,
            "numWordsToInterrupt": 1, # ユーザーが話し始めたら即座に止まる（感度高め）
            "backgroundSound": "office" # オフィスの環境音を入れて臨場感を出す（オプション）
        }

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
        1. 挨拶と本人確認（firstMessageで実施済みだが、相手の反応に応じて柔軟に）
        2. 動画を見たきっかけや、現在困っていることのヒアリング
           - 例：「今回、動画を請求されたということは、何か集客でお悩みでしたか？」
        3. 課題への共感
           - 例：「それは大変ですよね。実は他の方からも同じような相談をよく受けるんです。」
        4. 解決策の提示（Zoom相談への誘導）
           - 例：「その状況でしたら、動画を見るよりも一度直接お話しした方が、具体的な解決策をお伝えできると思います。明日か明後日、15分ほどお時間は取れませんか？」
        5. 日程調整と確定
           - 具体的な日時（◯日の◯時など）を聞き出し、確定させる。
        
        【禁止事項】
        - 押し売りをしてはいけません。相手が嫌がったら引いてください。
        - 嘘をついてはいけません。
        - ロボットのような機械的な口調にならないようにしてください。
        """
