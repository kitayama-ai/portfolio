import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import threading
import webbrowser
import socket
from pathlib import Path

class ServerLauncher:
    """サーバー起動アプリ（一般ユーザー向け）"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zoom録画ツール サーバー")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.server_process = None
        self.setup_ui()
    
    def setup_ui(self):
        # タイトル
        title = tk.Label(
            self.root,
            text="🎥 Zoom自動録画ツール",
            font=("Helvetica", 16, "bold"),
            pady=20
        )
        title.pack()
        
        # ステータス
        self.status_label = tk.Label(
            self.root,
            text="停止中",
            font=("Helvetica", 12),
            fg="gray"
        )
        self.status_label.pack(pady=10)
        
        # 起動ボタン
        self.start_btn = tk.Button(
            self.root,
            text="▶️ サーバーを起動",
            command=self.start_server,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 12),
            width=20,
            height=2
        )
        self.start_btn.pack(pady=10)
        
        # 停止ボタン
        self.stop_btn = tk.Button(
            self.root,
            text="⏹️ サーバーを停止",
            command=self.stop_server,
            bg="#f44336",
            fg="white",
            font=("Helvetica", 12),
            width=20,
            height=2,
            state=tk.DISABLED
        )
        self.stop_btn.pack(pady=10)
        
        # アクセス情報
        self.info_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 9),
            fg="blue",
            cursor="hand2"
        )
        self.info_label.pack(pady=10)
        self.info_label.bind("<Button-1>", self.open_browser)
    
    def get_local_ip(self):
        """ローカルIPアドレスを取得"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    def start_server(self):
        """サーバーを起動"""
        def run():
            backend_dir = Path(__file__).parent.parent / "backend"
            self.server_process = subprocess.Popen(
                [sys.executable, str(backend_dir / "main.py")],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.root.after(0, lambda: self.on_server_started())
        
        threading.Thread(target=run, daemon=True).start()
    
    def on_server_started(self):
        """サーバー起動後の処理"""
        self.status_label.config(text="起動中...", fg="orange")
        self.start_btn.config(state=tk.DISABLED)
        
        # 少し待ってからブラウザを開く
        self.root.after(2000, lambda: self.open_browser())
        
        ip = self.get_local_ip()
        self.info_label.config(
            text=f"アクセス: http://{ip}:8000\n（クリックで開く）"
        )
        
        self.root.after(3000, lambda: self.status_label.config(
            text="起動中", fg="green"
        ))
        self.stop_btn.config(state=tk.NORMAL)
    
    def stop_server(self):
        """サーバーを停止"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
        
        self.status_label.config(text="停止中", fg="gray")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.info_label.config(text="")
    
    def open_browser(self, event=None):
        """ブラウザで開く"""
        webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    app = ServerLauncher()
    app.root.mainloop()
