#!/usr/bin/env python3
"""
初期管理者ユーザーを作成するスクリプト
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from auth import create_user

def main():
    print("=" * 50)
    print("ISAIチャットボット - 初期ユーザー作成")
    print("=" * 50)
    print()
    
    username = input("ユーザー名を入力してください: ").strip()
    if not username:
        print("エラー: ユーザー名が入力されていません")
        return
    
    password = input("パスワードを入力してください: ").strip()
    if not password:
        print("エラー: パスワードが入力されていません")
        return
    
    if len(password) < 6:
        print("警告: パスワードは6文字以上を推奨します")
        confirm = input("続行しますか？ (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    email = input("メールアドレス（オプション）: ").strip()
    
    print()
    print("ユーザーを作成しています...")
    
    if create_user(username, password, email):
        print(f"✅ ユーザー '{username}' を作成しました！")
        print()
        print("管理画面にログインできます:")
        print("  URL: http://localhost:8002")
        print(f"  ユーザー名: {username}")
    else:
        print(f"❌ エラー: ユーザー '{username}' は既に存在します")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nキャンセルされました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
