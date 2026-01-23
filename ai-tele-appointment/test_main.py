import pytest
from fastapi.testclient import TestClient
from main import app
from vapi_client import VapiClient
from unittest.mock import MagicMock

client = TestClient(app)

def test_read_index():
    response = client.get("/")
    assert response.status_code == 200
    # インデックスページが返ってくるか、もしくはファイルがない場合のメッセージ
    # 現在のmain.pyではstatic/index.htmlがあればそれを返す
    # テスト環境にstatic/index.htmlがある前提、もしくはモックする

def test_register_lead_success():
    # VapiClientをモック化する
    # 実際にはmain.py内のvapi_clientインスタンスを差し替えるのが難しい場合があるため
    # 依存性注入を使うか、あるいはpatchを使うのが一般的だが、
    # ここでは簡易的に、APIキーがなくてもmock_successが返ることを利用してテストする。
    
    # 正常なペイロード
    payload = {
        "name": "Test User",
        "phone": "09012345678",
        "email": "test@example.com"
    }
    
    response = client.post("/api/register", json=payload)
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    # モック動作の場合のメッセージ確認
    assert "mock_success" in json_response["call_result"]["status"]

def test_register_lead_invalid_phone():
    # バリデーションエラー（電話番号なし）
    payload = {
        "name": "Test User",
        "email": "test@example.com"
    }
    
    response = client.post("/api/register", json=payload)
    
    assert response.status_code == 422  # Validation Error
