from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import traceback

# macOS専用モジュール（クラウド環境ではスキップ）
try:
    from recorder import HeadlessZoomRecorder, TranscriptionOnlyRecorder
    from zoom_detector import ZoomDetector
    HAS_LOCAL_FEATURES = True
except ImportError as e:
    print(f"ローカル機能のインポートをスキップ: {e}")
    HeadlessZoomRecorder = None
    TranscriptionOnlyRecorder = None
    ZoomDetector = None
    HAS_LOCAL_FEATURES = False
from transcription import TranscriptionService
from meeting_summary import MeetingSummaryService
from slack_notifier import SlackNotifier
from google_docs import GoogleDocsService
from config_manager import ConfigManager
from auth import AuthService, verify_token, get_user, create_user, load_users
from config import Config

app = FastAPI(title="Zoom自動録画ツール")

# エラーハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """グローバルエラーハンドラー"""
    print(f"エラー発生: {type(exc).__name__}: {str(exc)}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"サーバーエラー: {str(exc)}"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """バリデーションエラーハンドラー"""
    print(f"バリデーションエラー: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# CORS設定
# GitHub Pages用に特定のオリジンを許可（本番環境では適切に設定）
allowed_origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # GitHub Pagesのドメインを追加（例: "https://kitayama-ai.github.io"）
    # 環境変数から取得することも可能
]
# 開発環境ではすべて許可（本番環境では削除推奨）
if os.getenv("ENVIRONMENT") != "production":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルのマウント
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_dir)), name="frontend")
    # 静的ファイルとして直接提供
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="frontend_static")

# ルートパス: トークンチェックして適切なページにリダイレクト
@app.get("/")
async def root():
    """ルートパス: トークンチェックして適切なページにリダイレクト"""
    from fastapi.responses import RedirectResponse, HTMLResponse
    # フロントエンドのindex.htmlを返す（トークンチェックはフロントエンドで行う）
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return RedirectResponse(url="/frontend/login.html")

# グローバル状態
recorder_state: Dict = {
    "recording": False,
    "recorder": None,
    "recording_path": None,
    "meeting_title": None,
    "start_time": None,
    "zoom_status": "未検出",
    "meeting_active": False,
    "mode": "recording_and_transcription"
}

# WebSocket接続管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# エージェント接続管理
agent_connections: Dict[str, WebSocket] = {}

# モデル
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str

class RecordingRequest(BaseModel):
    meeting_title: Optional[str] = None
    audio_only: bool = False
    auto_stop: bool = True
    mode: str = "recording_and_transcription"

class SettingsRequest(BaseModel):
    recording_folder: str
    document_folder: str
    google_docs_enabled: bool = False

# APIエンドポイント
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """フロントエンドを返す"""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Zoom自動録画ツール</h1><p>フロントエンドファイルが見つかりません</p>"

@app.get("/login.html", response_class=HTMLResponse)
async def login_page():
    """ログインページ"""
    login_file = frontend_dir / "login.html"
    if login_file.exists():
        with open(login_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>ログイン</h1><p>ログインファイルが見つかりません</p>"

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """ログイン"""
    print(f"ログイン試行: username={request.username}")
    
    user = get_user(request.username)
    if not user:
        print(f"ユーザーが見つかりません: {request.username}")
        raise HTTPException(status_code=401, detail="ユーザー名またはパスワードが正しくありません")
    
    print(f"ユーザーが見つかりました: {request.username}, hashed_password存在: {'hashed_password' in user}")
    
    password_valid = AuthService.verify_password(request.password, user["hashed_password"])
    print(f"パスワード検証結果: {password_valid}")
    
    if not password_valid:
        print(f"パスワードが一致しません: {request.username}")
        raise HTTPException(status_code=401, detail="ユーザー名またはパスワードが正しくありません")
    
    access_token = AuthService.create_access_token(
        data={"sub": request.username}
    )
    
    print(f"ログイン成功: {request.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": request.username
    }

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """新規登録"""
    try:
        print(f"登録リクエスト: username={request.username}, email={request.email}")
        if get_user(request.username):
            raise HTTPException(status_code=400, detail="このユーザー名は既に使用されています")
        
        result = create_user(request.username, request.password, request.email)
        print(f"create_user結果: {result}")
        if result:
            return {"status": "success", "message": "ユーザー登録が完了しました"}
        else:
            raise HTTPException(status_code=400, detail="ユーザー登録に失敗しました")
    except HTTPException:
        raise
    except Exception as e:
        print(f"登録エラー: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"サーバーエラー: {str(e)}")

@app.get("/api/auth/me")
async def get_current_user(credentials = Depends(verify_token)):
    """現在のユーザー情報を取得"""
    username = credentials.get("sub")
    user = get_user(username)

    if user:
        return {"username": user["username"], "email": user.get("email", "")}
    raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

@app.get("/api/settings")
async def get_settings(credentials = Depends(verify_token)):
    """設定を取得"""
    config = ConfigManager.load_config()
    return {
        "recording_folder": config["recording_folder"],
        "document_folder": config["document_folder"],
        "google_docs_enabled": config.get("google_docs_enabled", False)
    }

@app.post("/api/settings")
async def save_settings(request: SettingsRequest, credentials = Depends(verify_token)):
    """設定を保存"""
    config = ConfigManager.load_config()
    config["recording_folder"] = request.recording_folder
    config["document_folder"] = request.document_folder
    config["google_docs_enabled"] = request.google_docs_enabled
    
    # フォルダが存在するか確認
    recording_folder = Path(request.recording_folder)
    document_folder = Path(request.document_folder)
    
    try:
        recording_folder.mkdir(parents=True, exist_ok=True)
        document_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"フォルダ作成エラー: {str(e)}")
    
    ConfigManager.save_config(config)
    return {"status": "success", "message": "設定を保存しました"}

@app.get("/api/status")
async def get_status():
    """現在の状態を取得"""
    return {
        "recording": recorder_state["recording"],
        "zoom_status": recorder_state["zoom_status"],
        "meeting_active": recorder_state["meeting_active"],
        "meeting_title": recorder_state["meeting_title"],
        "start_time": recorder_state["start_time"].isoformat() if recorder_state["start_time"] else None,
        "duration": (datetime.now() - recorder_state["start_time"]).total_seconds() 
                    if recorder_state["start_time"] else 0
    }

@app.post("/api/recording/start")
async def start_recording(request: RecordingRequest, credentials = Depends(verify_token)):
    """録画開始"""
    if not HAS_LOCAL_FEATURES:
        raise HTTPException(status_code=400, detail="録画機能はローカル環境のみ利用可能です")
    
    if recorder_state["recording"]:
        raise HTTPException(status_code=400, detail="既に録画中です")
    
    if not recorder_state["meeting_active"]:
        raise HTTPException(status_code=400, detail="Zoom会議が検出されていません")
    
    username = credentials.get("sub")
    config = ConfigManager.load_config(username)
    recording_folder = ConfigManager.get_recording_folder(username)
    document_folder = ConfigManager.get_document_folder(username)
    
    recorder_state["mode"] = request.mode
    
    try:
        if request.mode == "transcription_only":
            recorder = TranscriptionOnlyRecorder(
                output_dir=recording_folder,
                meeting_title=request.meeting_title or recorder_state["meeting_title"]
            )
        else:
            recorder = HeadlessZoomRecorder(
                output_dir=recording_folder,
                meeting_title=request.meeting_title or recorder_state["meeting_title"],
                audio_only=request.audio_only
            )
        
        recorder.start()
        recorder_state["recording"] = True
        recorder_state["recorder"] = recorder
        recorder_state["start_time"] = datetime.now()
        recorder_state["recording_path"] = recorder.output_path
        
        # 自動停止モニタリング
        if request.auto_stop:
            asyncio.create_task(auto_stop_monitoring(username))
        
        # WebSocketで通知
        await manager.broadcast({
            "type": "recording_started",
            "recording": True,
            "mode": request.mode,
            "audio_only": request.audio_only if request.mode != "transcription_only" else True
        })
        
        return {
            "status": "success",
            "message": "録画を開始しました",
            "recording": True,
            "mode": request.mode
        }
    except Exception as e:
        print(f"録画開始エラー: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"録画開始エラー: {str(e)}")

@app.post("/api/recording/stop")
async def stop_recording(credentials = Depends(verify_token)):
    """録画停止"""
    if not recorder_state["recording"]:
        raise HTTPException(status_code=400, detail="録画中ではありません")
    
    username = credentials.get("sub")
    recorder = recorder_state["recorder"]
    
    try:
        recorder.stop()
        recording_path = recorder_state["recording_path"]
        
        recorder_state["recording"] = False
        recorder_state["recorder"] = None
        recorder_state["recording_path"] = None
        
        # 非同期で処理
        asyncio.create_task(process_recording_async(recording_path, username, recorder_state["mode"]))
        
        # WebSocketで通知
        await manager.broadcast({
            "type": "recording_stopped",
            "recording": False
        })
        
        return {
            "status": "success",
            "message": "録画を停止しました",
            "recording": False
        }
    except Exception as e:
        print(f"録画停止エラー: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"録画停止エラー: {str(e)}")

async def auto_stop_monitoring(username: str):
    """会議終了を監視して自動停止"""
    while recorder_state["recording"]:
        await asyncio.sleep(5)
        
        if not recorder_state["meeting_active"]:
            print("会議が終了したため、録画を自動停止します")
            recorder = recorder_state["recorder"]
            if recorder:
                try:
                    recorder.stop()
                    recording_path = recorder_state["recording_path"]
                    
                    recorder_state["recording"] = False
                    recorder_state["recorder"] = None
                    recorder_state["recording_path"] = None
                    
                    # 非同期で処理
                    await process_recording_async(recording_path, username, recorder_state["mode"])
                    
                    # WebSocketで通知
                    await manager.broadcast({
                        "type": "recording_auto_stopped",
                        "recording": False,
                        "reason": "会議終了"
                    })
                except Exception as e:
                    print(f"自動停止エラー: {e}")
                    traceback.print_exc()
            break

async def process_recording_async(recording_path: str, username: str, mode: str):
    """録画後の処理（文字起こし、議事録生成など）"""
    try:
        config = ConfigManager.load_config(username)
        document_folder = ConfigManager.get_document_folder(username)
        
        if mode == "transcription_only" or not recording_path.endswith(".mp4"):
            # 音声ファイルの場合
            audio_path = recording_path
        else:
            # 動画ファイルから音声を抽出（必要に応じて）
            audio_path = recording_path.replace(".mp4", ".wav")
            # TODO: ffmpegで音声抽出
        
        # 文字起こし
        transcription_service = TranscriptionService()
        transcript = transcription_service.transcribe_audio(audio_path)
        
        if not transcript:
            print("文字起こしに失敗しました")
            return
        
        # 議事録生成
        summary_service = MeetingSummaryService()
        summary = summary_service.generate_summary(transcript)
        
        # ファイル保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        transcript_file = Path(document_folder) / f"transcript_{timestamp}.txt"
        summary_file = Path(document_folder) / f"summary_{timestamp}.txt"
        
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)
        
        # Googleドキュメントに保存（オプション）
        if config.get("google_docs_enabled", False):
            try:
                docs_service = GoogleDocsService()
                doc_title = f"議事録_{timestamp}"
                doc_url = docs_service.create_document(doc_title, summary)
                print(f"Googleドキュメントに保存しました: {doc_url}")
            except Exception as e:
                print(f"Googleドキュメント保存エラー: {e}")
        
        # Slack通知（オプション）
        if Config.SLACK_BOT_TOKEN and Config.SLACK_CHANNEL:
            try:
                notifier = SlackNotifier()
                notifier.send_meeting_summary(
                    title=recorder_state.get("meeting_title", "会議"),
                    summary=summary,
                    transcript=transcript
                )
            except Exception as e:
                print(f"Slack通知エラー: {e}")
        
        # WebSocketで通知
        await manager.broadcast({
            "type": "processing_complete",
            "transcript_file": str(transcript_file),
            "summary_file": str(summary_file)
        })
        
    except Exception as e:
        print(f"録画処理エラー: {e}")
        traceback.print_exc()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocketエンドポイント（クライアント接続用）"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/agent")
async def websocket_agent(websocket: WebSocket, token: str = None):
    """WebSocketエンドポイント（エージェント接続用）"""
    # TODO: トークン認証
    
    await websocket.accept()
    agent_id = None
    
    try:
        # エージェント登録
        message = await websocket.receive_json()
        if message.get("type") == "agent_register":
            agent_id = message.get("hostname", "unknown")
            agent_connections[agent_id] = websocket
            print(f"エージェント登録: {agent_id}")
        
        # エージェントからのメッセージを処理
        while True:
            try:
                message = await websocket.receive_json()
                message_type = message.get("type")
                
                if message_type == "recording_status":
                    # エージェントからの録画状態更新
                    recorder_state["recording"] = message.get("recording", False)
                    recorder_state["recording_path"] = message.get("recording_path")
                    
                    # クライアントに通知
                    await manager.broadcast({
                        "type": "recording_status_update",
                        "recording": recorder_state["recording"],
                        "recording_path": recorder_state["recording_path"]
                    })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"エージェントメッセージ処理エラー: {e}")
                traceback.print_exc()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"エージェント接続エラー: {e}")
        traceback.print_exc()
    finally:
        if agent_id and agent_id in agent_connections:
            del agent_connections[agent_id]
        print(f"エージェント切断: {agent_id}")

# 起動時のイベント（非推奨の@app.on_eventを使用）
try:
    @app.on_event("startup")
    async def startup_event():
        # Zoom状態監視はローカル環境のみ（クラウド環境ではスキップ）
        if HAS_LOCAL_FEATURES and os.getenv("RAILWAY_ENVIRONMENT") is None and os.getenv("RENDER") is None:
            asyncio.create_task(zoom_status_monitor())
        else:
            # クラウド環境では固定値
            recorder_state["zoom_status"] = "クラウド環境"
            recorder_state["meeting_active"] = False
except Exception as e:
    print(f"startup_event設定エラー（無視）: {e}")
    # クラウド環境では固定値
    recorder_state["zoom_status"] = "クラウド環境"
    recorder_state["meeting_active"] = False

async def zoom_status_monitor():
    """Zoom状態を監視（ローカル環境のみ）"""
    if not HAS_LOCAL_FEATURES or not ZoomDetector:
        return
    
    while True:
        try:
            zoom_running = ZoomDetector.is_zoom_running()
            meeting_active = ZoomDetector.is_meeting_active()
            
            zoom_status = "会議中" if meeting_active else ("起動中" if zoom_running else "未検出")
            
            recorder_state["zoom_status"] = zoom_status
            recorder_state["meeting_active"] = meeting_active
        except Exception as e:
            print(f"Zoom状態監視エラー: {e}")
        
        await asyncio.sleep(2)

if __name__ == "__main__":
    import uvicorn
    # RailwayやRenderなどのクラウド環境では環境変数からポートを取得
    port = int(os.getenv("PORT", 8000))
    print(f"サーバーを起動します: 0.0.0.0:{port}")
    print(f"Python version: {os.sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Frontend directory exists: {frontend_dir.exists()}")
    print(f"Static directory exists: {static_dir.exists()}")
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"起動エラー: {e}")
        import traceback
        traceback.print_exc()
        raise
