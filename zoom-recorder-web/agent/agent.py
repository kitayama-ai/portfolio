import asyncio
import websockets
import json
import subprocess
import sys
from pathlib import Path
import signal
from datetime import datetime

# バックエンドのモジュールをインポート（相対パスで）
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from recorder import HeadlessZoomRecorder, TranscriptionOnlyRecorder
    from zoom_detector import ZoomDetector
except ImportError as e:
    print(f"インポートエラー: {e}")
    print(f"バックエンドパス: {backend_path}")
    sys.exit(1)

class ZoomAgent:
    """Zoom録画エージェント（各PCで実行）"""
    
    def __init__(self, server_url: str, agent_token: str):
        self.server_url = server_url
        self.agent_token = agent_token
        self.recorder = None
        self.recording = False
        self.recording_path = None
    
    async def connect(self):
        """サーバーに接続"""
        ws_url = self.server_url.replace("http", "ws") + "/ws/agent"
        
        try:
            async with websockets.connect(
                f"{ws_url}?token={self.agent_token}"
            ) as websocket:
                hostname = subprocess.check_output(["hostname"]).decode().strip()
                await websocket.send(json.dumps({
                    "type": "agent_register",
                    "hostname": hostname
                }))
                
                print(f"サーバーに接続しました: {self.server_url}")
                print(f"PC名: {hostname}")
                
                async for message in websocket:
                    await self.handle_message(json.loads(message), websocket)
        except Exception as e:
            print(f"接続エラー: {e}")
            print("5秒後に再接続を試みます...")
            await asyncio.sleep(5)
            await self.connect()
    
    async def handle_message(self, message: dict, websocket):
        """メッセージを処理"""
        if message["type"] == "start_recording":
            await self.start_recording(message["data"], websocket)
        elif message["type"] == "stop_recording":
            await self.stop_recording(websocket)
        elif message["type"] == "get_status":
            await self.send_status(websocket)
    
    async def start_recording(self, data: dict, websocket):
        """録画開始"""
        if self.recording:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "既に録画中です"
            }))
            return
        
        try:
            meeting_title = data.get("meeting_title", f"Meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            mode = data.get("mode", "recording_and_transcription")
            recording_folder = Path(data.get("recording_folder", "~/Documents/ZoomRecordings")).expanduser()
            
            if mode == "transcription_only":
                temp_folder = Path("/tmp/zoom_transcription")
                self.recorder = TranscriptionOnlyRecorder()
                self.recording_path = self.recorder.start_recording(meeting_title, temp_folder)
            else:
                audio_only = data.get("audio_only", False)
                self.recorder = HeadlessZoomRecorder(recording_folder=recording_folder)
                self.recording_path = self.recorder.start_recording(meeting_title, audio_only=audio_only)
            
            self.recording = True
            
            await websocket.send(json.dumps({
                "type": "recording_started",
                "message": "録画を開始しました",
                "meeting_title": meeting_title
            }))
            
            print(f"録画開始: {meeting_title}")
        
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"録画開始エラー: {str(e)}"
            }))
            print(f"エラー: {e}")
    
    async def stop_recording(self, websocket):
        """録画停止"""
        if not self.recording:
            return
        
        try:
            output_path = self.recorder.stop_recording()
            self.recording = False
            
            await websocket.send(json.dumps({
                "type": "recording_stopped",
                "file_path": str(output_path),
                "message": "録画を停止しました"
            }))
            
            print(f"録画停止: {output_path}")
        
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"録画停止エラー: {str(e)}"
            }))
            print(f"エラー: {e}")
    
    async def send_status(self, websocket):
        """ステータスを送信"""
        zoom_running = ZoomDetector.is_zoom_running()
        meeting_active = ZoomDetector.is_meeting_active()
        
        await websocket.send(json.dumps({
            "type": "status",
            "data": {
                "recording": self.recording,
                "zoom_running": zoom_running,
                "meeting_active": meeting_active
            }
        }))

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Zoom録画エージェント")
    parser.add_argument("--server", required=True, help="サーバーURL")
    parser.add_argument("--token", required=True, help="エージェントトークン")
    
    args = parser.parse_args()
    
    agent = ZoomAgent(args.server, args.token)
    
    # シグナルハンドラ
    def signal_handler(sig, frame):
        print("\nエージェントを終了します...")
        if agent.recording and agent.recorder:
            agent.recorder.stop_recording()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(agent.connect())
    except KeyboardInterrupt:
        print("\nエージェントを終了します...")
        if agent.recording and agent.recorder:
            agent.recorder.stop_recording()

if __name__ == "__main__":
    main()
