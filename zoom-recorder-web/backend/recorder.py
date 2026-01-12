import subprocess
import os
import signal
from datetime import datetime
from pathlib import Path
import platform
from typing import Optional

class HeadlessZoomRecorder:
    """Zoom録画・文字起こしレコーダー"""
    
    def __init__(self, recording_folder: Optional[Path] = None):
        if recording_folder:
            self.output_dir = Path(recording_folder)
        else:
            self.output_dir = Path.home() / "Documents" / "ZoomRecordings"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.recording_process = None
        self.output_path = None
        self.is_macos = platform.system() == "Darwin"
    
    def prevent_sleep(self):
        """macOSがスリープしないように設定"""
        if self.is_macos:
            subprocess.Popen(
                ["caffeinate", "-d"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    
    def start_recording(self, meeting_title: str, audio_only: bool = False):
        """録画開始"""
        self.prevent_sleep()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{meeting_title}_{timestamp}.mp4"
        self.output_path = self.output_dir / filename
        
        if audio_only:
            # 音声のみ録音
            cmd = [
                "ffmpeg",
                "-f", "avfoundation",
                "-i", ":0",  # 音声のみ（BlackHole）
                "-c:a", "aac",
                "-b:a", "192k",
                "-loglevel", "error",
                "-y",
                str(self.output_path)
            ]
        else:
            # 画面+音声録画
            cmd = [
                "ffmpeg",
                "-f", "avfoundation",
                "-framerate", "30",
                "-video_size", "1920x1080",
                "-i", "1:0",  # 画面:音声（BlackHole）
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-loglevel", "error",
                "-y",
                str(self.output_path)
            ]
        
        self.recording_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return self.output_path
    
    def stop_recording(self) -> Optional[Path]:
        """録画停止"""
        if self.recording_process:
            self.recording_process.send_signal(signal.SIGINT)
            self.recording_process.wait(timeout=5)
            return self.output_path
        return None
    
    def is_recording(self) -> bool:
        """録画中かチェック"""
        if self.recording_process:
            return self.recording_process.poll() is None
        return False


class TranscriptionOnlyRecorder:
    """文字起こしのみモード（録画なし）"""
    
    def __init__(self):
        self.recording_process = None
        self.output_path = None
    
    def start_recording(self, meeting_title: str, temp_folder: Path):
        """音声のみ録音（一時ファイル）"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{meeting_title}_{timestamp}.m4a"
        self.output_path = temp_folder / filename
        temp_folder.mkdir(parents=True, exist_ok=True)
        
        # 音声のみ録音
        cmd = [
            "ffmpeg",
            "-f", "avfoundation",
            "-i", ":0",  # 音声のみ（BlackHole）
            "-c:a", "aac",
            "-b:a", "192k",
            "-loglevel", "error",
            "-y",
            str(self.output_path)
        ]
        
        self.recording_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return self.output_path
    
    def stop_recording(self) -> Optional[Path]:
        """録音停止"""
        if self.recording_process:
            self.recording_process.send_signal(signal.SIGINT)
            self.recording_process.wait(timeout=5)
            return self.output_path
        return None
    
    def is_recording(self) -> bool:
        """録音中かチェック"""
        if self.recording_process:
            return self.recording_process.poll() is None
        return False
    
    def cleanup(self):
        """一時ファイルを削除"""
        if self.output_path and self.output_path.exists():
            self.output_path.unlink()
