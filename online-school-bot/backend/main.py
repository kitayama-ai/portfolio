from fastapi import FastAPI, Request, HTTPException, Depends, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import uuid

from config import Config
from line_bot import LineBotService
from chatwork_bot import ChatworkBotService
from pdf_processor import PDFProcessor
from ai_responder import AIResponder
from satisfaction_analyzer import SatisfactionAnalyzer
from spreadsheet import SpreadsheetService
from slack_notifier import SlackNotifier
from course_manager import CourseManager
from conversation_manager import ConversationManager
from auth import AuthService, verify_token, get_user, create_user

app = FastAPI(title="オンラインスクールチャットボット")

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

# グローバルサービス（初期化時にエラーが発生しても続行可能にする）
try:
    pdf_processor = PDFProcessor()
except Exception as e:
    print(f"PDFProcessor初期化エラー: {e}")
    pdf_processor = None

try:
    ai_responder = AIResponder()
except Exception as e:
    print(f"AIResponder初期化エラー: {e}")
    ai_responder = None

try:
    satisfaction_analyzer = SatisfactionAnalyzer()
except Exception as e:
    print(f"SatisfactionAnalyzer初期化エラー: {e}")
    satisfaction_analyzer = None

try:
    spreadsheet_service = SpreadsheetService()
except Exception as e:
    print(f"SpreadsheetService初期化エラー: {e}")
    spreadsheet_service = None

try:
    slack_notifier = SlackNotifier()
except Exception as e:
    print(f"SlackNotifier初期化エラー: {e}")
    slack_notifier = None

course_manager = CourseManager()
conversation_manager = ConversationManager()

# LINEボットインスタンス（コースごと）
line_bots: Dict[str, LineBotService] = {}

def get_line_bot(course_id: str) -> Optional[LineBotService]:
    """コースIDからLINEボットを取得"""
    if course_id not in line_bots:
        try:
            line_bots[course_id] = LineBotService(course_id)
        except Exception as e:
            print(f"LINEボット初期化エラー ({course_id}): {e}")
            return None
    return line_bots.get(course_id)

# Chatworkボットインスタンス（コースごと）
chatwork_bots: Dict[str, ChatworkBotService] = {}

def get_chatwork_bot(course_id: str) -> Optional[ChatworkBotService]:
    """コースIDからChatworkボットを取得"""
    if course_id not in chatwork_bots:
        try:
            chatwork_bots[course_id] = ChatworkBotService(course_id)
        except Exception as e:
            print(f"Chatworkボット初期化エラー ({course_id}): {e}")
            return None
    return chatwork_bots.get(course_id)

# モデル
class LoginRequest(BaseModel):
    username: str
    password: str

class CourseRegisterRequest(BaseModel):
    course_id: str
    course_name: str
    manager_slack_id: Optional[str] = None
    platform: str = "chatwork"  # "chatwork" or "line"

