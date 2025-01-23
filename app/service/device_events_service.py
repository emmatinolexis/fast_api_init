from collections import defaultdict
from datetime import datetime, timedelta

from app.core.exceptions import NotFoundError
from app.core.messages import DEVICE_DOES_NOT_EXIST, GAS_CYLINDER_NOT_FOUND
from app.repository.device_events_repository import DeviceEventRepository
from app.service.base_service import BaseService
from app.util.utils import parse_date


class DeviceEventService(BaseService):
    def __init__(
        self,
        device_event_repository: DeviceEventRepository,
    ):
        self.device_event_repository = device_event_repository
        super().__init__(device_event_repository)

    def get_devices_latest_reading(self, node_id: str):
        try:
            devices = self.device_event_repository.get_device_latest_reading(node_id)
            return devices
        except Exception as e:
            raise e

    def __init__(
        self,
        device_event_repository: DeviceEventRepository,
    ):
        self.device_event_repository = device_event_repository
        super().__init__(device_event_repository)

    def get_devices_latest_reading(self, node_id: str):
        try:
            devices = self.device_event_repository.get_device_latest_reading(node_id)
            return devices
        except Exception as e:
            raise e

    def generate_report_single_cylinder(
        self, cylinder_uuid: str, start_date: str, end_date: str
    ):
        cylinder = self.device_event_repository.read_gas_cylinder_by_uuid(cylinder_uuid)

        if not cylinder:
            raise NotFoundError(detail=cylinder)

        gas_device_serial_number = cylinder.gas_device_serial_number
        if not gas_device_serial_number:
            raise NotFoundError(detail=gas_device_serial_number)
        device_name = cylinder.cylinder_name

        peripheral_device = (
            self.device_event_repository.get_peripheral_device_by_serial_number(
                gas_device_serial_number
            )
        )

        if not peripheral_device:
            return {
                "name": device_name,
                "daily_usage": [],
                "current_gas_value": None,
                "unit": None,
            }

        node_id = str(peripheral_device.node_id)

        try:
            start_date_parsed = parse_date(start_date)
            end_date_parsed = parse_date(end_date)
            start_date_obj = datetime.strptime(start_date_parsed, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date_parsed, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {str(e)}")

        start_date_obj = datetime.combine(start_date_obj.date(), datetime.min.time())
        end_date_obj = datetime.combine(end_date_obj.date(), datetime.max.time())

        events = self.device_event_repository.get_device_events_between_dates(
            node_id=node_id,
            start_date=start_date_obj,
            end_date=end_date_obj,
        )

        if not events:
            return {
                "name": device_name,
                "daily_usage": [],
                "current_gas_value": None,
                "unit": None,
            }

        daily_values = defaultdict(list)

        for event in events:
            created_at = event.created_at
            if not created_at:
                continue
            date_part = created_at.date().isoformat()

            measurements = event.measurements or []
            if measurements:
                measurement = measurements[0]
                value_str = measurement.get("value")
                try:
                    value = float(value_str)
                    daily_values[date_part].append(value)
                except (ValueError, TypeError):
                    continue
            else:
                continue

        daily_usage = []
        for date_str, values in daily_values.items():
            average_value = round(sum(values) / len(values), 2)
            daily_usage.append({"date": date_str, "average_value": average_value})

        daily_usage.sort(key=lambda x: x["date"])

        return {
            "name": device_name,
            "daily_usage": daily_usage,
        }
