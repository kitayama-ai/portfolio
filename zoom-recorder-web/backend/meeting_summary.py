from openai import OpenAI
from config import Config

class MeetingSummaryService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
        self.model = Config.GPT_MODEL
    
    def generate_summary(self, transcription_text, meeting_title=None):
        """文字起こしテキストから議事録を生成"""
        if not self.client:
            raise Exception("OpenAI APIキーが設定されていません")
        
        prompt = f"""以下の会議の文字起こしテキストから、以下の形式で議事録を作成してください。

【会議情報】
タイトル: {meeting_title or "未設定"}

【文字起こしテキスト】
{transcription_text}

【出力形式】
## 📋 会議サマリー
- 会議の目的と概要（2-3行）

## ✅ 決定事項
- 決定した内容を箇条書きで

## 📝 アクションアイテム
- [担当者名] [タスク内容] [期限]
（担当者名が不明な場合は「要確認」と記載）

## 💡 主要な議論ポイント
- 重要な議論内容を箇条書きで

## ⚠️ 課題・懸念事項
- 課題があれば記載

## 📅 次回会議
- 次回会議の予定があれば記載
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは優秀な議事録作成アシスタントです。文字起こしテキストから重要な情報を抽出し、構造化された議事録を作成します。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"議事録生成エラー: {str(e)}")
