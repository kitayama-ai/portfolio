from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from config import Config
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json
import os

class SpreadsheetService:
    """Googleスプレッドシートへの記録"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        self.service = None
        self.spreadsheet_id = Config.GOOGLE_SPREADSHEET_ID
        self.credentials_path = Config.GOOGLE_CREDENTIALS_PATH
        try:
            self._authenticate()
        except Exception as e:
            print(f"Google Sheets認証エラー（後で設定可能）: {e}")
    
    def _authenticate(self):
        """Google認証"""
        creds = None
        token_path = "token.json"
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
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
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('sheets', 'v4', credentials=creds)
        return True
    
    def create_spreadsheet(self, course_id: str) -> Optional[str]:
        """新規スプレッドシートを作成"""
        if not self.service:
            return None
        
        try:
            spreadsheet = {
                'properties': {
                    'title': f'オンラインスクール質問記録_{course_id}_{datetime.now().strftime("%Y%m%d")}'
                },
                'sheets': [{
                    'properties': {
                        'title': '質問記録',
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 10
                        }
                    }
                }]
            }
            
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            
            # ヘッダー行を設定
            headers = [
                '日時', '質問者アカウント名', '質問内容', 'ボット回答', 
                '満足度スコア', '満足しているか', '人間レビュー必要', 
                '改善コメント（運営入力）', 'コースID', '会話ID'
            ]
            
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='質問記録!A1:J1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
            # フォーマット設定（ヘッダー行を太字に）
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {
                                'bold': True
                            },
                            'backgroundColor': {
                                'red': 0.9,
                                'green': 0.9,
                                'blue': 0.9
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            }]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            return spreadsheet_id
        
        except HttpError as error:
            print(f'スプレッドシート作成エラー: {error}')
            return None
    
    def append_record(self, course_id: str, user_id: str, user_message: str, 
                     bot_response: str, satisfaction: Dict, conversation_id: str) -> bool:
        """記録を追加"""
        if not self.service or not self.spreadsheet_id:
            # スプレッドシートIDが設定されていない場合は新規作成
            if not self.spreadsheet_id:
                self.spreadsheet_id = self.create_spreadsheet(course_id)
                if not self.spreadsheet_id:
                    return False
        
        try:
            values = [[
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                user_id,
                user_message,
                bot_response,
                satisfaction.get('satisfaction_score', 0),
                'はい' if satisfaction.get('is_satisfied', False) else 'いいえ',
                'はい' if satisfaction.get('needs_human_review', False) else 'いいえ',
                '',  # 改善コメント（運営が後から入力）
                course_id,
                conversation_id
            ]]
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='質問記録!A:J',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
        
        except HttpError as error:
            print(f'スプレッドシート記録エラー: {error}')
            return False
    
    def get_conversations(self, course_id: str = None, limit: int = 100) -> List[Dict]:
        """会話履歴を取得"""
        if not self.service or not self.spreadsheet_id:
            return []
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='質問記録!A2:J'  # ヘッダー行を除く
            ).execute()
            
            rows = result.get('values', [])
            conversations = []
            
            for row in rows[-limit:]:  # 最新のlimit件
                if len(row) >= 10:
                    if course_id and row[8] != course_id:
                        continue
                    
                    conversations.append({
                        'datetime': row[0] if len(row) > 0 else '',
                        'user_id': row[1] if len(row) > 1 else '',
                        'user_message': row[2] if len(row) > 2 else '',
                        'bot_response': row[3] if len(row) > 3 else '',
                        'satisfaction_score': float(row[4]) if len(row) > 4 and row[4] else 0,
                        'is_satisfied': row[5] == 'はい' if len(row) > 5 else False,
                        'needs_human_review': row[6] == 'はい' if len(row) > 6 else False,
                        'improvement_comment': row[7] if len(row) > 7 else '',
                        'course_id': row[8] if len(row) > 8 else '',
                        'conversation_id': row[9] if len(row) > 9 else ''
                    })
            
            return conversations
        
        except HttpError as error:
            print(f'会話履歴取得エラー: {error}')
            return []
