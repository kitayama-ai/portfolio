from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
from pathlib import Path
import os
from typing import List, Dict, Optional
from config import Config

class CalendarService:
    """Googleカレンダーから予定を取得"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
    def __init__(self):
        self.credentials_path = Config.GOOGLE_CREDENTIALS_PATH
        self.token_path = Config.GOOGLE_TOKEN_PATH
        self.service = None
        self.calendar_email = Config.CALENDAR_EMAIL
    
    def authenticate(self) -> bool:
        """Google認証"""
        creds = None
        
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"認証情報ファイルが見つかりません: {self.credentials_path}")
                    return False
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        return True
    
    def get_today_events(self, calendar_id: Optional[str] = None) -> List[Dict]:
        """今日の予定を取得"""
        if not self.service:
            if not self.authenticate():
                return []
        
        # カレンダーIDを取得（メールアドレスが指定されている場合）
        if calendar_id is None:
            if self.calendar_email:
                calendar_id = self.calendar_email
            else:
                calendar_id = 'primary'
        
        # 今日の開始時刻と終了時刻
        today = datetime.now().date()
        time_min = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
        time_max = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'
        
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # 特定のアカウント（メールアドレス）で参加している予定のみをフィルタ
            if self.calendar_email:
                filtered_events = []
                for event in events:
                    attendees = event.get('attendees', [])
                    for attendee in attendees:
                        if attendee.get('email') == self.calendar_email:
                            filtered_events.append(event)
                            break
                return filtered_events
            
            return events
        
        except HttpError as error:
            print(f'カレンダー取得エラー: {error}')
            return []