# APIエンドポイント
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """管理画面を返す"""
    admin_file = frontend_dir / "admin.html"
    if admin_file.exists():
        with open(admin_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>オンラインスクールチャットボット管理画面</h1><p>フロントエンドファイルが見つかりません</p>"

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

@app.post("/api/webhook/line/{course_id}")
async def line_webhook(course_id: str, request: Request):
    """LINE Webhook受信"""
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")
    
    line_bot = get_line_bot(course_id)
    if not line_bot:
        raise HTTPException(status_code=400, detail=f"コース {course_id} のLINEボットが設定されていません")
    
    def handle_event(event_type: str, event):
        """イベントハンドラー"""
        if event_type == "follow":
            # 友だち追加時
            user_id = event.source.user_id
            user_profile = line_bot.get_user_profile(user_id)
            user_name = user_profile.get("display_name", user_id) if user_profile else user_id
            
            welcome_message = f"""こんにちは、{user_name}さん！
オンラインスクールの教材に関する質問にお答えします。
何かご質問がございましたら、お気軽にお聞かせください。"""
            
            line_bot.send_message(user_id, welcome_message)
        
        elif event_type == "message":
            # メッセージ受信
            user_id = event.source.user_id
            user_message = event.message.text
            
            # 会話IDを取得または作成
            conversation_id = conversation_manager.get_or_create_conversation(user_id, course_id)
            
            # 質問かどうかを判定
            if not satisfaction_analyzer or not satisfaction_analyzer.is_question(user_message):
                # 質問ではない場合は記録しない
                return
            
            # 会話履歴を取得
            conversation_history = conversation_manager.get_conversation_history(conversation_id)
            history_for_ai = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversation_history
            ]
            
            # ユーザープロフィールを取得
            user_profile = line_bot.get_user_profile(user_id)
            user_name = user_profile.get("display_name", user_id) if user_profile else user_id
            
            # AI回答を生成
            if not ai_responder:
                bot_response = "申し訳ございません。現在サービスを利用できません。"
            else:
                bot_response = ai_responder.generate_response(
                    user_message, course_id, history_for_ai
                )
            
            # 満足度を分析
            if not satisfaction_analyzer:
                satisfaction = {
                    "satisfaction_score": 0.5,
                    "is_satisfied": True,
                    "reason": "分析サービスが利用できません",
                    "needs_human_review": False
                }
                is_same_question = False
            else:
                satisfaction = satisfaction_analyzer.analyze_satisfaction(
                    user_message, bot_response, history_for_ai
                )
                
                # 同じ質問かどうかをチェック
                is_same_question = satisfaction_analyzer.check_same_question(user_message, history_for_ai)
            
            # 同じ質問の場合は満足度を下げる
            if is_same_question:
                satisfaction["satisfaction_score"] = max(0, satisfaction["satisfaction_score"] - 0.3)
                satisfaction["is_satisfied"] = satisfaction["satisfaction_score"] > Config.SATISFACTION_THRESHOLD
                satisfaction["needs_human_review"] = True
                satisfaction["reason"] = "同じ内容について再度質問されています"
            
            # メッセージを会話履歴に追加
            conversation_manager.add_message(conversation_id, "user", user_message)
            conversation_manager.add_message(conversation_id, "assistant", bot_response)
            
            # スプレッドシートに記録
            if spreadsheet_service and spreadsheet_service.service:
                try:
                    spreadsheet_service.append_record(
                        course_id, user_name, user_message, bot_response,
                        satisfaction, conversation_id
                    )
                except Exception as e:
                    print(f"スプレッドシート記録エラー: {e}")
            
            # ボット回答を送信
            line_bot.send_message(user_id, bot_response)
            
            # 二次回答が必要な場合、Slackに通知
            if satisfaction.get("needs_human_review", False) and slack_notifier and slack_notifier.client:
                try:
                    course_info = course_manager.get_course(course_id)
                    manager_slack_id = course_info.get("manager_slack_id") if course_info else None
                    
                    slack_notifier.notify_human_review_needed(
                        course_id, user_id, user_name, user_message, bot_response,
                        satisfaction, conversation_id, manager_slack_id
                    )
                except Exception as e:
                    print(f"Slack通知エラー: {e}")
    
    try:
        line_bot.handle_webhook(body.decode("utf-8"), signature, handle_event)
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook処理エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook/chatwork/{course_id}")
async def chatwork_webhook(course_id: str, request: Request):
    """Chatwork Webhook受信"""
    try:
        body = await request.json()
    except:
        body = {}
    
    chatwork_bot = get_chatwork_bot(course_id)
    if not chatwork_bot:
        raise HTTPException(status_code=400, detail=f"コース {course_id} のChatworkボットが設定されていません")
    
    def handle_event(event_type: str, event):
        """イベントハンドラー"""
        if event_type == "member_added":
            # メンバー追加時（初回DM時など）
            room_id = event.get("room_id")
            account_id = event.get("account_id")
            
            user_info = chatwork_bot.get_user_info(account_id)
            user_name = user_info.get("name", str(account_id)) if user_info else str(account_id)
            
            welcome_message = f"""[info][title]こんにちは、{user_name}さん！[/title]
オンラインスクールの教材に関する質問にお答えします。
何かご質問がございましたら、お気軽にお聞かせください。[/info]"""
            
            chatwork_bot.send_message(room_id, welcome_message)
        
        elif event_type == "message":
            # メッセージ受信
            room_id = event.get("room_id")
            account_id = event.get("from_account_id")
            user_message = event.get("body", "").strip()
            
            # ボット自身のメッセージは無視
            my_info = chatwork_bot.get_my_info()
            if my_info and account_id == my_info.get("account_id"):
                return
            
            # 会話IDを取得または作成（room_idとaccount_idの組み合わせ）
            conversation_id = conversation_manager.get_or_create_conversation(
                f"chatwork_{room_id}_{account_id}", course_id
            )
            
            # 質問かどうかを判定
            if not satisfaction_analyzer or not satisfaction_analyzer.is_question(user_message):
                # 質問ではない場合は記録しない
                return
            
            # 会話履歴を取得
            conversation_history = conversation_manager.get_conversation_history(conversation_id)
            history_for_ai = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversation_history
            ]
            
            # ユーザー情報を取得
            user_info = chatwork_bot.get_user_info(account_id)
            user_name = user_info.get("name", str(account_id)) if user_info else str(account_id)
            
            # AI回答を生成
            if not ai_responder:
                bot_response = "申し訳ございません。現在サービスを利用できません。"
            else:
                bot_response = ai_responder.generate_response(
                    user_message, course_id, history_for_ai
                )
            
            # 満足度を分析
            if not satisfaction_analyzer:
                satisfaction = {
                    "satisfaction_score": 0.5,
                    "is_satisfied": True,
                    "reason": "分析サービスが利用できません",
                    "needs_human_review": False
                }
                is_same_question = False
            else:
                satisfaction = satisfaction_analyzer.analyze_satisfaction(
                    user_message, bot_response, history_for_ai
                )
                
                # 同じ質問かどうかをチェック
                is_same_question = satisfaction_analyzer.check_same_question(user_message, history_for_ai)
            
            # 同じ質問の場合は満足度を下げる
            if is_same_question:
                satisfaction["satisfaction_score"] = max(0, satisfaction["satisfaction_score"] - 0.3)
                satisfaction["is_satisfied"] = satisfaction["satisfaction_score"] > Config.SATISFACTION_THRESHOLD
                satisfaction["needs_human_review"] = True
                satisfaction["reason"] = "同じ内容について再度質問されています"
            
            # メッセージを会話履歴に追加
            conversation_manager.add_message(conversation_id, "user", user_message)
            conversation_manager.add_message(conversation_id, "assistant", bot_response)
            
            # スプレッドシートに記録
            if spreadsheet_service and spreadsheet_service.service:
                try:
                    spreadsheet_service.append_record(
                        course_id, user_name, user_message, bot_response,
                        satisfaction, conversation_id
                    )
                except Exception as e:
                    print(f"スプレッドシート記録エラー: {e}")
            
            # ボット回答を送信
            chatwork_bot.send_message(room_id, bot_response)
            
            # 二次回答が必要な場合、Slackに通知
            if satisfaction.get("needs_human_review", False) and slack_notifier and slack_notifier.client:
                try:
                    course_info = course_manager.get_course(course_id)
                    manager_slack_id = course_info.get("manager_slack_id") if course_info else None
                    
                    slack_notifier.notify_human_review_needed(
                        course_id, f"chatwork_{account_id}", user_name, user_message, bot_response,
                        satisfaction, conversation_id, manager_slack_id
                    )
                except Exception as e:
                    print(f"Slack通知エラー: {e}")
    
    try:
        chatwork_bot.handle_webhook(body, handle_event)
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook処理エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/courses/register")
async def register_course(request: CourseRegisterRequest, credentials = Depends(verify_token)):
    """コースを登録"""
    success = course_manager.register_course(
        request.course_id, request.course_name, request.manager_slack_id, request.platform
    )
    if success:
        return {"status": "success", "message": "コースを登録しました"}
    else:
        raise HTTPException(status_code=400, detail="コースIDが既に存在します")

