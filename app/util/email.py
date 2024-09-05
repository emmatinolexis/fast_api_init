from structlog import get_logger

from app.core.container import Container
from app.util.enums import EmailPurpose

log = get_logger()


async def send_email(
    email_purpose,
    email_body,
    email,
):
    try:
        echo_parrot = Container().echo_parrot()
        response = await echo_parrot.echo_email(
            recipient_email=email,
            email_purpose=email_purpose,
            email_body=email_body,
        )
        return response

    except Exception as e:
        raise Exception(str(e))


async def send_email_verification(
    recipient_name,
    email,
    message,
    url,
    btn,
    token="",
    email_purpose=EmailPurpose.EMAIL_VERIFICATION,
):
    try:
        response = await send_email(
            email_purpose=email_purpose,
            email_body={
                "recipient_name": recipient_name,
                "message": message,
                "verify_token": token,
                "url": url,
                "btn": btn,
            },
            email=email,
        )
        if response["data"]["status"] == "success":
            log.info(f"Verification email [{email}] sent successfully")
            return

        log.error(f"Failed to send verification email [{email}]")
    except Exception as e:
        log.error(f"Failed to send verification email [{email}]")
        raise Exception(str(e))


async def send_smart_report_email(
    email,
    message,
    title,
    btn_url,
    btn_text="",
    email_purpose=EmailPurpose.SMART_REPORT_ALERT,
):
    try:
        response = await send_email(
            email_purpose=email_purpose,
            email_body={
                "message": message,
                "title": title,
                "btn_url": btn_url,
                "btn_text": btn_text,
            },
            email=email,
        )
        if response["data"]["status"] == "success":
            log.info("Smart report notification sent successfully")
            return

        log.error(f"Failed smart report notification email [{email}]")
    except Exception as e:
        log.error(f"Failed to smart report notification email [{email}]")
        raise Exception(str(e))


async def send_email_invitation(
    recipient_name, email, invitee_name, business_profile_uuid, role, expiry_date
):
    try:
        response = await send_email(
            email_purpose=EmailPurpose.INVITATION,
            email_body={
                "recipient_name": recipient_name,
                "invitee_name": invitee_name,
                "business_profile_uuid": business_profile_uuid,
                "email": email,
                "role": role,
                "expiry_date": expiry_date,
            },
            email=email,
        )
        if response["data"]["status"] == "success":
            log.info(f"Invitation email [{email}] sent successfully")
            return

        log.error(f"Failed to send invitation email [{email}]")
    except Exception as e:
        log.error(f"Failed to send invitation email [{email}]")
        raise Exception(str(e))


async def send_otp_email(
    recipient_name,
    email,
    otp,
):
    try:
        response = await send_email(
            email_purpose=EmailPurpose.EMAIL_OTP,
            email_body={
                "recipient_name": recipient_name,
                "otp": otp,
            },
            email=email,
        )
        if response["data"]["status"] == "success":
            log.info(f"OTP email [{email}] sent successfully")
            return

        log.error(f"Failed to send OTP email [{email}]")
    except Exception as e:
        log.error(f"Failed to send OTP email [{email}]")
        raise Exception(str(e))


async def send_alert_policy_violation_email(
    recipient_name,
    email,
    asset_name,
    policy_name,
):
    try:
        response = await send_email(
            email_purpose=EmailPurpose.ALERT_VIOLATION,
            email_body={
                "recipient_name": recipient_name,
                "asset_name": asset_name,
                "policy_name": policy_name,
            },
            email=email,
        )
        if response["data"]["status"] == "success":
            log.info(f"Alert policy violation email [{email}] sent successfully")
            return
        log.error(f"Failed to send alert policy violation email [{email}]")
    except Exception as e:
        log.error(f"Failed to send alert policy violation email [{email}]")
        raise Exception(str(e))


async def send_maintenance_alert_email(
    recipient_name,
    email,
    asset_name,
    policy_name,
):
    try:
        response = await send_email(
            email_purpose=EmailPurpose.MAINTENANCE_ALERT,
            email_body={
                "recipient_name": recipient_name,
                "asset_name": asset_name,
                "policy_name": policy_name,
            },
            email=email,
        )
        if response["data"]["status"] == "success":
            log.info(f"Alert policy violation email [{email}] sent successfully")
            return
        log.error(f"Failed to send alert policy violation email [{email}]")
    except Exception as e:
        log.error(f"Failed to send alert policy violation email [{email}]")
        raise Exception(str(e))


async def send_password_change_email(
    recipient_name, email, ip_address, user_agent, time_stamp
):
    try:
        response = await send_email(
            email_purpose=EmailPurpose.PASSWORD_CHANGE,
            email_body={
                "recipient_name": recipient_name,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "time_stamp": time_stamp,
            },
            email=email,
        )
        if response["data"]["status"] == "success":
            log.info(f"Password change email [{email}] sent successfully")
            return
        log.error(f"Failed to send password change email [{email}]")
    except Exception as e:
        log.error(f"Failed to send password change email [{email}]")
        raise Exception(str(e))
