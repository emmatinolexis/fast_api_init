from app.core.container import Container
from app.core.logger import get_logger

log = get_logger()


async def send_sms(
    recipient: str,
    message: str,
):
    try:
        return "send sms"
    except Exception as e:
        log.error(f"Failed to send SMS to [{recipient}]")
        raise Exception(str(e))
