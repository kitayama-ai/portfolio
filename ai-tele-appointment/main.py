from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from vapi_client import VapiClient

# 環境変数の読み込み
load_dotenv()

app = FastAPI(title="AI Tele-Appointment Backend")

# Vapiクライアントの初期化
vapi_client = VapiClient()

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
    
    # ここでDBへの保存処理などを行う（省略）
    
    # AIによる架電を開始 (Speed to Lead)
    call_result = vapi_client.make_call(
        phone_number=lead.phone,
        customer_name=lead.name
    )
    
    return {
        "status": "success",
        "message": "Registration complete. Call initiated.",
        "call_result": call_result
    }

# フロントエンドの提供（簡易的）
# 実際にはFrontendは別ホスティング（Vercelなど）が望ましいが、デモ用に同一サーバーで配信
@app.get("/")
async def read_index():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Welcome to AI Tele-Appointment API. static/index.html not found."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
