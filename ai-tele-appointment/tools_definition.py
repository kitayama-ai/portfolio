# Vapiに登録するツールの定義
# functionNameは、main.pyのエンドポイントで判定に使用する名前

calendar_tool = {
    "type": "function",
    "function": {
        "name": "bookAppointment",
        "description": "お客様とのアポイントメントが確定した際に実行し、カレンダー予約とZoom/Meetリンクの発行を行う。",
        "parameters": {
            "type": "object",
            "properties": {
                "startTime": {
                    "type": "string",
                    "description": "予約開始日時。ISO 8601形式 (例: 2026-01-23T14:00:00+09:00)。必ず「明日」や「明後日」などの相対表現ではなく、具体的な日付に変換して渡すこと。"
                },
                "customerEmail": {
                    "type": "string",
                    "description": "お客様のメールアドレス（もし会話中で取得できていれば）。"
                }
            },
            "required": ["startTime"]
        }
    },
    # サーバーサイドで実行する設定
    "server": {
        "url": "https://YOUR_DOMAIN/api/vapi-webhook" # デプロイ時に書き換えが必要
    }
}

sms_tool = {
    "type": "function",
    "function": {
        "name": "sendSmsInfo",
        "description": "通話終了後や会話中に、資料やリンクをSMSで送信する。",
        "parameters": {
            "type": "object",
            "properties": {
                "phoneNumber": {
                    "type": "string",
                    "description": "送信先の電話番号。"
                },
                "content": {
                    "type": "string",
                    "description": "送信するメッセージの内容。"
                }
            },
            "required": ["phoneNumber", "content"]
        }
    }
}

ALL_TOOLS = [calendar_tool, sms_tool]
