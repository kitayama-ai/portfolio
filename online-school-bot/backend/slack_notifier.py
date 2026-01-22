from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config
from typing import Optional, Dict

class SlackNotifier:
    def __init__(self):
        self.client = WebClient(token=Config.SLACK_BOT_TOKEN) if Config.SLACK_BOT_TOKEN else None
        self.channel = Config.SLACK_CHANNEL
    
    def send_meeting_summary(self, summary, meeting_title=None, transcription_text=None):
        """議事録をSlackに送信"""
        if not self.client:
            return  # Slack設定がない場合はスキップ
        
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📝 会議議事録: {meeting_title or '未設定'}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": summary
                    }
                }
            ]
            
            # 文字起こしテキストも添付（折りたたみ可能）
            if transcription_text:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```\n{transcription_text[:2000]}...\n```"
                    }
                })
            
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                text=f"会議議事録: {meeting_title or '未設定'}"
            )
            
            return response
        except SlackApiError as e:
            print(f"Slack送信エラー: {e.response['error']}")
            return None
    
    def notify_human_review_needed(self, course_id: str, user_id: str, user_name: str, 
                                   user_message: str, bot_response: str, 
                                   satisfaction: Dict, conversation_id: str, 
                                   course_manager_slack_id: Optional[str] = None):
        """二次回答が必要な場合にSlackで通知"""
        if not self.client:
            return None
        
        try:
            # コース担当者のメンション
            mention = f"<@{course_manager_slack_id}>" if course_manager_slack_id else f"@{course_id}コース担当者"
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚠️ 二次回答が必要です"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*コースID:*\n{course_id}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*ユーザー:*\n{user_name} ({user_id})"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*満足度スコア:*\n{satisfaction.get('satisfaction_score', 0):.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*会話ID:*\n{conversation_id}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*質問内容:*\n```{user_message}```"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*ボット回答:*\n```{bot_response}```"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*判定理由:*\n{satisfaction.get('reason', '')}"
                    }
                }
            ]
            
            text = f"{mention} 二次回答が必要です: {user_name}さんからの質問"
            
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                text=text
            )
            
            return response
        except SlackApiError as e:
            print(f"Slack通知エラー: {e.response['error']}")
            return None
