import os
from twilio.rest import Client
from typing import Optional

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("Warning: Twilio credentials not set. SMS sending will be mocked.")

    def send_sms(self, to_number: str, message: str) -> dict:
        """
        SMSを送信する
        """
        if not self.client:
            print(f"[Mock] Sending SMS to {to_number}: {message}")
            return {"status": "success", "sid": "mock_sid"}

        try:
            message_instance = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            return {"status": "success", "sid": message_instance.sid}
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return {"status": "error", "message": str(e)}
