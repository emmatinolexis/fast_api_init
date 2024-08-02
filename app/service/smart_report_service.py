from collections import defaultdict
from datetime import datetime, timedelta

from app.repository.asset_repository import AssetRepository
from app.repository.equipment_repository import EquipmentRepository
from app.repository.smart_report_repository import SmartReportRepository
from app.repository.tracking_event_repository import TrackingEventRepository
from app.service.base_service import BaseService
from app.util.enums import GeofenceTypeUuid
from app.util.utils import (
    calculate_time_traveled,
    calculate_total_fuel_used,
    calculate_total_idle_time_and_movement,
    get_distance_travelled_by_coordinates,
    get_status,
)


class SmartReportService(BaseService):
    def __init__(
        self,
        smart_report_repository: SmartReportRepository,
        asset_repository: AssetRepository,
        tracking_event_repository: TrackingEventRepository,
        equipment_repository: EquipmentRepository,
    ):
        self.smart_report_repository = smart_report_repository
        self.asset_repository = asset_repository
        self.tracking_event_repository = tracking_event_repository
        self.equipment_repository = equipment_repository
        super().__init__(smart_report_repository)

    def get_reports(
        self,
        user_uuid: str = None,
        business_profile_uuid: str = None,
        page=1,
        page_size=10,
    ):
        try:
            return self.smart_report_repository.read_all_reports(
                user_uuid=user_uuid,
                business_uuid=business_profile_uuid,
                page=page,
                page_size=page_size,
            )
        except Exception as e:
            raise e

    def generate_total_distance_report(
        self,
        date_from: str,
        date_to: str,
        asset_uuids: list,
    ):
        try:
            assets = []
            for asset_uuid in asset_uuids:
                asset = self.asset_repository.get_asset_with_relationships(
                    asset_uuid, date_from, date_to
                )

                assets.append(asset)

            (
                total_distance_traveled_current_range,
                total_distance_traveled_past_range,
                fuel_level_current_range,
                fuel_level_past_range,
            ) = self.calculate_total_distance(assets, date_from, date_to)

            report = {
                "total_distance_covered_current_date": round(
                    total_distance_traveled_current_range, 2
                ),
                "total_distance_covered_previous_date": round(
                    total_distance_traveled_past_range, 2
                ),
                "total_fuel_recorded_current_date": fuel_level_current_range,
                "total_fuel_recorded_previous_date": fuel_level_past_range,
                "total_fuel_saved": fuel_level_past_range - fuel_level_current_range,
            }

            return report

        except Exception as e:
            raise e

    def parse_dates(self, date_from, date_to):
        date_from_dt = datetime.strptime(date_from, "%d/%m/%Y")
        date_to_dt = datetime.strptime(date_to, "%d/%m/%Y")
        months = [
            (date_from_dt + timedelta(days=x)).strftime("%B")
            for x in range((date_to_dt - date_from_dt).days + 1)
        ]
        unique_months = sorted(set(months), key=lambda x: datetime.strptime(x, "%B"))
        return date_from_dt, date_to_dt, unique_months

    def retrieve_assets(self, asset_uuids, date_from, date_to):
        assets = []
        for asset_uuid in asset_uuids:
            asset = self.asset_repository.get_asset_with_relationships(
                asset_uuid, date_from, date_to
            )
            assets.append(asset)
        return assets

    def group_events_by_month(self, asset):
        monthly_events = defaultdict(list)
        if asset.tracking_events:
            for event in asset.tracking_events:
                event_time = datetime.strptime(
                    event.get("timestamp"), "%Y-%m-%d %H:%M:%S"
                )
                event_month = event_time.strftime("%B")
                monthly_events[event_month].append(event)
        return monthly_events

    def calculate_times(self, events):
        if events:
            moving_time = calculate_time_traveled(events)
            idling_time = calculate_total_idle_time_and_movement(events)
            return moving_time, idling_time.get("total_idle_time", 0)
        return 0, 0

    def generate_report(
        self,
        assets,
        grouped_assets,
        good_asset_count,
        poor_asset_count,
        monthly_utilization,
    ):
        for equipment_name, times in grouped_assets.items():
            total_time = times["moving_time"] + times["idling_time"]
            if total_time > 0:
                times["moving_time_percentage"] = round(
                    (times["moving_time"] / total_time) * 100, 2
                )
                times["idling_time_percentage"] = round(
                    (times["idling_time"] / total_time) * 100, 2
                )
            else:
                times["moving_time_percentage"] = 0
                times["idling_time_percentage"] = 0

        report = {
            "fleet": {
                "total_asset": len(assets),
                "good_assets": good_asset_count,
                "poor_assets": poor_asset_count,
            },
            "utilization_rate": grouped_assets,
            "utilization_trend": monthly_utilization,
        }
        return report

    def generate_smart_report_fleet_overview(
        self,
        date_from: str,
        date_to: str,
        asset_type_uuid: str,
        asset_uuids: list,
        user_uuid: str = None,
        business_uuid: str = None,
    ):
        try:
            good_asset_count = 0
            poor_asset_count = 0

            date_from_dt, date_to_dt, unique_months = self.parse_dates(
                date_from, date_to
            )
            monthly_utilization = {
                month: {"moving_time": 0, "idle_time": 0} for month in unique_months
            }

            assets = self.retrieve_assets(asset_uuids, date_from, date_to)
            grouped_assets = {}

            for asset in assets:
                asset_violation = self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    date_from,
                    date_to,
                    business_uuid=business_uuid,
                    asset_uuid=asset.uuid,
                    asset_type_uuid=asset_type_uuid,
                    user_uuid=user_uuid,
                )
                if asset_violation:
                    poor_asset_count += 1
                else:
                    good_asset_count += 1

                equipment_name = asset.equipment.name
                if equipment_name not in grouped_assets:
                    grouped_assets[equipment_name] = {
                        "moving_time": 0,
                        "idling_time": 0,
                    }

                monthly_events = self.group_events_by_month(asset)

                for month, events in monthly_events.items():
                    moving_time, idle_time = self.calculate_times(events)
                    monthly_utilization[month]["moving_time"] += moving_time
                    monthly_utilization[month]["idle_time"] += idle_time

                overall_moving_time, overall_idle_time = self.calculate_times(
                    asset.tracking_events
                )
                grouped_assets[equipment_name]["moving_time"] += overall_moving_time
                grouped_assets[equipment_name]["idling_time"] += overall_idle_time

            report = self.generate_report(
                assets,
                grouped_assets,
                good_asset_count,
                poor_asset_count,
                monthly_utilization,
            )
            return report

        except Exception as e:
            raise e

    def calculate_total_distance(self, assets, start_date, end_date):
        total_distance_traveled_current_range = 0
        total_distance_traveled_past_range = 0
        fuel_level_current_range = 0
        fuel_level_past_range = 0

        for asset in assets:
            if asset.device_imei:
                # Get asset points for the specified date range
                asset_events = (
                    self.tracking_event_repository.read_all_events_by_date_range(
                        asset.device_imei, start_date, end_date
                    )
                )

                # Extract coordinates from asset events
                current_range_events = [
                    {
                        "latitude": event.latitude,
                        "longitude": event.longitude,
                        "speed": event.speed,
                        "timestamp": str(event.event_datetime),
                        "event_type": get_status(event.event_type),
                        "fuel_level": event.fuel_level,
                    }
                    for event in asset_events.get("current_range_events")
                ]

                past_range_events = [
                    {
                        "latitude": event.latitude,
                        "longitude": event.longitude,
                        "speed": event.speed,
                        "timestamp": str(event.event_datetime),
                        "event_type": get_status(event.event_type),
                        "fuel_level": event.fuel_level,
                    }
                    for event in asset_events.get("past_range_events")
                ]

                # Calculate distance traveled
                current_distance = get_distance_travelled_by_coordinates(
                    current_range_events
                )
                past_distance = get_distance_travelled_by_coordinates(past_range_events)

                current_fuel_level = calculate_total_fuel_used(current_range_events)
                past_fuel_level = calculate_total_fuel_used(past_range_events)

                total_distance_traveled_current_range += current_distance
                total_distance_traveled_past_range += past_distance
                fuel_level_past_range += past_fuel_level
                fuel_level_current_range += current_fuel_level

        return (
            total_distance_traveled_current_range,
            total_distance_traveled_past_range,
            fuel_level_current_range,
            fuel_level_past_range,
        )
