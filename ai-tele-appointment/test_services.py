import pytest
from services.twilio_service import TwilioService
from services.google_calendar import GoogleCalendarService
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_twilio_mock():
    service = TwilioService()
    # 認証情報がない場合はモックが動くはず
    result = service.send_sms("09012345678", "Test Message")
    assert result["status"] == "success"
    assert "mock" in str(result) or "sid" in result

def test_calendar_mock():
    service = GoogleCalendarService()
    # 認証情報がない場合はモックが動くはず
    result = service.create_event("2026-01-23T10:00:00+09:00", attendee_email="test@example.com")
    assert result["status"] == "success"
    assert "mock" in result["htmlLink"]

def test_webhook_book_appointment():
    # Vapiからのツール呼び出しリクエストをシミュレート
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCalls": [
                {
                    "id": "call_123",
                    "function": {
                        "name": "bookAppointment",
                        "arguments": {
                            "startTime": "2026-01-23T10:00:00+09:00",
                            "customerEmail": "test@example.com"
                        }
                    }
                }
            ]
        },
        "call": {
            "customer": {
                "number": "09012345678"
            }
        }
    }
    
    response = client.post("/api/webhook", json=payload)
    assert response.status_code == 200
    json_resp = response.json()
    
    assert "results" in json_resp
    assert len(json_resp["results"]) == 1
    result = json_resp["results"][0]
    assert result["toolCallId"] == "call_123"
    assert "予約が完了しました" in result["result"]
    # モック環境ではSMSも送信されるログが出るはず（標準出力確認）

def test_webhook_unknown_tool():
    payload = {
        "message": {
            "type": "tool-calls",
            "toolCalls": [
                {
                    "id": "call_999",
                    "function": {
                        "name": "unknownTool",
                        "arguments": {}
                    }
                }
            ]
        }
    }
    
    response = client.post("/api/webhook", json=payload)
    assert response.status_code == 200
    json_resp = response.json()
    assert "未定義" in json_resp["results"][0]["result"]
