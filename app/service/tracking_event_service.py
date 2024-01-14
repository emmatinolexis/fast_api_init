from datetime import datetime

from app.core.logger import get_logger
from app.repository.tracking_event_repository import TrackingEventRepository
from app.service.base_service import BaseService

log = get_logger()


class TrackingEventService(BaseService):
    def __init__(
        self,
        tracking_event_repository: TrackingEventRepository,
    ):
        self.tracking_event_repository = tracking_event_repository
        super().__init__(tracking_event_repository)

    def get_events_by_device_imei(self, device_imei: str, date: str, limit: int):
        try:
            if not date:
                date = datetime.now().strftime("%d/%m/%Y")

            events = self.tracking_event_repository.read_all_events_by_device_imei(
                device_imei, date, limit
            )
            if events is None:
                return []
            log.info(f"Number of events retrieved: {len(events)}")

            response = {"uuid": events[0].device_uuid, "date": str(date), "events": []}
            prev_end_time = None
            for event in events:
                period = (
                    generateTimeRange(prev_end_time, event.event_datetime)
                    if prev_end_time
                    else generateTimeRange(end=event.event_datetime)
                )
                response["events"].append(
                    {
                        "status": get_status(event.event_type),
                        "period": period,
                    }
                )
                prev_end_time = event.event_datetime
            return response
        except Exception as e:
            raise e

    def get_route_replay_events_by_device_imei(self, device_imei: str):
        try:
            return self.tracking_event_repository.read_all_route_replay_events_by_device_imei(
                device_imei
            )

        except Exception as e:
            raise e


def get_status(status: str):
    if status == "Start_Moving":
        return "moving"
    elif status == "Stop_Moving":
        return "stopped"
    elif status == "Idling_Alarm":
        return "idle"
    elif status == "Ignition_Off":
        return "stopped"
    else:
        return "unknown"


def generateTimeRange(start=None, end=None):
    start = start.strftime("%H:%M") if start else "0"
    end = end.strftime("%H:%M") if end else "0"
    if end == start:
        end = "0"
    return {
        "start": start,
        "end": end,
    }
