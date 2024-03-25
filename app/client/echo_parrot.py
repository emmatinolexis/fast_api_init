import httpx

from app.util.enums import EmailPurpose


class EchoParrot:
    def __init__(self, host, port, sender_id, sender_app, sender_email, sender_name):
        self.host = host
        self.port = port
        self.sender_id = sender_id
        self.sender_app = sender_app
        self.sender_email = sender_email
        self.sender_name = sender_name

    # echo sms message via echo parrot to recipient
    async def echo_sms(self, message, recipient):
        response = httpx.post(
            f"http://{self.host}:{self.port}/api/v1/sms",
            data={
                "message": message,
                "recipient": recipient,
                "sender_id": self.sender_id,
                "sender_app": self.sender_app,
            },
            headers={"Content-Type": "application/json"},
        )
        return response.json()

    async def echo_email(
        self, recipient_email, email_purpose: EmailPurpose, email_body
    ):
        response = httpx.post(
            f"http://{self.host}:{self.port}/api/v1/email",
            data={
                "recipient_email": recipient_email,
                "sender_email": self.sender_email,
                "sender_name": self.sender_name,
                "email_purpose": email_purpose,
                "body": email_body,
                "sender_app": self.sender_app,
            },
            headers={"Content-Type": "application/json"},
        )
        return response.json()
