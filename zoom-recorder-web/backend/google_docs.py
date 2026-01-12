from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from pathlib import Path
import os
from typing import Optional

class GoogleDocsService:
    """Googleドキュメントへの自動アップロード"""
    
    SCOPES = ['https://www.googleapis.com/auth/documents',
              'https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or "credentials.json"
        self.service = None
        self.drive_service = None
    
    def authenticate(self):
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
                    return False
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('docs', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)
        return True
    
    def create_document(self, title: str, content: str, folder_id: Optional[str] = None) -> Optional[str]:
        """Googleドキュメントを作成"""
        try:
            if not self.service:
                if not self.authenticate():
                    return None
            
            # ドキュメントを作成
            document = self.service.documents().create(
                body={'title': title}
            ).execute()
            
            document_id = document.get('documentId')
            
            # コンテンツを挿入
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }]
            
            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            # フォルダに移動（指定されている場合）
            if folder_id:
                self.drive_service.files().update(
                    fileId=document_id,
                    addParents=folder_id,
                    fields='id, parents'
                ).execute()
            
            return document.get('webViewLink')
        
        except HttpError as error:
            print(f'Googleドキュメント作成エラー: {error}')
            return None
    
    def save_to_local(self, title: str, content: str, folder_path: Path):
        """ローカルにテキストファイルとして保存"""
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / f"{title}.txt"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return file_path
