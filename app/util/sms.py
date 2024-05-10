from app.core.container import Container
from app.core.logger import get_logger

log = get_logger()


async def send_sms(
    recipient: str,
    message: str,
):
    try:
        echo_parrot = Container().echo_parrot()
        response = await echo_parrot.echo_sms(
            recipient=recipient,
            message=message,
        )
        if response["data"]["status"] == "success":
            log.info(f"SMS sent successfully to [{recipient}]")
            return True
        log.error(f"Failed to send SMS to [{recipient}]")
        return False
    except Exception as e:
        log.error(f"Failed to send SMS to [{recipient}]")
        raise Exception(str(e))
