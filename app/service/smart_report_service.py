import logging
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta

from app.repository.alert_policy_repository import AlertPolicyRepository
from app.repository.asset_repository import AssetRepository
from app.repository.equipment_repository import EquipmentRepository
from app.repository.fuel_log_repository import FuelLogRepository
from app.repository.smart_report_repository import SmartReportRepository
from app.repository.tracking_event_repository import TrackingEventRepository
from app.repository.user_repository import UserRepository
from app.service.base_service import BaseService
from app.util.enums import (
    AccountType,
    AlertPolicy,
    GeofenceTypeUuid,
    SmartReportStatus,
    SmartReportType,
)
from app.util.utils import (
    calculate_time_traveled,
    calculate_total_fuel_used,
    calculate_total_idle_time_and_movement,
    convert_date_format,
    convert_iso_datetime_format,
    get_distance_travelled_by_coordinates,
    get_status,
    sort_events_by_timestamp,
    to_snake_case,
)


class SmartReportService(BaseService):
    def __init__(
        self,
        smart_report_repository: SmartReportRepository,
        asset_repository: AssetRepository,
        tracking_event_repository: TrackingEventRepository,
        equipment_repository: EquipmentRepository,
        alert_policy_repository: AlertPolicyRepository,
        user_repository: UserRepository,
        fuel_log_repository: FuelLogRepository,
    ):
        self.smart_report_repository = smart_report_repository
        self.asset_repository = asset_repository
        self.tracking_event_repository = tracking_event_repository
        self.equipment_repository = equipment_repository
        self.alert_policy_repository = alert_policy_repository
        self.user_repository = user_repository
        self.fuel_log_repository = fuel_log_repository
        super().__init__(smart_report_repository)

    def get_reports(
        self,
        user_uuid: str = None,
        query_parameter: str = None,
        created_by: str = None,
        business_profile_uuid: str = None,
        page=1,
        page_size=10,
    ):
        try:
            return self.smart_report_repository.read_all_reports(
                user_uuid=user_uuid,
                business_uuid=business_profile_uuid,
                query_parameter=query_parameter,
                created_by=created_by,
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

    def process_asset(self, asset, start_date, end_date):
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
            "over_speeding",
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
        # Convert date strings to datetime objects
        current_date = datetime.strptime(start_date, "%d/%m/%Y")
        end_date = datetime.strptime(end_date, "%d/%m/%Y")

        months_to_remove = []

        while current_date <= end_date:
            month_year = current_date.strftime("%Y-%m")

            if month_year not in incidents_rate:
                # If the month is not in incidents_rate, do nothing
                pass
            else:
                # If the month exists, check if it has any non-zero incidents
                if not any(incidents_rate[month_year].values()):
                    # Mark the month for removal if it has no incidents
                    months_to_remove.append(month_year)

            # Ensure monthly_totals has an entry for every month
            if month_year not in monthly_totals:
                monthly_totals[month_year] = 0

            # Move to the next month
            current_date += relativedelta(months=1)

        # Remove months that have no incidents
        for month in months_to_remove:
            del incidents_rate[month]

    def generate_violation_fleet_performance_report(
        self, date_from: str, date_to: str, assets: list
    ):
        try:
            # Initialize data structures
            data = self.initialize_data_structures()

            # Process each asset
            for asset in assets:
                self.process_assets(asset, date_from, date_to, data)

            # Calculate KMPG for each make
            data["fuel_utilization_mpg"] = self.calculate_kmpg(data)

            # Process violations
            if data["asset_violations"]:
                self.process_violations(data)

            # Ensure all months are present in the incidents_rate
            self.ensure_all_months_present(
                data["incidents_rate"], date_from, date_to, data["monthly_totals"]
            )

            # Prepare the final report
            report = self.prepare_final_report(data)

            return report

        except Exception as e:
            # Ensure you log or handle exceptions appropriately
            raise e

    def initialize_data_structures(self):
        return {
            "incidents_by_equipment_type": defaultdict(int),
            "incidents": defaultdict(int),
            "incidents_rate": defaultdict(lambda: defaultdict(int)),
            "monthly_totals": defaultdict(int),
            "total_rapid_acceleration": 0,
            "total_emergency_braking": 0,
            "policy_type_counts": defaultdict(int),
            "asset_violations": [],
            "violated_assets": [],
            "fuel_purchased": [],
            "fuel_usage_by_month": defaultdict(lambda: {"total_litres": 0.0}),
            "fuel_usage_by_equipment": defaultdict(
                lambda: defaultdict(lambda: {"total_litres": 0.0})
            ),
            "total_litres_all_months": 0.0,
            "fuel_usage_by_make": defaultdict(lambda: defaultdict(float)),
            "distance_by_make": defaultdict(lambda: defaultdict(float)),
        }

    def process_assets(self, asset, date_from, date_to, data):
        # return asset
        (
            asset,
            equipment_name,
            rapid_acceleration,
            emergency_braking,
        ) = self.process_asset(asset, start_date=date_from, end_date=date_to)

        data["total_rapid_acceleration"] += rapid_acceleration
        data["total_emergency_braking"] += emergency_braking

        total_distance_traveled = get_distance_travelled_by_coordinates(
            asset.tracking_events
        )
        # asset_make = asset.make

        asset_violations_data = self.asset_repository.get_violations_by_asset(
            asset.uuid, date_from, date_to
        )
        data["asset_violations"].extend(asset_violations_data)

        fuel_purchase = self.fuel_log_repository.get_fuel_log_by_asset(
            asset.uuid, date_from, date_to
        )
        data["fuel_purchased"].extend(fuel_purchase)

        # Aggregate fuel data
        self.aggregate_fuel_data(asset, data, total_distance_traveled)

    def aggregate_fuel_data(self, asset, data, total_distance_traveled):
        # Calculate the total fuel used for the given asset and update the overall total
        total_fuel_used = calculate_total_fuel_used(asset.tracking_events)
        # data["total_litres_all_months"] += total_fuel_used
        total_fuel_used_all_months = 0.0

        # Extract the necessary data from the asset
        equipment_name = asset.equipment.name
        asset_make = asset.make

        # Iterate over each tracking event to aggregate data by month
        events_by_month = {}

        for event in asset.tracking_events:
            event_date = datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")
            month_year = event_date.strftime("%Y-%m")

            if month_year not in events_by_month:
                events_by_month[month_year] = []

            events_by_month[month_year].append(event)

        for month_year, events in events_by_month.items():
            # Calculate the fuel used for the current month
            monthly_fuel_used = calculate_total_fuel_used(events)
            total_fuel_used_all_months += monthly_fuel_used

            # Update fuel usage by month
            data["fuel_usage_by_month"][month_year]["total_litres"] += monthly_fuel_used

            # Update fuel usage by equipment type and month
            data["fuel_usage_by_equipment"][equipment_name][month_year][
                "total_litres"
            ] += monthly_fuel_used

            # Update fuel usage by make and month
            data["fuel_usage_by_make"][asset_make][month_year] += monthly_fuel_used

            # Update distance traveled by make and month
            data["distance_by_make"][asset_make][month_year] += total_distance_traveled

        # Update the total litres for all months
        data["total_litres_all_months"] += total_fuel_used

    def calculate_kmpg(self, data):
        fuel_utilization_mpg = []
        for month_year in sorted(data["fuel_usage_by_month"].keys()):
            month_utilization = []
            for make in data["fuel_usage_by_make"].keys():
                total_fuel_consumed = data["fuel_usage_by_make"][make][month_year]
                total_distance = data["distance_by_make"][make][month_year]
                kmpg = (
                    total_distance / total_fuel_consumed
                    if total_fuel_consumed > 0 and total_distance > 0
                    else 0
                )
                month_utilization.append({"model": make, "utilization": round(kmpg, 2)})

            fuel_utilization_mpg.append(
                {
                    "year_month": month_year,
                    "fuel_utilization_by_month": month_utilization,
                }
            )

        return fuel_utilization_mpg

    def process_violations(self, data):
        # Initialize or reset the total_incidents count
        # data["incidents"] = defaultdict(int)

        for violation in data["asset_violations"]:
            # Automatically append '_violations' to the policy type name
            policy_type_name = to_snake_case(
                violation.alert_policy.alert_policy_type.name.replace(
                    "alert policy", "violations"
                )
            )

            # Increment the count for this policy type
            data["policy_type_counts"][policy_type_name] += 1

            # Increment the count for the equipment type
            equipment_name = violation.asset.equipment.name
            data["incidents_by_equipment_type"][equipment_name] += 1

            # Track the incident rate by month and policy type
            month_year = violation.created_at.strftime("%Y-%m")
            data["incidents_rate"][month_year][policy_type_name] += 1

            # Increment the count for this policy type in incidents
            data["incidents"][policy_type_name] += 1

            # Increment the total incident count
            # data["incidents"]["total_violations"] += 1

            # Prepare the violated asset details
            violated_asset = []
            for violation_coordinate in violation.violation_coordinates:
                asset = {
                    "asset_name": violation.asset.asset_name,
                    "violation_date": violation.created_at,
                    "violation_type": policy_type_name,
                    "longitude": violation_coordinate.get("longitude"),
                    "latitude": violation_coordinate.get("latitude"),
                }
                violated_asset.append(asset)

            # Add to violated assets list
            data["violated_assets"].extend(violated_asset)

    def prepare_final_report(self, data):
        return {
            "fuel_usage": {
                "total_litres_all_months": data["total_litres_all_months"],
                "fuel_usage_by_month": [
                    {
                        "year_month": month,
                        "quantity": {"total_quantity": month_data["total_litres"]},
                    }
                    for month, month_data in data["fuel_usage_by_month"].items()
                ],
                "fuel_usage_by_asset_type": {
                    "assets": [
                        {
                            "type": equipment_name,
                            "quantity": sum(
                                month_data["total_litres"]
                                for month_data in monthly_data.values()
                            ),
                            "fuel_percentage": round(
                                (
                                    sum(
                                        month_data["total_litres"]
                                        for month_data in monthly_data.values()
                                    )
                                    / data["total_litres_all_months"]
                                    if data["total_litres_all_months"] > 0
                                    else 0  # Avoid division by zero
                                )
                                * 100,
                                2,
                            ),
                        }
                        for equipment_name, monthly_data in data[
                            "fuel_usage_by_equipment"
                        ].items()
                    ]
                },
            },
            "fuel_utilization_mpg": data["fuel_utilization_mpg"],
            "incidents": data["incidents"],
            "incidents_by_equipment_type": data["incidents_by_equipment_type"],
            "incidents_rate": data["incidents_rate"],
            "violated_assets": data["violated_assets"],
        }

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
                event_time = datetime.strptime(
                    event.get("timestamp"), "%Y-%m-%d %H:%M:%S"
                )
                event_month = event_time.strftime("%B")
                monthly_events[event_month].append(event)
        return monthly_events

    def calculate_times(self, events):
        if events:
            moving_time = calculate_time_traveled(events, unit="hours")
            idling_time = calculate_total_idle_time_and_movement(
                events, idle_time_unit="hours"
            )
            return round(moving_time, 2), round(
                idling_time.get("total_idle_time", 0), 2
            )
        return 0, 0

    def generate_report_fleet_overview(
        self,
        no_of_assets: int,
        grouped_assets,
        good_asset_count,
        poor_asset_count,
        monthly_utilization,
    ):
        report = {
            "fleet": {
                "total_asset": no_of_assets,
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
        assets: list,
        user_uuid: str = None,
        business_uuid: str = None,
    ):
        try:
            date_from_dt, date_to_dt, unique_months = self.parse_dates(
                date_from, date_to
            )

            monthly_utilization = self.initialize_monthly_utilization(unique_months)
            grouped_assets = {}
            good_asset_count, poor_asset_count = 0, 0

            for asset in assets:
                asset_violation = self.get_asset_violation(
                    asset,
                    date_from_dt,
                    date_to_dt,
                    business_uuid,
                    asset_type_uuid,
                    user_uuid,
                )

                if asset_violation:
                    poor_asset_count += 1
                else:
                    good_asset_count += 1

                equipment_name = asset.equipment.name
                if equipment_name not in grouped_assets:
                    grouped_assets[equipment_name] = {"hours_worked": 0, "idle_time": 0}

                self.update_monthly_utilization(monthly_utilization, asset)
                self.update_grouped_assets(grouped_assets, asset)

            self.normalize_grouped_assets(grouped_assets)
            self.round_monthly_utilization(monthly_utilization)

            report = self.generate_report_fleet_overview(
                len(assets),
                grouped_assets,
                good_asset_count,
                poor_asset_count,
                monthly_utilization,
            )
            return report

        except Exception as e:
            raise e

    def initialize_monthly_utilization(self, unique_months):
        return {month: {"hours_worked": 0, "idle_time": 0} for month in unique_months}

    def get_asset_violation(
        self, asset, date_from_dt, date_to_dt, business_uuid, asset_type_uuid, user_uuid
    ):
        return self.asset_repository.get_violations_by_alert_type(
            GeofenceTypeUuid.MAINTENANCE_ALERT_POLICY,
            date_from_dt,
            date_to_dt,
            business_uuid=business_uuid,
            asset_uuid=asset.uuid,
            asset_type_uuid=asset_type_uuid,
            user_uuid=user_uuid,
        )

    def update_monthly_utilization(self, monthly_utilization, asset):
        monthly_events = self.group_events_by_month(asset)
        for month, events in monthly_events.items():
            moving_time, idle_time = self.calculate_times(events)
            total_time = moving_time + idle_time

            if total_time > 0:
                hours_worked_percentage = round((moving_time / total_time) * 100, 2)
                idle_time_percentage = round((idle_time / total_time) * 100, 2)
            else:
                hours_worked_percentage = 0
                idle_time_percentage = 0

            monthly_utilization[month]["hours_worked"] += hours_worked_percentage
            monthly_utilization[month]["idle_time"] += idle_time_percentage

    def update_grouped_assets(self, grouped_assets, asset):
        overall_moving_time, overall_idle_time = self.calculate_times(
            asset.tracking_events
        )
        total_overall_time = overall_moving_time + overall_idle_time

        if total_overall_time > 0:
            overall_hours_worked_percentage = round(
                (overall_moving_time / total_overall_time) * 100, 2
            )
            overall_idle_time_percentage = round(
                (overall_idle_time / total_overall_time) * 100, 2
            )

            equipment_name = asset.equipment.name
            grouped_assets[equipment_name][
                "hours_worked"
            ] += overall_hours_worked_percentage
            grouped_assets[equipment_name]["idle_time"] += overall_idle_time_percentage
        else:
            # If there are no incidents, return an empty dictionary
            return {}

        return grouped_assets

    def normalize_grouped_assets(self, grouped_assets):
        for equipment_name, utilization in grouped_assets.items():
            total_percentage = utilization["hours_worked"] + utilization["idle_time"]
            if total_percentage > 0:
                grouped_assets[equipment_name]["hours_worked"] = round(
                    (utilization["hours_worked"] / total_percentage) * 100, 2
                )
                grouped_assets[equipment_name]["idle_time"] = round(
                    (utilization["idle_time"] / total_percentage) * 100, 2
                )

    def round_monthly_utilization(self, monthly_utilization):
        for month, utilization in monthly_utilization.items():
            monthly_utilization[month]["hours_worked"] = round(
                monthly_utilization[month]["hours_worked"], 2
            )
            monthly_utilization[month]["idle_time"] = round(
                monthly_utilization[month]["idle_time"], 2
            )

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
        asset_uuids: list,
    ):
        try:
            assets = []
            start_date_dt = parser.parse(start_date)
            end_date_dt = parser.parse(end_date)

            # Retrieve assets and their tracking events
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
                fuel_usage_report[
                    month_key
                ] = 0.0  # Ensure the initial value is a float
                # Move to the next month
                next_month = current_date.month % 12 + 1
                next_year = current_date.year + (current_date.month // 12)
                current_date = current_date.replace(
                    year=next_year, month=next_month, day=1
                )

            # Organize events by month
            organized_events = defaultdict(list)

            for asset in assets:
                for event in asset.tracking_events:
                    event_date = parser.parse(event["timestamp"])
                    if start_date_dt <= event_date <= end_date_dt:
                        # Group by month and year
                        period_key = event_date.strftime("%Y-%m")
                        organized_events[period_key].append(event)

            # Calculate fuel usage for each period
            for period, events in organized_events.items():
                # Filter out events that have a fuel level
                fuel_level_events = [
                    event for event in events if event["fuel_level"] is not None
                ]
                # Calculate total fuel used for this period
                total_fuel_used = calculate_total_fuel_used(fuel_level_events)
                # Convert period_key to month name
                month_name = parser.parse(period + "-01").strftime("%B")
                # Update the report with actual values, rounded to 2 decimal places
                fuel_usage_report[month_name] = round(total_fuel_used, 2)

            return {
                "fuel_usage_report": fuel_usage_report,
                "total_fuel_used": round(sum(fuel_usage_report.values()), 2),
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

    def generate_fuel_utilization_report(
        self,
        start_date: str,
        end_date: str,
        asset_uuids: list,
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
                        # Aggregate fuel usage by asset and month, rounding to 2 decimal places
                        monthly_fuel_utilization[month][asset_name] += round(
                            event["fuel_level"], 2
                        )

            # Prepare the final report structure
            smart_report = []
            for month in sorted(
                monthly_fuel_utilization.keys(),
                key=lambda x: parser.parse(x, fuzzy=True).month,
            ):
                month_fuel_data = monthly_fuel_utilization[month]
                fuel_utilization = [
                    {asset: round(fuel, 2)} for asset, fuel in month_fuel_data.items()
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

    def generate_fuel_usage_by_asset_type_report(
        self,
        start_date: str,
        end_date: str,
        asset_uuids: list,
    ):
        try:
            assets = []

            # Step 1: Retrieve assets and filter events by date range
            for asset_uuid in asset_uuids:
                asset = self.asset_repository.get_asset_with_relationships(
                    asset_uuid, start_date, end_date
                )
                assets.append(asset)

            # Initialize the structure for storing monthly fuel utilization data
            return assets

        except Exception as e:
            raise e

    def get_unprocessed_smart_report_by_uuid(self):
        try:
            report = self.smart_report_repository.get_unprocessed_report()
            return report
        except Exception as e:
            raise e

    def get_processed_smart_report(self, smart_report):
        try:
            url = smart_report.result_url

            # Fetch the content from the URL
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful

            # Parse the JSON content
            smart_report = response.json()

            return smart_report
        except Exception as e:
            raise e

    def update_smart_report_status(
        self, smart_report_uuid: str, status: SmartReportStatus, url: str = None
    ):
        try:
            report = self.smart_report_repository.update_smart_report_status(
                smart_report_uuid, status, url
            )
            return report
        except Exception as e:
            raise e

    def generate_smart_report(self, report):
        try:
            if not report:
                logging.info("No smart report to process")
                return None

            asset_uuids = report.get("asset_group_uuids").get("asset_uuids")
            start_date = convert_date_format(report.get("start_date"))
            end_date = convert_date_format(report.get("end_date"))
            report_types = report.get("report_types")
            user_uuid = report.get("user_uuid")
            asset_type_uuid = report.get("asset_type_uuid")
            created_by = report.get("created_by")
            report_title_header = report.get("title")
            report_date = convert_iso_datetime_format(report.get("created_at"))

            # Retrieve user and business details
            user, business_uuid, business_name = self.get_user_and_business_details(
                user_uuid, report
            )

            # Retrieve assets
            assets = self.get_assets(asset_uuids, start_date, end_date)

            # Calculate distances and fuel efficiency
            (
                total_distance_traveled_current_range,
                total_distance_traveled_past_range,
                fuel_level_current_range,
                fuel_level_past_range,
            ) = self.calculate_total_distance(assets, start_date, end_date)

            (
                fuel_efficiency_current_range,
                fuel_efficiency_past_range,
            ) = self.calculate_fuel_efficiency(
                total_distance_traveled_current_range,
                fuel_level_current_range,
                total_distance_traveled_past_range,
                fuel_level_past_range,
            )

            # Generate fleet overview report section
            smart_report_fleet_overview = {}
            if SmartReportType.FLEET_OVERVIEW in report_types:
                if user.get("account_type") == AccountType.INDIVIDUAL:
                    smart_report_fleet_overview = (
                        self.generate_smart_report_fleet_overview(
                            start_date,
                            end_date,
                            asset_type_uuid,
                            assets,
                            user_uuid=user.get("uuid"),
                        )
                    )
                elif user.get("account_type") == AccountType.BUSINESS:
                    smart_report_fleet_overview = (
                        self.generate_smart_report_fleet_overview(
                            start_date,
                            end_date,
                            asset_type_uuid,
                            assets,
                            business_uuid=business_uuid,
                        )
                    )

            # Generate fleet performance report section
            smart_report_fleet_performance = {}
            if SmartReportType.FLEET_PERFORMANCE in report_types:
                smart_report_fleet_performance = (
                    self.generate_violation_fleet_performance_report(
                        start_date, end_date, assets
                    )
                )

            # Generate cost analysis report section
            cost_analysis = {}
            if SmartReportType.COST_ANALYSIS in report_types:
                cost_analysis = self.generate_cost_analysis_report(
                    start_date, end_date, assets
                )

            # Assemble the final report
            return self.assemble_report(
                report_date,
                report_title_header,
                created_by,
                business_name,
                start_date,
                end_date,
                fuel_efficiency_current_range,
                fuel_efficiency_past_range,
                total_distance_traveled_current_range,
                total_distance_traveled_past_range,
                fuel_level_current_range,
                fuel_level_past_range,
                smart_report_fleet_overview,
                smart_report_fleet_performance,
                cost_analysis,
            )

        except Exception as e:
            raise e

    def get_user_and_business_details(self, user_uuid, report):
        user = self.user_repository.get_user_by_uuid(user_uuid)
        if user.get("account_type") == AccountType.BUSINESS:
            business_uuid = report.get("business_profile_uuid")
            business_name = report.get("business_name")
        else:
            business_uuid = None
            business_name = None
        return user, business_uuid, business_name

    def get_assets(self, asset_uuids, start_date, end_date):
        assets = []
        for asset_uuid in asset_uuids:
            asset = self.asset_repository.get_asset_with_relationships(
                asset_uuid, start_date, end_date
            )
            assets.append(asset)
        return assets

    def calculate_fuel_efficiency(
        self,
        total_distance_traveled_current_range,
        fuel_level_current_range,
        total_distance_traveled_past_range,
        fuel_level_past_range,
    ):
        fuel_efficiency_current_range = (
            round(total_distance_traveled_current_range / fuel_level_current_range, 2)
            if fuel_level_current_range > 0
            else 0.0
        )
        fuel_efficiency_past_range = (
            round(total_distance_traveled_past_range / fuel_level_past_range, 2)
            if fuel_level_past_range > 0
            else 0.0
        )
        return fuel_efficiency_current_range, fuel_efficiency_past_range

    def generate_fleet_overview(
        self,
        report_types,
        user,
        asset_type_uuid,
        assets,
        start_date,
        end_date,
        business_uuid,
    ):
        if SmartReportType.FLEET_OVERVIEW not in report_types:
            return {}

        if user.get("account_type") == AccountType.INDIVIDUAL:
            return self.generate_smart_report_fleet_overview(
                start_date,
                end_date,
                asset_type_uuid,
                assets,
                user_uuid=user.get("uuid"),
            )
        elif user.get("account_type") == AccountType.BUSINESS:
            return self.generate_smart_report_fleet_overview(
                start_date,
                end_date,
                asset_type_uuid,
                assets,
                business_uuid=business_uuid,
            )
        else:
            return {}

    def assemble_report(
        self,
        report_date,
        report_title_header,
        created_by,
        business_name,
        start_date,
        end_date,
        fuel_efficiency_current_range,
        fuel_efficiency_past_range,
        total_distance_traveled_current_range,
        total_distance_traveled_past_range,
        fuel_level_current_range,
        fuel_level_past_range,
        smart_report_fleet_overview,
        smart_report_fleet_performance,
        cost_analysis,
    ):
        return {
            "report_header": {
                "report_date": report_date,
                "report_title": report_title_header,
                "created_by": created_by,
                "business_name": business_name,
                "end_date": end_date,
                "start_date": start_date,
                "fuel_efficiency_current_date": fuel_efficiency_current_range,
                "fuel_efficiency_previous_date": fuel_efficiency_past_range,
                "total_distance_covered_current_date": round(
                    total_distance_traveled_current_range, 2
                ),
                "total_distance_covered_previous_date": round(
                    total_distance_traveled_past_range, 2
                ),
                "total_fuel_recorded_current_date": round(fuel_level_current_range, 2),
                "total_fuel_recorded_previous_date": round(fuel_level_past_range, 2),
                "total_fuel_saved": round(
                    fuel_level_past_range - fuel_level_current_range, 2
                ),
            },
            "smart_report_fleet_overview": smart_report_fleet_overview,
            "smart_report_fleet_performance": smart_report_fleet_performance,
            "cost_analysis": cost_analysis,
        }

    def filter_events_by_date_range(self, events, start_date, end_date):
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date)
            events = [
                event
                for event in events
                if datetime.fromisoformat(event["timestamp"]) >= start_date
            ]

        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date)
            events = [
                event
                for event in events
                if datetime.fromisoformat(event["timestamp"]) <= end_date
            ]

        return events

    def calculate_rapid_events_by_month(
        self, events, accel_threshold=10, brake_threshold=-10
    ):
        # Initialize counters for rapid acceleration and emergency braking by month
        rapid_acceleration_by_month = defaultdict(int)
        emergency_braking_by_month = defaultdict(int)

        # Sort events by timestamp
        events_sorted = sort_events_by_timestamp(events)

        # Initialize variables to keep track of previous event data
        prev_event = None

        for event in events_sorted:
            # Convert timestamp to datetime and extract month
            event_timestamp = datetime.fromisoformat(event["timestamp"])
            month_year = event_timestamp.strftime("%Y-%m")

            if prev_event:
                # Calculate speed change between events
                speed_change = event["speed"] - prev_event["speed"]

                # Check for rapid acceleration
                if speed_change >= accel_threshold:
                    rapid_acceleration_by_month[month_year] += 1

                # Check for rapid braking
                if speed_change <= brake_threshold:
                    emergency_braking_by_month[month_year] += 1

            # Update previous event
            prev_event = event

        return rapid_acceleration_by_month, emergency_braking_by_month

    def generate_cost_analysis_report(self, date_from: str, date_to: str, assets: list):
        try:
            fuel_purchased = []
            fuel_usage_by_month = defaultdict(
                lambda: {"total_amount": 0.0, "total_litres": 0.0}
            )
            fuel_usage_by_equipment = defaultdict(
                lambda: defaultdict(lambda: {"total_amount": 0.0, "total_litres": 0.0})
            )
            total_amount_all_months = 0.0
            total_litres_all_months = 0.0

            # Fetch fuel purchase logs for each asset
            for asset in assets:
                fuel_purchase = self.fuel_log_repository.get_fuel_log_by_asset(
                    asset.uuid, date_from, date_to
                )
                fuel_purchased.extend(fuel_purchase)

            # Process each purchase
            for purchase in fuel_purchased:
                purchase_date = datetime.strptime(purchase.purchase_date, "%Y-%m-%d")
                month_year = purchase_date.strftime("%Y-%m")
                equipment_name = purchase.asset.equipment.name

                # Aggregate fuel data by month and by equipment
                fuel_usage_by_month[month_year]["total_amount"] += purchase.amount
                fuel_usage_by_month[month_year]["total_litres"] += purchase.quantity
                total_amount_all_months += purchase.amount
                total_litres_all_months += purchase.quantity

                fuel_usage_by_equipment[equipment_name][month_year][
                    "total_amount"
                ] += purchase.amount
                fuel_usage_by_equipment[equipment_name][month_year][
                    "total_litres"
                ] += purchase.quantity

            # Reformat fuel usage by month
            fuel_amount_by_month = [
                {
                    "year_month": month_year,
                    "amount": {
                        "total_amount": month_data["total_amount"],
                    },
                }
                for month_year, month_data in fuel_usage_by_month.items()
            ]

            # Calculate the percentage and total fuel amount for each equipment type
            fuel_cost_by_asset_type = []
            for equipment_name, monthly_data in fuel_usage_by_equipment.items():
                total_fuel_amount = sum(
                    data["total_amount"] for data in monthly_data.values()
                )
                fuel_percentage = (
                    (total_fuel_amount / total_amount_all_months) * 100
                    if total_amount_all_months > 0
                    else 0
                )
                fuel_cost_by_asset_type.append(
                    {
                        "type": equipment_name,
                        "fuel_amount": total_fuel_amount,
                        "fuel_percentage": round(fuel_percentage, 2),
                    }
                )

            # Prepare the final result in the desired format
            result = {
                "total_amount_all_months": total_amount_all_months,
                "total_litres_all_months": total_litres_all_months,
                "fuel_amount_by_month": fuel_amount_by_month,
                "fuel_cost_by_asset_type": {"assets": fuel_cost_by_asset_type},
            }

            return result
        except Exception as e:
            raise e
