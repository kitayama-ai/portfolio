import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import Dict, Any, Optional

class GoogleCalendarService:
    def __init__(self):
        self.creds = None
        # 環境変数からサービスアカウントキーのパスを取得
        service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")
        
        scopes = ['https://www.googleapis.com/auth/calendar']
        
        if os.path.exists(service_account_path):
            try:
                self.creds = service_account.Credentials.from_service_account_file(
                    service_account_path, scopes=scopes
                )
                self.service = build('calendar', 'v3', credentials=self.creds)
            except Exception as e:
                print(f"Error initializing Google Calendar: {e}")
                self.service = None
        else:
            print("Warning: Google Service Account file not found. Calendar operations will be mocked.")
            self.service = None
            
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

    def create_event(self, start_time_iso: str, duration_minutes: int = 45, attendee_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Googleカレンダーに予定を作成し、Meetリンクを発行する
        """
        if not self.service:
            print(f"[Mock] Creating event at {start_time_iso} for {attendee_email}")
            return {
                "status": "success",
                "htmlLink": "https://calendar.google.com/mock",
                "hangoutLink": "https://meet.google.com/mock-meet-id"
            }

        try:
            # ISO形式の文字列をdatetimeオブジェクトに変換（必要に応じて）
            # ここではAPIがISO文字列をそのまま受け入れるため、タイムゾーン処理などに注意
            
            start_dt = datetime.datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
            end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
            
            event_body = {
                'summary': '【Zoom/Meet無料相談】AIアポ自動予約',
                'description': 'AIアポイントメントシステムによる自動予約です。',
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"req-{int(datetime.datetime.now().timestamp())}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                },
            }
            
            if attendee_email:
                event_body['attendees'] = [{'email': attendee_email}]

            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_body,
                conferenceDataVersion=1
            ).execute()

            return {
                "status": "success",
                "htmlLink": event.get('htmlLink'),
                "hangoutLink": event.get('hangoutLink')
            }

        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return {"status": "error", "message": str(e)}

    def check_availability(self, start_time_iso: str) -> bool:
        """
        指定された時間の空き状況を確認する（簡易版）
        """
        # 実装簡略化のため、常に空いていると仮定するか、freebusyクエリを実装する
        # ここではモック
        return True
