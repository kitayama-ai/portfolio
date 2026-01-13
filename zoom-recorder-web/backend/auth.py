from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import Config
import hashlib
import json
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
USERS_DB_FILE = Path.home() / ".zoom_recorder" / "users.json"

def load_users():
    """ユーザーを読み込む"""
    if USERS_DB_FILE.exists():
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users: dict):
    """ユーザーを保存"""
    USERS_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def get_user(username: str):
    """ユーザーを取得"""
    users = load_users()
    return users.get(username)

def create_user(username: str, password: str, email: str):
    """ユーザーを作成"""
    try:
        users = load_users()
        if username in users:
            return False
        users[username] = {
            "username": username,
            "hashed_password": AuthService.get_password_hash(password),
            "email": email
        }
        save_users(users)
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
