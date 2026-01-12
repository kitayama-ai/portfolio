from openai import OpenAI
from config import Config
from typing import Dict
import re
import json

class SatisfactionAnalyzer:
    """ユーザーの満足度を判定"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
    
    def is_question(self, message: str) -> bool:
        """メッセージが質問かどうかを判定"""
        # 感謝や挨拶などの非質問パターン
        non_question_patterns = [
            r"^(ありがとう|感謝|thx|thanks|thank you)",
            r"^(どうも|おつかれ|お疲れ)",
            r"^(こんにちは|こんばんは|おはよう|hello|hi)",
            r"^(了解|わかりました|ok|okay|OK)",
            r"^(はい|いいえ|yes|no)$",
        ]
        
        message_lower = message.lower().strip()
        for pattern in non_question_patterns:
            if re.match(pattern, message_lower, re.IGNORECASE):
                return False
        
        # 疑問詞や疑問符がある場合は質問
        question_indicators = ["?", "？", "か", "ですか", "でしょうか", "どう", "なぜ", "なに", "何", "what", "how", "why", "when", "where"]
        if any(indicator in message for indicator in question_indicators):
            return True
        
        # 短すぎるメッセージ（3文字以下）は質問ではない可能性が高い
        if len(message.strip()) <= 3:
            return False
        
        return True
    
    def analyze_satisfaction(self, user_message: str, bot_response: str, conversation_history: list = None) -> Dict:
        """満足度を分析"""
        if not self.client:
            # フォールバック: シンプルなルールベース判定
            return self._rule_based_analysis(user_message)
        
        # AI判定
        try:
            prompt = f"""ユーザーのメッセージとボットの回答を分析し、ユーザーの満足度を0.0（非常に不満）から1.0（非常に満足）のスコアで評価してください。

ユーザーのメッセージ: {user_message}
ボットの回答: {bot_response}

以下のパターンに注意してください：
- 「わかりません」「わからない」「理解できない」→ 不満（0.0-0.3）
- 「どういうこと？」「もう少し詳しく」→ やや不満（0.3-0.5）
- 「ありがとう」「助かりました」→ 満足（0.7-1.0）
- 同じ内容について再度質問している → 不満（0.0-0.4）
- 怒りや不満の表現がある → 不満（0.0-0.3）
- 次の質問に移っている → 満足（0.6-1.0）

JSON形式で返答してください：
{{
    "satisfaction_score": 0.0-1.0,
    "is_satisfied": true/false,
    "reason": "判定理由",
    "needs_human_review": true/false
}}
"""
            
            response = self.client.chat.completions.create(
                model=Config.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "あなたはユーザーの満足度を分析する専門家です。JSON形式で正確に返答してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # スコアが閾値以下なら不満
            is_satisfied = result.get("satisfaction_score", 0.5) > Config.SATISFACTION_THRESHOLD
            
            return {
                "satisfaction_score": float(result.get("satisfaction_score", 0.5)),
                "is_satisfied": is_satisfied,
                "reason": result.get("reason", ""),
                "needs_human_review": result.get("needs_human_review", not is_satisfied)
            }
        
        except Exception as e:
            print(f"満足度分析エラー: {e}")
            return self._rule_based_analysis(user_message)
    
    def _rule_based_analysis(self, user_message: str) -> Dict:
        """ルールベースの満足度分析（フォールバック）"""
        message_lower = user_message.lower()
        
        # 不満のパターン
        dissatisfaction_patterns = [
            "わかりません", "わからない", "理解できない", "意味不明",
            "どういうこと", "もう少し詳しく", "説明不足",
            "違う", "間違ってる", "違います", "違うよ",
            "怒", "イライラ", "不満", "ダメ", "使えない"
        ]
        
        # 満足のパターン
        satisfaction_patterns = [
            "ありがとう", "感謝", "助かりました", "理解できました",
            "わかりました", "なるほど", "参考になりました"
        ]
        
        for pattern in dissatisfaction_patterns:
            if pattern in message_lower:
                return {
                    "satisfaction_score": 0.2,
                    "is_satisfied": False,
                    "reason": f"不満の表現を検出: {pattern}",
                    "needs_human_review": True
                }
        
        for pattern in satisfaction_patterns:
            if pattern in message_lower:
                return {
                    "satisfaction_score": 0.8,
                    "is_satisfied": True,
                    "reason": f"満足の表現を検出: {pattern}",
                    "needs_human_review": False
                }
        
        # デフォルト: やや満足
        return {
            "satisfaction_score": 0.6,
            "is_satisfied": True,
            "reason": "特に問題なし",
            "needs_human_review": False
        }
    
    def check_same_question(self, current_message: str, conversation_history: list) -> bool:
        """同じ内容の質問かどうかを判定"""
        if not conversation_history or len(conversation_history) < 2:
            return False
        
        # 直近の2-3件の会話を確認
        recent_messages = conversation_history[-3:]
        
        for msg in recent_messages:
            if msg.get("role") == "user":
                # 簡易的な類似度チェック（キーワードの重複）
                current_words = set(current_message.lower().split())
                prev_words = set(msg.get("content", "").lower().split())
                
                # 共通単語が70%以上なら同じ質問の可能性
                if len(current_words) > 0 and len(prev_words) > 0:
                    overlap = len(current_words & prev_words) / max(len(current_words), len(prev_words))
                    if overlap > 0.7:
                        return True
        
        return False
