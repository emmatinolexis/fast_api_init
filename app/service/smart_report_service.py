from collections import defaultdict
from datetime import datetime, timedelta

from dateutil import parser
from dateutil.relativedelta import relativedelta

from app.repository.alert_policy_repository import AlertPolicyRepository
from app.repository.asset_repository import AssetRepository
from app.repository.equipment_repository import EquipmentRepository
from app.repository.smart_report_repository import SmartReportRepository
from app.repository.tracking_event_repository import TrackingEventRepository
from app.service.base_service import BaseService
from app.util.enums import AlertPolicy, GeofenceTypeUuid
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
        alert_policy_repository: AlertPolicyRepository,
    ):
        self.smart_report_repository = smart_report_repository
        self.asset_repository = asset_repository
        self.tracking_event_repository = tracking_event_repository
        self.equipment_repository = equipment_repository
        self.alert_policy_repository = alert_policy_repository
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

    def process_asset(self, asset_uuid, date_from, date_to):
        asset = self.asset_repository.get_asset_with_relationships(
            asset_uuid, date_from, date_to
        )

        # Retrieve equipment name
        equipment_name = asset.equipment.name if asset.equipment else "Unknown"

        # Calculate rapid acceleration and emergency braking counts
        rapid_acceleration_count = calculate_total_idle_time_and_movement(
            asset.tracking_events
        )
        rapid_acceleration = rapid_acceleration_count.get("rapid_acceleration_count", 0)
        emergency_braking = rapid_acceleration_count.get("emergency_braking_count", 0)

        return asset, equipment_name, rapid_acceleration, emergency_braking

    def calculate_incidents_by_month(self, violations, incidents_rate, monthly_totals):
        required_keys = [
            "geofence",
            "overspeeding",
            "rapid_acceleration",
            "emergency_braking",
        ]

        for violation in violations:
            incident_date = violation.created_at
            month_name = incident_date.strftime("%B")

            alert_policy_type = violation.alert_policy.alert_policy_type.name.lower()

            # Ensure we only account for predefined alert policy types
            if alert_policy_type in required_keys:
                incidents_rate[month_name][alert_policy_type] += 1
                monthly_totals[month_name] += 1  # Track total incidents per month

    def ensure_all_months_present(
        self, incidents_rate, start_date, end_date, monthly_totals
    ):
        required_keys = [
            "geofence",
            "overspeeding",
            "rapid_acceleration",
            "emergency_braking",
        ]

        current_date = start_date
        while current_date <= end_date:
            month_name = current_date.strftime("%B")
            if month_name not in incidents_rate:
                incidents_rate[month_name] = {key: 0 for key in required_keys}
            else:
                # Ensure all required keys are present with a value of 0 if missing
                for key in required_keys:
                    if key not in incidents_rate[month_name]:
                        incidents_rate[month_name][key] = 0

            # Ensure monthly_totals has an entry for every month
            if month_name not in monthly_totals:
                monthly_totals[month_name] = 0

            current_date += relativedelta(months=1)

    def generate_violation_report(
        self, date_from: str, date_to: str, asset_uuids: list
    ):
        try:
            # Initialize data structures
            incidents_by_equipment_type = defaultdict(int)
            total_incidents = defaultdict(int)
            incidents_rate = defaultdict(lambda: defaultdict(int))
            monthly_totals = defaultdict(int)  # Track totals for each month
            total_rapid_acceleration = 0
            total_emergency_braking = 0

            # Parse the date strings to datetime objects
            start_date = datetime.strptime(date_from, "%d/%m/%Y")
            end_date = datetime.strptime(date_to, "%d/%m/%Y")

            for asset_uuid in asset_uuids:
                (
                    asset,
                    equipment_name,
                    rapid_acceleration,
                    emergency_braking,
                ) = self.process_asset(asset_uuid, date_from, date_to)

                total_rapid_acceleration += rapid_acceleration
                total_emergency_braking += emergency_braking

                # Get violations for the asset
                asset_violations = self.asset_repository.get_violations_by_asset(
                    asset_uuid, date_from, date_to
                )

                # Calculate incidents by month and update monthly totals
                self.calculate_incidents_by_month(
                    asset_violations, incidents_rate, monthly_totals
                )

                # Update incidents counts
                for violation in asset_violations:
                    alert_policy_type = (
                        violation.alert_policy.alert_policy_type.name.lower()
                    )
                    total_incidents[alert_policy_type] += 1

            # Add rapid acceleration and emergency braking to the total incidents
            total_incidents["rapid_acceleration"] = total_rapid_acceleration
            total_incidents["emergency_braking"] = total_emergency_braking

            # Calculate the total number of incidents
            total_incidents["total_incidents"] = sum(total_incidents.values())

            # Update incidents by equipment type
            incidents_by_equipment_type[equipment_name] = total_incidents[
                "total_incidents"
            ]
            incidents_by_equipment_type["total"] = sum(
                incidents_by_equipment_type.values()
            )

            # Ensure all months are present in the incidents_rate
            self.ensure_all_months_present(
                incidents_rate, start_date, end_date, monthly_totals
            )

            geofence = total_incidents.get("geofence", 0)
            overspeeding = total_incidents.get("overspeeding", 0)
            rapid_acceleration = total_incidents.get("rapid_acceleration", 0)
            emergency_braking = total_incidents.get("emergency_braking", 0)
            total_incidents = total_incidents.get("total_incidents", 0)

            # Prepare the final report
            report = {
                "incidents": {
                    "geofence": geofence,
                    "overspeeding": overspeeding,
                    "rapid_acceleration": rapid_acceleration,
                    "emergency_braking": emergency_braking,
                    "total_incidents": total_incidents,
                },
                "incidents_by_equipment_type": dict(incidents_by_equipment_type),
                "incidents_rate": {
                    month: dict(data) for month, data in incidents_rate.items()
                },
            }

            # Verify that the sum of all monthly incidents matches the total incidents
            # sum_of_monthly_totals = sum(sum(data.values()) for data in incidents_rate.values())
            # assert sum_of_monthly_totals == total_incidents[
            #     'total_incidents'], "Monthly totals do not match total incidents"

            return report

        except Exception as e:
            # Ensure you log or handle exceptions appropriately
            raise e

    def parse_dates(self, date_from, date_to):
        date_from_dt = datetime.strptime(
            date_from, "%d/%m/%Y"
        )  # Adjust the format according to your input
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
                event_time = datetime.strptime(event.get("event_datetime"), "%d/%m/%Y")
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

            # return monthly_utilization

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

    def generate_fuel_usage_report(
        self,
        start_date: str,
        end_date: str,
        asset_type_uuid: str,
        asset_uuids: list,
        user_uuid: str = None,
        business_uuid: str = None,
    ):
        try:
            assets = []
            start_date_dt = parser.parse(start_date)
            end_date_dt = parser.parse(end_date)

            for asset_uuid in asset_uuids:
                asset = self.asset_repository.get_asset_with_relationships(
                    asset_uuid, start_date, end_date
                )
                assets.append(asset)

            # Initialize the report dictionary with all months in the date range set to 0
            fuel_usage_report = {}
            current_date = start_date_dt.replace(day=1)
            while current_date <= end_date_dt:
                month_key = current_date.strftime("%B")
                fuel_usage_report[month_key] = 0
                # Move to the next month
                next_month = current_date.month % 12 + 1
                next_year = current_date.year + (current_date.month // 12)
                current_date = current_date.replace(
                    year=next_year, month=next_month, day=1
                )

            organized_events = defaultdict(list)

            for asset in assets:
                for event in asset.tracking_events:
                    event_date = parser.parse(event["timestamp"])
                    if start_date_dt <= event_date <= end_date_dt:
                        # Group by month and year
                        period_key = event_date.strftime("%Y-%m")
                        organized_events[period_key].append(event)

            for period, events in organized_events.items():
                # Filter out events that have a fuel level
                fuel_level_events = [
                    event for event in events if event["fuel_level"] is not None
                ]
                # Calculate total fuel used for this period
                total_fuel_used = calculate_total_fuel_used(fuel_level_events)
                # Convert period_key to month name
                month_name = parser.parse(period + "-01").strftime("%B")
                # Update the report with actual values
                fuel_usage_report[month_name] = total_fuel_used

            return {
                "fuel_usage_report": fuel_usage_report,
                "total_fuel_used": sum(fuel_usage_report.values()),
            }

        except Exception as e:
            raise e

    def get_violations_reminders(
        self,
        start_date,
        end_date,
        business_uuid=None,
        user_uuid=None,
        asset_uuid=None,
        asset_type_uuid=None,
    ):
        if business_uuid:
            return {
                "geofence_violations": self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.GEOFENCE_ALERT_POLICY,
                    start_date,
                    end_date,
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "over_speeding_violations": self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.OVER_SPEEDING_ALERT_POLICY,
                    start_date,
                    end_date,
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "idling_violations": self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.IDLING_ALERT_POLICY,
                    start_date,
                    end_date,
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "break_inspection": self.asset_repository.get_maintenance_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    AlertPolicy.BRAKE_INSPECTION,
                    start_date,
                    end_date,
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "oil_change": self.asset_repository.get_maintenance_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    AlertPolicy.OIL_CHANGE,
                    start_date,
                    end_date,
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "tire_rotation": self.asset_repository.get_maintenance_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    AlertPolicy.TIRE_ROTATION,
                    start_date,
                    end_date,
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "general_servicing": self.asset_repository.get_maintenance_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    AlertPolicy.GENERAL_SERVICING,
                    start_date,
                    end_date,
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "others": self.asset_repository.get_maintenance_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    AlertPolicy.OTHER,
                    start_date,
                    end_date,
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
            }
        elif user_uuid:
            return {
                "geofence_violations": self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.GEOFENCE_ALERT_POLICY,
                    start_date,
                    end_date,
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "over_speeding_violations": self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.OVER_SPEEDING_ALERT_POLICY,
                    start_date,
                    end_date,
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "idling_violations": self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.IDLING_ALERT_POLICY,
                    start_date,
                    end_date,
                    user_uuid=user_uuid,
                ),
                "break_inspection": self.asset_repository.get_maintenance_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    AlertPolicy.BRAKE_INSPECTION,
                    start_date,
                    end_date,
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "oil_change": self.asset_repository.get_maintenance_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    AlertPolicy.OIL_CHANGE,
                    start_date,
                    end_date,
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "tire_rotation": self.asset_repository.get_maintenance_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    AlertPolicy.TIRE_ROTATION,
                    start_date,
                    end_date,
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "general_servicing": self.asset_repository.get_maintenance_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    AlertPolicy.GENERAL_SERVICING,
                    start_date,
                    end_date,
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "others": self.asset_repository.get_maintenance_by_alert_type(
                    GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
                    AlertPolicy.OTHER,
                    start_date,
                    end_date,
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
            }
        else:
            return {}

    def generate_heat_map_report(self, date_from: str, date_to: str, asset_uuids: list):
        try:
            violations = self.alert_policy_repository.generate_violations_by_asset_uuids_date_range(
                date_from, date_to, asset_uuids
            )
            return violations
            # for asset_uuid in asset_uuids:
            #     asset = self.alert_policy_violation.alert_policy() asset_repository.get_asset_with_relationships(
            #         asset_uuid, date_from, date_to
            #     )
            #
            #     assets.append(asset)
            #
            # (
            #     total_distance_traveled_current_range,
            #     total_distance_traveled_past_range,
            #     fuel_level_current_range,
            #     fuel_level_past_range,
            # ) = self.calculate_total_distance(assets, date_from, date_to)
            #
            # report = {
            #     "total_distance_covered_current_date": round(
            #         total_distance_traveled_current_range, 2
            #     ),
            #     "total_distance_covered_previous_date": round(
            #         total_distance_traveled_past_range, 2
            #     ),
            #     "total_fuel_recorded_current_date": fuel_level_current_range,
            #     "total_fuel_recorded_previous_date": fuel_level_past_range,
            #     "total_fuel_saved": fuel_level_past_range - fuel_level_current_range,
            # }
            #
            # return report

    def generate_fuel_utilization_report(
        self,
        start_date: str,
        end_date: str,
        asset_type_uuid: str,
        asset_uuids: list,
        user_uuid: str = None,
        business_uuid: str = None,
    ):
        try:
            assets = []
            start_date_dt = parser.parse(start_date)
            end_date_dt = parser.parse(end_date)

            # Step 1: Retrieve assets and filter events by date range
            for asset_uuid in asset_uuids:
                asset = self.asset_repository.get_asset_with_relationships(
                    asset_uuid, start_date, end_date
                )
                assets.append(asset)

            # Initialize the structure for storing monthly fuel utilization data
            monthly_fuel_utilization = defaultdict(lambda: defaultdict(float))

            for asset in assets:
                asset_name = asset.asset_name
                for event in asset.tracking_events:
                    event_date = parser.parse(event["timestamp"])
                    if (
                        start_date_dt <= event_date <= end_date_dt
                        and event["fuel_level"] is not None
                    ):
                        month = event_date.strftime("%B")
                        # Aggregate fuel usage by asset and month
                        monthly_fuel_utilization[month][asset_name] += event[
                            "fuel_level"
                        ]

            # Prepare the final report structure
            smart_report = []
            for month in sorted(
                monthly_fuel_utilization.keys(),
                key=lambda x: parser.parse(x, fuzzy=True).month,
            ):
                month_fuel_data = monthly_fuel_utilization[month]
                fuel_utilization = [
                    {asset: fuel} for asset, fuel in month_fuel_data.items()
                ]
                smart_report.append(
                    {
                        "fuel_utilization": fuel_utilization,
                        "month": month,
                    }
                )

            utilization_data = [{"smart_report": smart_report}]

            return utilization_data

        except Exception as e:
            raise e
