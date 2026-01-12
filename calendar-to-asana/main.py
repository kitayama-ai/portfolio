#!/usr/bin/env python3
"""
Googleカレンダーから予定を取得してAsanaのマイタスクに登録するツール
"""
from datetime import datetime, date
from calendar_service import CalendarService
from asana_service import AsanaService
import sys

def main():
    """メイン処理"""
    print(f"[{datetime.now()}] カレンダーから予定を取得してAsanaに登録します...")
    
    # カレンダーサービス
    calendar_service = CalendarService()
    events = calendar_service.get_today_events()
    
    if not events:
        print("今日の予定はありません")
        return
    
    print(f"今日の予定が{len(events)}件見つかりました")
    
    # Asanaサービス
    asana_service = AsanaService()
    if not asana_service.authenticate():
        print("Asana認証に失敗しました")
        sys.exit(1)
    
    # 各予定をAsanaタスクとして登録
    today = date.today()
    created_count = 0
    
    for event in events:
        summary = event.get('summary', '予定なし')
        start = event.get('start', {})
        start_time = start.get('dateTime') or start.get('date')
        
        # 説明を作成
        notes_parts = []
        if start_time:
            notes_parts.append(f"開始時刻: {start_time}")
        if event.get('location'):
            notes_parts.append(f"場所: {event.get('location')}")
        if event.get('description'):
            notes_parts.append(f"説明: {event.get('description')}")
        
        notes = "\n".join(notes_parts) if notes_parts else None
        
        # タスクを作成
        task = asana_service.create_task(
            name=summary,
            notes=notes,
            due_on=today
        )
        
        if task:
            created_count += 1
    
    print(f"{created_count}件のタスクをAsanaに登録しました")

if __name__ == "__main__":
    main()
