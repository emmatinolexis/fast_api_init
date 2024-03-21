import os

# from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
from typing import Dict

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

SMTP_SERVER = "live.smtp.mailtrap.io"
SMTP_PORT = 587
SMTP_USERNAME = "api"
SMTP_PASSWORD = "9133d6b20cae5592a71b2c1246c9e8e9"
SMTP_FROM = "MVI Tracking <info@sagemicrosystems.net>"


def read_email_template() -> str:
    current_directory = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(
        current_directory, "..", "templates", "email-template.html"
    )

    with open(template_path, "r") as file:
        return file.read()


def get_email_config() -> ConnectionConfig:
    templates_dir = Path(__file__).parent.parent / "templates"

    return ConnectionConfig(
        MAIL_USERNAME=SMTP_USERNAME,
        MAIL_PASSWORD=SMTP_PASSWORD,
        MAIL_FROM=SMTP_FROM,
        MAIL_PORT=SMTP_PORT,
        MAIL_SERVER=SMTP_SERVER,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        TEMPLATE_FOLDER=templates_dir,
        USE_CREDENTIALS=True,
    )


async def send_email(
    subject,
    recipient_name,
    email,
    message,
    url,
    btn,
    token="",
) -> Dict[str, str]:
    try:
        msg = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body={
                "message": message,
                "recipient_name": recipient_name,
                "verify_token": token,
                "url": url,
                "btn": btn,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(config=get_email_config())
        await fm.send_message(msg, template_name="email-template.html")

    except Exception as e:
        raise Exception(str(e))


async def send_email_invitation(
    subject,
    recipient_name,
    email,
    invitee_name,
):
    try:
        msg = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body={
                "recipient_name": recipient_name,
                "invitee_name": invitee_name,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(config=get_email_config())
        await fm.send_message(msg, template_name="invitation-email-template.html")

    except Exception as e:
        raise Exception(str(e))


async def send_otp_email(
    subject,
    recipient_name,
    email,
    otp,
):
    try:
        msg = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body={
                "recipient_name": recipient_name,
                "otp": otp,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(config=get_email_config())
        await fm.send_message(msg, template_name="otp-email-template.html")

    except Exception as e:
        raise Exception(str(e))


async def send_alert_policy_violation_email(
    subject,
    recipient_name,
    email,
    asset_name,
    policy_name,
):
    try:
        msg = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body={
                "recipient_name": recipient_name,
                "asset_name": asset_name,
                "policy_name": policy_name,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(config=get_email_config())
        await fm.send_message(msg, template_name="alert-violation-template.html")
    except Exception as e:
        raise Exception(str(e))
