import subprocess
import platform

class ZoomDetector:
    """Zoomアプリと会議の状態を検知"""
    
    @staticmethod
    def is_zoom_running():
        """Zoomアプリが起動しているかチェック"""
        try:
            if platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    ["pgrep", "-f", "Zoom"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            elif platform.system() == "Windows":
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq Zoom.exe"],
                    capture_output=True,
                    text=True
                )
                return "Zoom.exe" in result.stdout
            else:  # Linux
                result = subprocess.run(
                    ["pgrep", "-f", "zoom"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def get_zoom_window_title():
        """Zoomウィンドウのタイトルを取得"""
        try:
            if platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    ["osascript", "-e",
                     'tell application "System Events" to tell process "Zoom" to get title of window 1'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                return result.stdout.strip()
            else:
                # Windows/Linuxの実装は省略（必要に応じて追加）
                return ""
        except:
            return ""
    
    @staticmethod
    def is_meeting_active():
        """Zoom会議がアクティブかチェック"""
        if not ZoomDetector.is_zoom_running():
            return False
        
        try:
            window_title = ZoomDetector.get_zoom_window_title()
            if not window_title:
                return False
            
            window_title_lower = window_title.lower()
            
            # 会議中のキーワード
            meeting_keywords = [
                "meeting", "会議", "zoom", "webinar", "ウェビナー",
                "in meeting", "会議中", "participants"
            ]
            
            # 会議外のキーワード（除外）
            non_meeting_keywords = ["settings", "設定", "preferences"]
            
            # 会議中かチェック
            has_meeting_keyword = any(
                keyword in window_title_lower 
                for keyword in meeting_keywords
            )
            
            is_non_meeting = all(
                keyword not in window_title_lower
                for keyword in non_meeting_keywords
            ) or "meeting" in window_title_lower or "会議" in window_title_lower
            
            return has_meeting_keyword and is_non_meeting
        
        except Exception:
            return False
    
    @staticmethod
    def wait_for_meeting_start(timeout=300):
        """会議開始を待機"""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ZoomDetector.is_meeting_active():
                return True
            time.sleep(2)
        return False
    
    @staticmethod
    def wait_for_meeting_end(timeout=7200, check_interval=5):
        """会議終了を待機"""
        import time
        start_time = time.time()
        consecutive_checks = 0
        required_checks = 3
        
        while time.time() - start_time < timeout:
            if not ZoomDetector.is_meeting_active():
                consecutive_checks += 1
                if consecutive_checks >= required_checks:
                    return True
            else:
                consecutive_checks = 0
            
            time.sleep(check_interval)
        
        return False