@app.get("/api/courses")
async def get_courses(credentials = Depends(verify_token)):
    """全コースを取得"""
    courses = course_manager.get_all_courses()
    return {"courses": courses}

@app.post("/api/courses/{course_id}/pdf")
async def upload_pdf(
    course_id: str,
    file: UploadFile = File(...),
    credentials = Depends(verify_token)
):
    """PDF教材をアップロード"""
    if not pdf_processor:
        raise HTTPException(status_code=500, detail="PDF処理サービスが利用できません")
    
    # 一時ファイルに保存
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        temp_path = Path(tmp_file.name)
    
    try:
        # PDFを処理
        result = pdf_processor.process_pdf(str(temp_path), course_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF処理エラー: {str(e)}")
    finally:
        # 一時ファイルを削除
        if temp_path.exists():
            temp_path.unlink()

@app.get("/api/conversations")
async def get_conversations(
    course_id: Optional[str] = None,
    limit: int = 100,
    credentials = Depends(verify_token)
):
    """会話履歴を取得"""
    if not spreadsheet_service or not spreadsheet_service.service:
        return {"conversations": []}
    conversations = spreadsheet_service.get_conversations(course_id, limit)
    return {"conversations": conversations}

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    credentials = Depends(verify_token)
):
    """特定の会話を取得"""
    conversation = conversation_manager.load_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="会話が見つかりません")
    return {"conversation": conversation}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
