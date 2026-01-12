import asana
from typing import Optional, Dict
from config import Config
from datetime import datetime, date

class AsanaService:
    """Asanaにタスクを作成"""
    
    def __init__(self):
        self.access_token = Config.ASANA_ACCESS_TOKEN
        self.workspace_gid = Config.ASANA_WORKSPACE_GID
        self.client = None
        self.user_gid = None
    
    def authenticate(self) -> bool:
        """Asana認証"""
        if not self.access_token:
            print("Asanaアクセストークンが設定されていません")
            return False
        
        try:
            self.client = asana.Client.access_token(self.access_token)
            
            # ユーザー情報を取得
            me = self.client.users.me()
            self.user_gid = me['gid']
            
            # ワークスペースGIDが指定されていない場合、最初のワークスペースを使用
            if not self.workspace_gid and me.get('workspaces'):
                self.workspace_gid = me['workspaces'][0]['gid']
            
            return True
        except Exception as e:
            print(f'Asana認証エラー: {e}')
            return False
    
    def create_task(self, name: str, notes: Optional[str] = None, due_on: Optional[date] = None) -> Optional[Dict]:
        """マイタスクにタスクを作成"""
        if not self.client:
            if not self.authenticate():
                return None
        
        try:
            task_data = {
                'name': name,
                'assignee': self.user_gid,
                'workspace': self.workspace_gid,
            }
            
            if notes:
                task_data['notes'] = notes
            
            if due_on:
                # YYYY-MM-DD形式に変換
                task_data['due_on'] = due_on.strftime('%Y-%m-%d')
            
            task = self.client.tasks.create_task(task_data)
            print(f"タスクを作成しました: {task['name']} (GID: {task['gid']})")
            return task
        
        except Exception as e:
            print(f'タスク作成エラー: {e}')
            return None
