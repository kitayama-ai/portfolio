from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import Config
import hashlib
import json
import os
from pathlib import Path

security = HTTPBearer()

class AuthService:
    """認証サービス"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """パスワードを検証"""
        try:
            # bcryptで直接検証
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            if isinstance(plain_password, str):
                plain_password = plain_password.encode('utf-8')
            result = bcrypt.checkpw(plain_password, hashed_password)
            print(f"パスワード検証: plain_length={len(plain_password)}, hashed_length={len(hashed_password)}, result={result}")
            return result
        except Exception as e:
            print(f"パスワード検証エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """パスワードをハッシュ化"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        # bcryptで直接ハッシュ化
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """アクセストークンを生成"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """トークンを検証"""
        token = credentials.credentials
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="認証に失敗しました",
                headers={"WWW-Authenticate": "Bearer"},
            )

# 簡易ユーザー管理（本番環境ではデータベースを使用）
# Renderなどのクラウド環境では、/tmpディレクトリを使用（永続化されないため、環境変数から初期ユーザーを読み込む）
if os.getenv("RENDER") or os.getenv("RAILWAY"):
    # クラウド環境: /tmpディレクトリを使用（永続化されない）
    USERS_DB_FILE = Path("/tmp") / "zoom_recorder_users.json"
    print("クラウド環境を検出: /tmpディレクトリを使用（永続化されません）")
else:
    # ローカル環境: ホームディレクトリを使用
    USERS_DB_FILE = Path.home() / ".zoom_recorder" / "users.json"
    print("ローカル環境: ホームディレクトリを使用")

def load_users():
    """ユーザーを読み込む"""
    print(f"ユーザーファイルパス: {USERS_DB_FILE}")
    print(f"ユーザーファイル存在: {USERS_DB_FILE.exists()}")
    
    users = {}
    
    # 環境変数から初期ユーザーを読み込む（Render環境用）
    default_username = os.getenv("DEFAULT_USERNAME")
    default_password = os.getenv("DEFAULT_PASSWORD")
    if default_username and default_password:
        print(f"環境変数から初期ユーザーを読み込み: {default_username}")
        users[default_username] = {
            "username": default_username,
            "hashed_password": AuthService.get_password_hash(default_password),
            "email": os.getenv("DEFAULT_EMAIL", f"{default_username}@example.com")
        }
        # 環境変数のユーザーをファイルに保存（存在する場合）
        if not USERS_DB_FILE.exists():
            save_users(users)
    
    # ファイルからユーザーを読み込む
    if USERS_DB_FILE.exists():
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                file_users = json.load(f)
                # ファイルのユーザーで環境変数のユーザーを上書き（ファイルが優先）
                users.update(file_users)
                print(f"ファイルから読み込んだユーザー数: {len(file_users)}, ユーザー名: {list(file_users.keys())}")
        except Exception as e:
            print(f"ユーザーファイル読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("ユーザーファイルが存在しません")
    
    print(f"合計ユーザー数: {len(users)}, ユーザー名: {list(users.keys())}")
    return users

def save_users(users: dict):
    """ユーザーを保存"""
    print(f"ユーザーを保存: ファイルパス={USERS_DB_FILE}, ユーザー数={len(users)}")
    USERS_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    print(f"ユーザー保存完了: {USERS_DB_FILE.exists()}")

def get_user(username: str):
    """ユーザーを取得"""
    users = load_users()  # 毎回load_usersを呼ぶことで、環境変数のユーザーも含まれる
    user = users.get(username)
    if user:
        print(f"ユーザーが見つかりました: {username}, hashed_password存在: {'hashed_password' in user}")
    else:
        print(f"ユーザーが見つかりません: {username}, 利用可能なユーザー: {list(users.keys())}")
        # 環境変数から直接読み込む（ファイルが存在しない場合のフォールバック）
        default_username = os.getenv("DEFAULT_USERNAME")
        default_password = os.getenv("DEFAULT_PASSWORD")
        if default_username == username and default_password:
            print(f"環境変数から直接ユーザーを読み込み: {username}")
            return {
                "username": default_username,
                "hashed_password": AuthService.get_password_hash(default_password),
                "email": os.getenv("DEFAULT_EMAIL", f"{default_username}@example.com")
            }
    return user

def create_user(username: str, password: str, email: str):
    """ユーザーを作成"""
    try:
        print(f"ユーザー作成開始: username={username}, email={email}, password_length={len(password)}")
        users = load_users()
        if username in users:
            print(f"ユーザー名が既に存在: {username}")
            return False
        hashed = AuthService.get_password_hash(password)
        print(f"パスワードハッシュ生成完了: hashed_length={len(hashed)}")
        users[username] = {
            "username": username,
            "hashed_password": hashed,
            "email": email
        }
        # ファイルに保存を試みる（失敗しても続行）
        try:
            save_users(users)
            print(f"ユーザー作成成功（ファイル保存済み）: {username}")
        except Exception as save_error:
            print(f"ファイル保存に失敗しましたが、メモリ上ではユーザーが作成されました: {save_error}")
            # Render環境では/tmpが永続化されないため、エラーを無視して続行
        return True
    except Exception as e:
        print(f"ユーザー作成エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

# 関数としてエクスポート（main.pyで使用）
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """トークンを検証（関数版）"""
    return AuthService.verify_token(credentials)
