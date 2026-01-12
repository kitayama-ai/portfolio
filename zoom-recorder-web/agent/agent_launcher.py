import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import threading
import json
from pathlib import Path

class AgentLauncher:
    """エージェント起動アプリ（一般ユーザー向け）"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zoom録画ツール エージェント")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.agent_process = None
        self.load_config()
        self.setup_ui()
    
    def load_config(self):
        """設定を読み込む"""
        config_file = Path.home() / ".zoom_recorder_agent" / "config.json"
        if config_file.exists():
            with open(config_file) as f:
                self.config = json.load(f)
        else:
            self.config = None
    
    def setup_ui(self):
        # タイトル
        title = tk.Label(
            self.root,
            text="🖥️ Zoom録画エージェント",
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
        
        if not self.config:
            # 設定がない場合
            setup_btn = tk.Button(
                self.root,
                text="⚙️ セットアップ",
                command=self.setup,
                bg="#2196F3",
                fg="white",
                font=("Helvetica", 12),
                width=20,
                height=2
            )
            setup_btn.pack(pady=10)
        else:
            # サーバー情報表示
            info_label = tk.Label(
                self.root,
                text=f"サーバー: {self.config.get('server_url', 'N/A')}\n"
                     f"PC名: {self.config.get('pc_name', 'N/A')}",
                font=("Helvetica", 9),
                fg="gray"
            )
            info_label.pack(pady=5)
            
            # 起動ボタン
            self.start_btn = tk.Button(
                self.root,
                text="▶️ エージェントを起動",
                command=self.start_agent,
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
                text="⏹️ エージェントを停止",
                command=self.stop_agent,
                bg="#f44336",
                fg="white",
                font=("Helvetica", 12),
                width=20,
                height=2,
                state=tk.DISABLED
            )
            self.stop_btn.pack(pady=10)
    
    def setup(self):
        """セットアップ画面を開く"""
        messagebox.showinfo(
            "セットアップ",
            "セットアップ画面を開きます。\n"
            "サーバーURLとトークンを入力してください。"
        )
        # 実際には別ウィンドウでセットアップ画面を開く
        # ここでは簡易的にメッセージを表示
    
    def start_agent(self):
        """エージェントを起動"""
        def run():
            self.agent_process = subprocess.Popen(
                [
                    sys.executable,
                    str(Path(__file__).parent / "agent.py"),
                    "--server", self.config["server_url"],
                    "--token", self.config["token"]
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.root.after(0, lambda: self.on_agent_started())
        
        threading.Thread(target=run, daemon=True).start()
    
    def on_agent_started(self):
        """エージェント起動後の処理"""
        self.status_label.config(text="起動中...", fg="orange")
        self.start_btn.config(state=tk.DISABLED)
        
        self.root.after(2000, lambda: self.status_label.config(
            text="接続中", fg="green"
        ))
        self.stop_btn.config(state=tk.NORMAL)
    
    def stop_agent(self):
        """エージェントを停止"""
        if self.agent_process:
            self.agent_process.terminate()
            self.agent_process.wait()
        
        self.status_label.config(text="停止中", fg="gray")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = AgentLauncher()
    app.root.mainloop()
