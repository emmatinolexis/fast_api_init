from app.repository.asset_repository import AssetRepository
from app.repository.smart_report_repository import SmartReportRepository
from app.repository.tracking_event_repository import TrackingEventRepository
from app.service.base_service import BaseService
from app.util.enums import GeofenceTypeUuid
from app.util.utils import (  # calculate_average_speed,; calculate_time_traveled,; calculate_total_idle_time_and_movement,
    calculate_total_fuel_used,
    get_distance_travelled_by_coordinates,
    get_status,
)


class SmartReportService(BaseService):
    def __init__(
        self,
        smart_report_repository: SmartReportRepository,
        asset_repository: AssetRepository,
        tracking_event_repository: TrackingEventRepository,
    ):
        self.smart_report_repository = smart_report_repository
        self.asset_repository = asset_repository
        self.tracking_event_repository = tracking_event_repository
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
                business_uuid=business_profile_uuid,
                user_uuid=user_uuid,
                page_size=page_size,
                page=page,
            )
        except Exception as e:
            raise e

    def generate_smart_report(
        self,
        date_from: str,
        date_to: str,
        asset_type_uuid: str,
        asset_uuids: list,
        user_uuid: str = None,
        business_uuid: str = None,
    ):
        try:
            assets = []
            good_asset_count = 0
            poor_asset_count = 0

            for asset_uuid in asset_uuids:
                asset = self.asset_repository.read_by_uuid(asset_uuid)
                assets.append(asset)

                asset_violation = self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    date_from,
                    date_to,
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                    user_uuid=user_uuid,
                )
                if asset_violation:
                    poor_asset_count += 1
                else:
                    good_asset_count += 1

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
                "fleet": {
                    "total_asset": len(assets),
                    "good_assets": good_asset_count,
                    "poor_assets": poor_asset_count,
                },
            }

            return report

            # for asset in assets:
            #     if asset.device_imei:
            #         # Get asset points for today in tracking events table
            #         asset_events = self.tracking_event_repository.read_all_events_by_device_imei_date_range(
            #             asset.device_imei, date_from, date_to
            #         )
            #
            #         # Extract coordinates from asset events
            #         coordinates = [
            #             {
            #                 "latitude": event.latitude,
            #                 "longitude": event.longitude,
            #                 "speed": event.speed,
            #                 "timestamp": str(event.event_datetime),
            #                 "event_type": get_status(event.event_type),
            #                 "fuel_level": event.fuel_level,
            #             }
            #             for event in asset_events
            #         ]
            #
            #         # Calculate distance traveled
            #         distance_traveled = get_distance_travelled_by_coordinates(
            #             coordinates
            #         )
            #
            #         # Extract speeds from asset tracking event
            #         speeds = [event.speed for event in asset_events]
            #
            #         # Calculate average speed
            #         average_speed = calculate_average_speed(speeds)
            #
            #         # Calculate time traveled
            #         time_traveled = calculate_time_traveled(coordinates)
            #
            #         total_fuel_used = calculate_total_fuel_used(coordinates)
            #
            #         # Calculate total idle time
            #         total_idle_time = calculate_total_idle_time_and_movement(
            #             coordinates
            #         )
            #
            #         speed_violations = (
            #             self.asset_repository.get_over_speeding_violations(
            #                 asset.uuid,
            #                 GeofenceTypeUuid.OVER_SPEEDING_ALERT_POLICY,
            #                 date_from,
            #                 date_to,
            #             )
            #         )
            #
            #         # Append the result
            #         report.append(
            #             {
            #                 "asset_name": asset.asset_name,
            #                 "distance_traveled": distance_traveled,
            #                 "average_speed": average_speed,
            #                 "time_traveled": time_traveled,
            #                 "total_idle_time": total_idle_time.get("total_idle_time"),
            #                 "rapid_acceleration": total_idle_time.get(
            #                     "rapid_acceleration_count"
            #                 ),
            #                 "rapid_breaking": total_idle_time.get(
            #                     "rapid_braking_count"
            #                 ),
            #                 "speed_violations": len(speed_violations),
            #                 "total_fuel_recorded_current_date": total_fuel_used,  # Placeholder for fuel used
            #             }
            #         )

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
