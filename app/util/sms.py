from app.core import container
from app.core.logger import get_logger

log = get_logger()


async def send_sms(
    recipient: str,
    message: str,
):
    try:
        echo_parrot = container.echo_parrot()
        response = await echo_parrot.echo_sms(
            recipient=recipient,
            message=message,
        )
        if response["data"]["status"] == "success":
            log.info(f"SMS sent successfully to [{recipient}]")
            return
        log.error(f"Failed to send SMS to [{recipient}]")

    except Exception as e:
        log.error(f"Failed to send SMS to [{recipient}]")
        raise Exception(str(e))
