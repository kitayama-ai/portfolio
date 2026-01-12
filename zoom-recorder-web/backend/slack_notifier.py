from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config

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
