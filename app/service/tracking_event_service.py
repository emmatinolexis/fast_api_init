from datetime import datetime
from typing import Dict

from app.core.logger import get_logger
from app.repository.tracking_event_repository import TrackingEventRepository
from app.service.base_service import BaseService
from app.util.utils import get_status

log = get_logger()


class TrackingEventService(BaseService):
    def __init__(
        self,
        tracking_event_repository: TrackingEventRepository,
    ):
        self.tracking_event_repository = tracking_event_repository
        super().__init__(tracking_event_repository)

    def get_events_by_device_imei(self, device_imei: str, date: str):
        try:
            if not date:
                date = datetime.now().strftime("%d/%m/%Y")

            events = self.tracking_event_repository.read_all_events_by_device_imei(
                device_imei, date
            )
            if events is None:
                return []

            response = {"uuid": events[0].device_uuid, "date": str(date), "events": []}

            current_event = None
            for event in events:
                if current_event is None:
                    current_event = {
                        "status": get_status(event.event_type),
                        "start_time": event.event_datetime,
                        "end_time": event.event_datetime,
                    }
                else:
                    if current_event["status"] == get_status(event.event_type):
                        current_event["end_time"] = event.event_datetime
                    else:
                        response["events"].append(
                            {
                                "status": current_event["status"],
                                "period": generateTimeRange(
                                    current_event["start_time"],
                                    current_event["end_time"],
                                ),
                            }
                        )
                        current_event = {
                            "status": get_status(event.event_type),
                            "start_time": event.event_datetime,
                            "end_time": event.event_datetime,
                        }
            # Append the last event
            if current_event is not None:
                response["events"].append(
                    {
                        "status": current_event["status"],
                        "period": generateTimeRange(
                            current_event["start_time"], current_event["end_time"]
                        ),
                    }
                )
            log.info(f"Number of events retrieved: {len(response['events'])}")
            return response
        except Exception as e:
            raise e

    def get_events_by_user(self, user_uuid: str, date: str) -> Dict[str, dict]:
        try:
            if not date:
                date = datetime.now().strftime("%d/%m/%Y")

            device_events = self.tracking_event_repository.read_all_events_by_user(
                user_uuid, date
            )

            if device_events is None:
                return {}

            response = {}

            for device_imei, events in device_events.items():
                device_response = {
                    "device_imei": device_imei,
                    "date": str(date),
                    "events": [],
                }

                current_event = None

                for event in events:
                    if current_event is None:
                        current_event = {
                            "status": get_status(event.event_type),
                            "start_time": event.event_datetime,
                            "end_time": event.event_datetime,
                        }
                    else:
                        if current_event["status"] == get_status(event.event_type):
                            current_event["end_time"] = event.event_datetime
                        else:
                            device_response["events"].append(
                                {
                                    "status": current_event["status"],
                                    "period": generateTimeRange(
                                        current_event["start_time"],
                                        current_event["end_time"],
                                    ),
                                }
                            )
                            current_event = {
                                "status": get_status(event.event_type),
                                "start_time": event.event_datetime,
                                "end_time": event.event_datetime,
                            }

                # Append the last event
                if current_event is not None:
                    device_response["events"].append(
                        {
                            "status": current_event["status"],
                            "period": generateTimeRange(
                                current_event["start_time"], current_event["end_time"]
                            ),
                        }
                    )

                response[device_imei] = device_response

            return response

        except Exception as e:
            raise e

    def get_route_replay_events_by_device_imei(self, device_imei: str, date: str):
        try:
            if not date:
                date = datetime.now().strftime("%d/%m/%Y")
            return self.tracking_event_repository.read_all_route_replay_events_by_device_imei(
                device_imei, date
            )
        except Exception as e:
            raise e


def generateTimeRange(start=None, end=None):
    start = start.strftime("%H:%M") if start else "0"
    end = end.strftime("%H:%M") if end else "0"
    # if end == start:
    #     end = "0"
    return f"{start} to {end}"
