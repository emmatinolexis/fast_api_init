from collections import defaultdict
from typing import Optional

from app.repository.gas_cylinder_event_repository import GasCylinderEventRepository
from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.repository.gas_cylinder_type_repository import GasCylinderTypeRepository
from app.service.base_service import BaseService
from app.util.utils import calculate_gas_level_percentage


class GasCylinderEventService(BaseService):
    def __init__(
        self,
        gas_cylinder_event_repository: GasCylinderEventRepository,
        gas_cylinder_repository: GasCylinderRepository,
        gas_cylinder_type_repository: GasCylinderTypeRepository,
    ):
        self.gas_cylinder_event_repository = gas_cylinder_event_repository
        self.gas_cylinder_repository = gas_cylinder_repository
        self.gas_cylinder_type_repository = gas_cylinder_type_repository
        super().__init__(gas_cylinder_event_repository)

    def query_between_dates(
        self, device_serial_number: str, start_date: str, end_date: str
    ):
        return self.gas_cylinder_event_repository.read_all_gas_events_by_date_range(
            device_serial_number=device_serial_number,
            start_date=start_date,
            end_date=end_date,
        )

    def generate_report(
        self,
        user_uuid: str,
        start_date: str,
        end_date: str,
        search: Optional[str] = None,
    ):
        # Read all cylinders associated with the user
        user_cylinders = self.gas_cylinder_repository.read_all_by_user_uuid(user_uuid)

        if search:
            user_cylinders = [
                cylinder
                for cylinder in user_cylinders
                if search.lower() in cylinder.cylinder_name.lower()
            ]

        if not user_cylinders:
            return []

        # Filter out cylinders with None as gas_device_serial_number
        cylinders_with_serial_numbers = [
            cylinder
            for cylinder in user_cylinders
            if cylinder.gas_device_serial_number is not None
        ]

        if not cylinders_with_serial_numbers:
            return []

        # Initialize the result list
        all_devices_daily_usage = []

        # Iterate over each device
        for cylinder in cylinders_with_serial_numbers:
            device_serial_number = cylinder.gas_device_serial_number
            device_name = (
                cylinder.cylinder_name
            )  # Assuming device_name is an attribute of the cylinder

            # Query events between the specified dates
            events = self.query_between_dates(
                device_serial_number=device_serial_number,
                start_date=start_date,
                end_date=end_date,
            )

            # Arrange events by datetime in ascending order
            events.sort(key=lambda x: x.event_timestamp)

            # Group events by date
            daily_events = defaultdict(list)
            for event in events:
                date_str = event.event_timestamp.date().isoformat()
                daily_events[date_str].append(event)

            # Calculate daily usage
            daily_usage = []
            for date_str, events in daily_events.items():
                if len(events) >= 2:
                    first_event = events[0]
                    last_event = events[-1]
                    usage = last_event.current_weight - first_event.current_weight
                    daily_usage.append(
                        {
                            "date": date_str,
                            "usage": int(usage),  # Round to 1 decimal place
                        }
                    )

            # Query the current weight of the device
            current_weight = events[-1].current_weight if events else None

            # Retrieve the cylinder type details
            cylinder_type_uuid = cylinder.cylinder_type_uuid
            if cylinder_type_uuid:
                cylinder_type = self.gas_cylinder_type_repository.read_by_uuid(
                    cylinder_type_uuid
                )
                empty_weight = cylinder_type.empty_weight
                full_weight = cylinder_type.full_weight

                # Calculate gas level percentage
                gas_percentage = (
                    calculate_gas_level_percentage(
                        empty_weight, full_weight, current_weight
                    )
                    if current_weight is not None
                    else None
                )

                if gas_percentage is not None:
                    gas_percentage = abs(
                        int(gas_percentage)
                    )  # Convert to positive integer
            else:
                gas_percentage = 0

            # Add the device data to the result list
            all_devices_daily_usage.append(
                {
                    "name": device_name,
                    "daily_usage": daily_usage,
                    "current_gas_percentage": gas_percentage,
                }
            )

        return all_devices_daily_usage

    def generate_report_business(
        self,
        business_uuid: str,
        start_date: str,
        end_date: str,
        search: Optional[str] = None,
    ):
        # Read all cylinders associated with the business
        business_cylinders = self.gas_cylinder_repository.read_all_by_business_uuid(
            business_uuid
        )

        if search:
            business_cylinders = [
                cylinder
                for cylinder in business_cylinders
                if search.lower() in cylinder.cylinder_name.lower()
            ]

        if not business_cylinders:
            return []

        # Filter out cylinders with None as gas_device_serial_number
        cylinders_with_serial_numbers = [
            cylinder
            for cylinder in business_cylinders
            if cylinder.gas_device_serial_number is not None
        ]

        if not cylinders_with_serial_numbers:
            return []

        # Initialize the result list
        all_devices_daily_usage = []

        # Iterate over each device
        for cylinder in cylinders_with_serial_numbers:
            device_serial_number = cylinder.gas_device_serial_number
            device_name = cylinder.cylinder_name

            # Query events between the specified dates
            events = self.query_between_dates(
                device_serial_number=device_serial_number,
                start_date=start_date,
                end_date=end_date,
            )

            # Arrange events by datetime in ascending order
            events.sort(key=lambda x: x.event_timestamp)

            # Group events by date
            daily_events = defaultdict(list)
            for event in events:
                date_str = event.event_timestamp.date().isoformat()
                daily_events[date_str].append(event)

            # Calculate daily usage
            daily_usage = []
            for date_str, events in daily_events.items():
                if len(events) >= 2:
                    first_event = events[0]
                    last_event = events[-1]
                    usage = last_event.current_weight - first_event.current_weight
                    daily_usage.append({"date": date_str, "usage": int(usage)})

            # Query the current weight of the device
            current_weight = events[-1].current_weight if events else None

            # Retrieve the cylinder type details
            cylinder_type_uuid = cylinder.cylinder_type_uuid
            if cylinder_type_uuid:
                cylinder_type = self.gas_cylinder_type_repository.read_by_uuid(
                    cylinder_type_uuid
                )
                empty_weight = cylinder_type.empty_weight
                full_weight = cylinder_type.full_weight

                # Calculate gas level percentage
                gas_percentage = (
                    calculate_gas_level_percentage(
                        empty_weight, full_weight, current_weight
                    )
                    if current_weight is not None
                    else None
                )

                if gas_percentage is not None:
                    gas_percentage = abs(
                        int(gas_percentage)
                    )  # Convert to positive integer
            else:
                gas_percentage = 0

            # Add the device data to the result list
            all_devices_daily_usage.append(
                {
                    "name": device_name,
                    "daily_usage": daily_usage,
                    "current_gas_percentage": gas_percentage,
                }
            )

        return all_devices_daily_usage
