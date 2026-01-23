from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
import json
from dotenv import load_dotenv
from vapi_client import VapiClient
from services.google_calendar import GoogleCalendarService
from services.twilio_service import TwilioService

# 環境変数の読み込み
load_dotenv()

app = FastAPI(title="AI Tele-Appointment Backend")

# サービスの初期化
vapi_client = VapiClient()
calendar_service = GoogleCalendarService()
twilio_service = TwilioService()

# サーバーのパブリックURL（Vapiからのコールバック用）
# ローカル開発時はngrokなどのURLを設定
SERVER_URL = os.getenv("SERVER_URL", "https://your-domain.com")

# リクエストモデル
class LeadRegistration(BaseModel):
    name: str
    phone: str
    email: str

@app.post("/api/register")
async def register_lead(lead: LeadRegistration):
    """
    LPからの登録を受け取り、Vapiへ架電リクエストを送る
    """
    print(f"New lead received: {lead.name}, {lead.phone}")
    
    # AIによる架電を開始 (Speed to Lead)
    # ここで serverUrl を渡すことで、Vapiがツール実行時にこのサーバーを叩くようになる
    call_result = vapi_client.make_call(
        phone_number=lead.phone,
        customer_name=lead.name,
        server_url=f"{SERVER_URL}/api/webhook" 
    )
    
    return {
        "status": "success",
        "message": "Registration complete. Call initiated.",
        "call_result": call_result
    }

@app.post("/api/webhook")
async def vapi_webhook(request: Request):
    """
    VapiからのWebhook（Tool Calls, Transcript, Status Updates）を処理する
    """
    payload = await request.json()
    message = payload.get("message", {})
    message_type = message.get("type")

    print(f"Received Webhook: {message_type}")

    if message_type == "tool-calls":
        tool_calls = message.get("toolCalls", [])
        results = []

        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            name = function.get("name")
            arguments = function.get("arguments", {})
            call_id = tool_call.get("id")
            
            result_content = ""

            print(f"Executing Tool: {name} with args: {arguments}")

            if name == "bookAppointment":
                start_time = arguments.get("startTime")
                customer_email = arguments.get("customerEmail")
                
                # Google Calendar予約
                event_result = calendar_service.create_event(
                    start_time_iso=start_time,
                    attendee_email=customer_email
                )
                
                if event_result["status"] == "success":
                    meet_link = event_result.get("hangoutLink", "リンク発行エラー")
                    result_content = f"予約が完了しました。Meetリンクは {meet_link} です。"
                    
                    # 予約成功時にSMSも送る（オプション）
                    # 電話番号が引数にない場合は、Vapiのcallオブジェクトから取得する必要があるが、
                    # ここでは簡略化のため、もしargumentsにphoneNumberがあれば送る、なければスキップ
                    # あるいは、Vapiのpayload.call.customer.number から取れる
                    customer_phone = payload.get("call", {}).get("customer", {}).get("number")
                    if customer_phone:
                        sms_msg = f"【Zoom/Meet予約確定】\n日時: {start_time}\nリンク: {meet_link}"
                        twilio_service.send_sms(customer_phone, sms_msg)
                        result_content += " SMSでリンクを送信しました。"
                else:
                    result_content = f"予約に失敗しました: {event_result.get('message')}"

            elif name == "sendSmsInfo":
                phone_number = arguments.get("phoneNumber")
                content = arguments.get("content")
                sms_result = twilio_service.send_sms(phone_number, content)
                
                if sms_result["status"] == "success":
                    result_content = "SMSを送信しました。"
                else:
                    result_content = f"SMS送信に失敗しました: {sms_result.get('message')}"
            
            else:
                result_content = "未定義のツールです。"

            results.append({
                "toolCallId": call_id,
                "result": result_content
            })

        # Vapiに結果を返す
        return {"results": results}

    elif message_type == "transcript":
        # 会話ログの保存などをここで行う
        pass

    return {"status": "ok"}

@app.get("/")
async def read_index():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Welcome to AI Tele-Appointment API. static/index.html not found."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
