import firebase_admin
from firebase_admin import credentials, messaging

from app.core.settings import settings
from app.util.utils import singleton


@singleton
class Firebase:
    def __init__(self):
        self.service_account_info = {
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": settings.FIREBASE_CLIENT_ID,
            "auth_uri": settings.FIREBASE_AUTH_URI,
            "token_uri": settings.FIREBASE_TOKEN_URI,
            "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
            "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
        }
        self.credential = credentials.Certificate(self.service_account_info)
        self.app = firebase_admin.initialize_app(self.credential)

    async def send_notification(
        self, token: str, title: str, body: str, deeplink_action: str
    ):
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
            data={"deeplink_action": deeplink_action},
        )
        try:
            response = messaging.send(message)
            return response
        except Exception as e:
            return str(e)
