from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from recorder import HeadlessZoomRecorder, TranscriptionOnlyRecorder
from zoom_detector import ZoomDetector
from transcription import TranscriptionService
from meeting_summary import MeetingSummaryService
from slack_notifier import SlackNotifier
from google_docs import GoogleDocsService
from config_manager import ConfigManager
from auth import AuthService, verify_token, get_user, create_user, load_users
from config import Config

app = FastAPI(title="Zoom自動録画ツール")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    user = get_user(request.username)
    if not user:
        raise HTTPException(status_code=401, detail="ユーザー名またはパスワードが正しくありません")
    
    if not AuthService.verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="ユーザー名またはパスワードが正しくありません")
    
    access_token = AuthService.create_access_token(
        data={"sub": request.username}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": request.username
    }

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """新規登録"""
    if get_user(request.username):
        raise HTTPException(status_code=400, detail="このユーザー名は既に使用されています")
    
    if create_user(request.username, request.password, request.email):
        return {"status": "success", "message": "ユーザー登録が完了しました"}
    else:
        raise HTTPException(status_code=400, detail="ユーザー登録に失敗しました")

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
    if recorder_state["recording"]:
        raise HTTPException(status_code=400, detail="既に録画中です")
    
    if not recorder_state["meeting_active"]:
        raise HTTPException(status_code=400, detail="Zoom会議が検出されません")
    
    try:
        username = credentials.get("sub")
        meeting_title = request.meeting_title or f"Meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        mode = request.mode
        
        recording_folder = ConfigManager.get_recording_folder(username=username)
        
        if mode == "transcription_only":
            # 文字起こしのみモード
            temp_folder = Path("/tmp/zoom_transcription")
            temp_folder.mkdir(parents=True, exist_ok=True)
            recorder = TranscriptionOnlyRecorder()
            recording_path = recorder.start_recording(meeting_title, temp_folder)
        else:
            # 録画+文字起こしモード
            recorder = HeadlessZoomRecorder(recording_folder=recording_folder)
            recording_path = recorder.start_recording(
                meeting_title,
                audio_only=request.audio_only
            )
        
        recorder_state["recording"] = True
        recorder_state["recorder"] = recorder
        recorder_state["recording_path"] = recording_path
        recorder_state["meeting_title"] = meeting_title
        recorder_state["start_time"] = datetime.now()
        recorder_state["mode"] = mode
        recorder_state["username"] = username
        
        await manager.broadcast({
            "type": "recording_started",
            "meeting_title": meeting_title,
            "mode": mode
        })
        
        if request.auto_stop:
            asyncio.create_task(auto_stop_monitoring())
        
        return {"status": "success", "message": "録画を開始しました"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recording/stop")
async def stop_recording(credentials = Depends(verify_token)):
    """録画停止"""
    if not recorder_state["recording"]:
        raise HTTPException(status_code=400, detail="録画中ではありません")
    
    try:
        recorder_state["recording"] = False
        output_path = recorder_state["recorder"].stop_recording()
        username = credentials.get("sub") or recorder_state.get("username", "default")
        
        # バックグラウンドで処理
        asyncio.create_task(process_recording_async(
            output_path, 
            recorder_state["mode"],
            username
        ))
        
        await manager.broadcast({
            "type": "recording_stopped",
            "message": "録画を停止しました。処理中..."
        })
        
        return {"status": "success", "message": "録画を停止しました"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def auto_stop_monitoring():
    """会議終了を監視して自動停止"""
    while recorder_state["recording"]:
        if not ZoomDetector.is_meeting_active():
            await asyncio.sleep(5)
            if not ZoomDetector.is_meeting_active():
                recorder_state["recording"] = False
                if recorder_state["recorder"]:
                    output_path = recorder_state["recorder"].stop_recording()
                    username = recorder_state.get("username", "default")
                    if output_path:
                        asyncio.create_task(process_recording_async(
                            output_path,
                            recorder_state["mode"],
                            username
                        ))
                
                await manager.broadcast({
                    "type": "auto_stopped",
                    "message": "会議終了を検知して自動停止しました"
                })
                break
        await asyncio.sleep(2)

async def process_recording_async(output_path: Path, mode: str, username: str):
    """録画ファイルを非同期で処理"""
    try:
        meeting_title = recorder_state["meeting_title"]
        document_folder = ConfigManager.get_document_folder(username=username)
        
        # 文字起こし
        transcription_service = TranscriptionService()
        transcription_result = transcription_service.transcribe_audio(
            str(output_path),
            language="ja"
        )
        
        await manager.broadcast({
            "type": "transcription_complete",
            "duration": transcription_result["duration"]
        })
        
        # 議事録生成
        summary_service = MeetingSummaryService()
        summary = summary_service.generate_summary(
            transcription_result["text"],
            meeting_title=meeting_title
        )
        
        # ドキュメントとして保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_title = f"{meeting_title}_{timestamp}"
        
        # テキストファイルとして保存
        doc_path = document_folder / f"{doc_title}.txt"
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(f"会議名: {meeting_title}\n")
            f.write(f"日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n")
            f.write(f"録画時間: {transcription_result['duration']:.1f}秒\n\n")
            f.write("=" * 50 + "\n")
            f.write("議事録\n")
            f.write("=" * 50 + "\n\n")
            f.write(summary)
            f.write("\n\n" + "=" * 50 + "\n")
            f.write("文字起こし全文\n")
            f.write("=" * 50 + "\n\n")
            f.write(transcription_result["text"])
        
        await manager.broadcast({
            "type": "document_saved",
            "path": str(doc_path),
            "title": doc_title
        })
        
        # Googleドキュメントに保存（設定されている場合）
        config = ConfigManager.load_config()
        if config.get("google_docs_enabled"):
            try:
                google_docs = GoogleDocsService()
                doc_url = google_docs.create_document(
                    title=doc_title,
                    content=f"会議名: {meeting_title}\n\n{summary}\n\n---\n\n文字起こし全文:\n{transcription_result['text']}"
                )
                
                if doc_url:
                    await manager.broadcast({
                        "type": "google_docs_created",
                        "url": doc_url,
                        "title": doc_title
                    })
            except Exception as e:
                await manager.broadcast({
                    "type": "error",
                    "message": f"Googleドキュメント保存エラー: {str(e)}"
                })
        
        # Slackに送信
        slack_notifier = SlackNotifier()
        slack_notifier.send_meeting_summary(
            summary=summary,
            meeting_title=meeting_title,
            transcription_text=transcription_result["text"]
        )
        
        duration_minutes = transcription_result["duration"] / 60
        cost = duration_minutes * 0.006
        
        await manager.broadcast({
            "type": "processing_complete",
            "message": f"処理完了（コスト: ${cost:.4f}）",
            "cost": cost,
            "document_path": str(doc_path)
        })
        
        # 文字起こしのみモードの場合、一時ファイルを削除
        if mode == "transcription_only" and isinstance(recorder_state["recorder"], TranscriptionOnlyRecorder):
            recorder_state["recorder"].cleanup()
    
    except Exception as e:
        await manager.broadcast({
            "type": "error",
            "message": f"処理エラー: {str(e)}"
        })
        import traceback
        traceback.print_exc()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket接続"""
    await manager.connect(websocket)
    
    # 初期状態を送信
    await websocket.send_json({
        "type": "status",
        "data": {
            "recording": recorder_state["recording"],
            "zoom_status": recorder_state["zoom_status"],
            "meeting_active": recorder_state["meeting_active"]
        }
    })
    
    try:
        while True:
            # Zoom状態を定期的に更新
            zoom_running = ZoomDetector.is_zoom_running()
            meeting_active = ZoomDetector.is_meeting_active()
            
            zoom_status = "会議中" if meeting_active else ("起動中" if zoom_running else "未検出")
            
            if (recorder_state["zoom_status"] != zoom_status or 
                recorder_state["meeting_active"] != meeting_active):
                recorder_state["zoom_status"] = zoom_status
                recorder_state["meeting_active"] = meeting_active
                
                await websocket.send_json({
                    "type": "status_update",
                    "data": {
                        "zoom_status": zoom_status,
                        "meeting_active": meeting_active
                    }
                })
            
            await asyncio.sleep(2)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/agent")
async def websocket_agent(websocket: WebSocket, token: str = None):
    """エージェント接続"""
    if not token:
        await websocket.close(code=4001, reason="トークンが必要です")
        return
    
    await websocket.accept()
    agent_id = None
    
    try:
        # エージェント登録
        message = await websocket.receive_json()
        if message["type"] == "agent_register":
            agent_id = message.get("hostname", "unknown")
            agent_connections[agent_id] = websocket
            
            await manager.broadcast({
                "type": "agent_connected",
                "agent_id": agent_id
            })
        
        # メッセージを待機
        while True:
            message = await websocket.receive_json()
            await manager.broadcast(message)
    
    except WebSocketDisconnect:
        if agent_id and agent_id in agent_connections:
            del agent_connections[agent_id]
            await manager.broadcast({
                "type": "agent_disconnected",
                "agent_id": agent_id
            })

# バックグラウンドタスクでZoom状態を監視
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(zoom_status_monitor())

async def zoom_status_monitor():
    """Zoom状態を監視"""
    while True:
        zoom_running = ZoomDetector.is_zoom_running()
        meeting_active = ZoomDetector.is_meeting_active()
        
        zoom_status = "会議中" if meeting_active else ("起動中" if zoom_running else "未検出")
        
        recorder_state["zoom_status"] = zoom_status
        recorder_state["meeting_active"] = meeting_active
        
        await asyncio.sleep(2)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
