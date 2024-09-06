from datetime import datetime
from typing import Any, Dict, List, Union

from app.core.constants import DISTANCE_UNIT, SPEED_UNIT
from app.core.logger import get_logger
from app.repository.tracking_event_repository import TrackingEventRepository
from app.service.base_service import BaseService
from app.util.utils import get_distance_travelled_by_coordinates, get_status

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

            if not events:
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

    def get_events_by_user(
        self, date: str, user_uuid: str = None, business_uuid: str = None
    ) -> List[Dict[str, Any]]:
        try:
            date = self._initialize_date(date)
            device_events = self._fetch_device_events(date, user_uuid, business_uuid)

            if device_events is None:
                return []

            return self._build_response(date, device_events)
        except Exception as e:
            raise e

    def _initialize_date(self, date: str) -> str:
        if not date:
            date = datetime.now().strftime("%d/%m/%Y")
        return date

    def _fetch_device_events(
        self, date: str, user_uuid: str, business_uuid: str
    ) -> Union[Dict[str, Any], None]:
        if user_uuid:
            return self.tracking_event_repository.read_all_events_by_user(
                date=date, user_uuid=user_uuid
            )
        if business_uuid:
            return self.tracking_event_repository.read_all_events_by_user(
                date=date, business_uuid=business_uuid
            )
        return None

    def _build_response(
        self, date: str, device_events: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        response = []
        for device_imei, data in device_events.items():
            device_response = self._process_device_events(device_imei, data, date)
            response.append(device_response)
        return response

    def _process_device_events(
        self, device_imei: str, data: Dict[str, Any], date: str
    ) -> Dict[str, Any]:
        events = data["events"]
        asset = data["asset"]

        device_response = {
            "device_imei": device_imei,
            "asset_name": asset.asset_name,
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

        return device_response

    # Dummy implementations for missing functions to avoid reference errors
    def get_status(event_type):
        return "status_placeholder"

    def generateTimeRange(start_time, end_time):
        return f"{start_time} - {end_time}"

    def get_route_replay_events_by_device_imei(self, device_imei: str, date: str):
        try:
            if not date:
                date = datetime.now().strftime("%d/%m/%Y")
            return self.tracking_event_repository.read_all_route_replay_events_by_device_imei(
                device_imei, date
            )
        except Exception as e:
            raise e

    def get_latest_tracking_event_by_device_imei(self, device_imei: str):
        try:
            return self.tracking_event_repository.read_latest_tracking_event_by_device_imei(
                device_imei
            )
        except Exception as e:
            raise e

    def get_events_by_device_imei_by_date(self, device_imei: str, date: str):
        try:
            if not date:
                date = datetime.now().strftime("%d/%m/%Y")
            return self.tracking_event_repository.read_all_events_by_device_imei(
                device_imei, date
            )
        except Exception as e:
            raise e

    def get_distance_travelled_by_device_imei(self, device_imei: str, date: str):
        events = self.get_events_by_device_imei_by_date(device_imei, date)

        if not events:
            return f"0 {DISTANCE_UNIT}"

        coordinates = []

        for event in events:
            coordinates.append(
                {"latitude": event.latitude, "longitude": event.longitude, "timestamp":event.event_datetime}
            )
        distance_travelled = get_distance_travelled_by_coordinates(coordinates)

        return f"{distance_travelled} {DISTANCE_UNIT}"

    def get_device_analytics(self, device_imei: str, date: str):
        try:
            latest_tracking_event = self.get_latest_tracking_event_by_device_imei(
                device_imei
            )

            distance_travelled = self.get_distance_travelled_by_device_imei(
                device_imei, date
            )

            return {
                "status": get_status(latest_tracking_event.event_type),
                "current_location": {
                    "latitude": latest_tracking_event.latitude,
                    "longitude": latest_tracking_event.longitude,
                },
                "current_speed": f"{latest_tracking_event.speed}{SPEED_UNIT}",
                "distance_travelled": distance_travelled,
            }
        except Exception as e:
            raise e

    def get_asset_average_speed(
        self, device_imei: str, date_from: datetime, date_to: datetime
    ):
        try:
            return self.tracking_event_repository.read_asset_average_speed(
                device_imei, date_from, date_to
            )
        except Exception as e:
            raise e


def generateTimeRange(start=None, end=None):
    start = start.strftime("%H:%M") if start else "0"
    end = end.strftime("%H:%M") if end else "0"
    # if end == start:
    #     end = "0"
    return f"{start} to {end}"
