from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import Config
import json
from pathlib import Path
import bcrypt

security = HTTPBearer()

class AuthService:
    """認証サービス"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """パスワードを検証"""
        try:
            # hashed_passwordは既に文字列として保存されているので、bytesに変換
            if isinstance(hashed_password, str):
                hashed_bytes = hashed_password.encode('ascii')
            else:
                hashed_bytes = hashed_password
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_bytes)
        except Exception:
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """パスワードをハッシュ化"""
        # bcrypt 5.0.0では72バイトを超えるとValueErrorが発生するため、事前に切り詰める
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        # bcrypt.hashpw()はbytesを返すが、bcryptハッシュはASCII文字のみを含むため、asciiでデコード可能
        if isinstance(hashed, bytes):
            return hashed.decode('ascii')
        return str(hashed)
    
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
# backendディレクトリ内のdataディレクトリに保存（ホームディレクトリへの書き込み権限がない場合に備える）
_backend_dir = Path(__file__).parent
USERS_DB_FILE = _backend_dir / "data" / "users.json"

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
    try:
        USERS_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except PermissionError:
        # ホームディレクトリへの書き込みができない場合、ワークスペース内に保存を試みる
        # 既にワークスペース内に設定されている場合は、エラーを再発生させる
        raise

def get_user(username: str):
    """ユーザーを取得"""
    users = load_users()
    return users.get(username)

def create_user(username: str, password: str, email: str = ""):
    """ユーザーを作成"""
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

# 後方互換性のため、関数エイリアスを提供
verify_token = AuthService.verify_token
