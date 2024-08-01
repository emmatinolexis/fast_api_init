import math
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any, List, Union

import pandas as pd
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from geopy.distance import geodesic

from app.client.s3_client import S3Client
from app.core.constants import ADMIN_USER_ROLE, CUSTOMER_USER_ROLE, THIRD_PARTY_APP_ROLE
from app.core.logger import get_logger
from app.core.security import JWTBearer
from app.core.settings import settings
from app.util.enums import ActiveStatus, FileFormat

log = get_logger()

allow_admins_only = Depends(
    JWTBearer(
        allowed_roles=[
            ADMIN_USER_ROLE,
        ]
    )
)

allow_customers_only = Depends(
    JWTBearer(
        allowed_roles=[
            CUSTOMER_USER_ROLE,
        ]
    )
)

allow_admins_and_customers = Depends(
    JWTBearer(
        allowed_roles=[
            ADMIN_USER_ROLE,
            CUSTOMER_USER_ROLE,
        ]
    )
)

allow_third_parties_only = Depends(
    JWTBearer(
        allowed_roles=[
            THIRD_PARTY_APP_ROLE,
        ]
    )
)


def generate_uuid() -> str:
    return str(uuid.uuid4())


def send_data(data: Any, status_code: int = 200):
    return ORJSONResponse(
        status_code=status_code,
        content={
            "data": jsonable_encoder(data),
        },
    )


def days_to_minutes(days):
    return days * 24 * 60


def send_data_with_info(data: Any, info: str, status_code: int = 200):
    log.info(info)
    return ORJSONResponse(
        status_code=status_code,
        content={
            "info": info,
            "data": data,
        },
    )


def send_info(info: str, status_code: int = 200):
    log.info(info)
    return ORJSONResponse(
        status_code=status_code,
        content={
            "info": info,
        },
    )


def send_client_side_error(user_msg: str, dev_msg: str = None, status_code: int = 400):
    log.error(user_msg, extra={"error": dev_msg})
    return ORJSONResponse(
        status_code=status_code,
        content={
            "userMsg": user_msg,
            "devMsg": user_msg if dev_msg is None else dev_msg,
        },
    )


def toggle_status(current_status):
    return (
        ActiveStatus.ACTIVE
        if current_status == ActiveStatus.INACTIVE
        else ActiveStatus.INACTIVE
    )


def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def send_internal_server_error(user_msg: str, error: Any, status_code: int = 500):
    log.error(user_msg, extra={"error": error})
    return ORJSONResponse(
        status_code=status_code,
        content={
            "userMsg": user_msg,
            "devMsg": str(error),
        },
    )


def get_status(status: str):
    status_mapping = {
        "Start_Moving": "moving",
        "Stop_Moving": "stopped",
        "Ignition_Off": "stopped",
        "Idling_Alarm": "idle",
        "Time_Interval_Tracking": "moving",
        "Time_Interval_Tracking_Moving": "moving",
        "Time_Interval_Tracking_Stopped": "stopped",
        "Time_Interval_Tracking_Idling": "idle",
    }

    return status_mapping.get(status, "unknown")


def generate_unique_token(size: int):
    return secrets.token_hex(size).upper()


def calculate_total_fuel_used(fuel_level_events):
    if not fuel_level_events:
        return 0.0

    if len(fuel_level_events) < 2:
        return (
            fuel_level_events[0]["fuel_level"]
            if "fuel_level" in fuel_level_events[0]
            and fuel_level_events[0]["fuel_level"] is not None
            else 0.0
        )

    total_fuel_used = 0.0

    # Sort events by timestamp to ensure they are in chronological order
    fuel_level_events.sort(key=lambda event: event["timestamp"])

    # Iterate through events and calculate fuel used between consecutive events
    for i in range(1, len(fuel_level_events)):
        previous_event = fuel_level_events[i - 1]
        current_event = fuel_level_events[i]

        # Ensure that fuel levels are present and not None
        if (
            "fuel_level" in previous_event
            and "fuel_level" in current_event
            and previous_event["fuel_level"] is not None
            and current_event["fuel_level"] is not None
        ):
            previous_fuel_level = previous_event["fuel_level"]
            current_fuel_level = current_event["fuel_level"]

            # Calculate the fuel used between the two events
            fuel_used = previous_fuel_level - current_fuel_level

            # Add to total fuel used, ensure that we are not adding negative values
            if fuel_used > 0:
                total_fuel_used += fuel_used

    return total_fuel_used


# Example usage:


def get_distance_travelled_by_coordinates(coordinates: Union[List[dict], List[tuple]]):
    """
    Calculate the total distance traveled given sets of coordinates
    :param coordinates: List of dictionaries or list of tuples where each dictionary contains "latitude" and "longitude"
    :return: Total distance traveled as float
    """
    if not coordinates:
        return 0.0

    total_distance = 0.0

    if isinstance(coordinates[0], dict):
        for i in range(len(coordinates) - 1):
            coord1 = (coordinates[i]["latitude"], coordinates[i]["longitude"])
            coord2 = (coordinates[i + 1]["latitude"], coordinates[i + 1]["longitude"])
            total_distance += geodesic(coord1, coord2).kilometers
    elif isinstance(coordinates[0], tuple):
        for i in range(len(coordinates) - 1):
            coord1 = coordinates[i]
            coord2 = coordinates[i + 1]
            total_distance += geodesic(coord1, coord2).kilometers
    else:
        raise ValueError(
            "Invalid coordinates format. Must be a list of dictionaries or a list of tuples."
        )

    return round(total_distance, 2)


def generate_polygon_geofence_coordinates(polygon_points: List[dict], num_points: int):
    """
    Generate coordinates for a geofence based on the boundary points of a polygon.

    Args:
    - polygon_points: list of dictionaries representing the boundary points of the polygon
    - num_points: number of points to generate along each edge of the polygon

    Returns:
    - list of tuples representing the coordinates of the geofence
    """
    if len(polygon_points) < 3:
        raise ValueError("A polygon must have at least 3 points.")

    geofence_coordinates = []
    for i in range(len(polygon_points)):
        start_point = polygon_points[i]
        end_point = polygon_points[(i + 1) % len(polygon_points)]

        # Extract latitude and longitude from dictionary
        start_lat, start_lon = start_point["latitude"], start_point["longitude"]
        end_lat, end_lon = end_point["latitude"], end_point["longitude"]

        lat_increment = (end_lat - start_lat) / num_points
        lon_increment = (end_lon - start_lon) / num_points
        for j in range(num_points):
            lat = start_lat + j * lat_increment
            lon = start_lon + j * lon_increment
            geofence_coordinates.append((lat, lon))

    # Add the first point again to close the geofence
    geofence_coordinates.append(geofence_coordinates[0])

    return geofence_coordinates


def generate_circle_geofence_coordinates(center: dict, radius: float, num_points: int):
    """
    Generate coordinates for a geofence representing a circle.

    Args:
    - center: tuple representing the center point of the circle (latitude, longitude)
    - radius: radius of the circle in meters
    - num_points: number of points to generate along the circumference of the circle

    Returns:
    - list of tuples representing the coordinates of the geofence
    """

    lat_center, lon_center = center["latitude"], center["longitude"]

    geofence_coordinates = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        lat = lat_center + radius / 111300 * math.sin(
            angle
        )  # 1 degree latitude = 111.3 km
        lon = lon_center + radius / (
            111300 * math.cos(lat_center * (math.pi / 180))
        ) * math.cos(
            angle
        )  # 1 degree longitude = 111.3 km * cos(latitude)
        geofence_coordinates.append((lat, lon))

    # Add the first point again to close the geofence
    geofence_coordinates.append(geofence_coordinates[0])

    return geofence_coordinates


def check_violated_geofence(
    asset_coordinates_events, geofence_coordinates, geofence_type
):
    """
    Check which geofences are violated by the given set of asset points.

    Args:
    - asset_coordinates_events: list of dictionaries representing points from the asset
                                {"lat": float, "lng": float, "speed": float,
                                 "course": float, "timestamp": str, "event_type": str}
    - geofence_coordinates: list of tuples representing the coordinates of the geofence
    - geofence_type: string indicating the type of geofence ('zone_exit' or 'zone_entry')

    Returns:
    - list of dictionaries representing the coordinates and speed of violated geofences
      {"lat": float, "lng": float, "speed": float, "course": float, "timestamp": str, "event_type": str}
    """
    violated_geofences = []

    for point in asset_coordinates_events:
        inside = False
        for i in range(len(geofence_coordinates) - 1):
            p1 = geofence_coordinates[i]
            p2 = geofence_coordinates[i + 1]
            if ((p1[1] > point["longitude"]) != (p2[1] > point["longitude"])) and (
                point["latitude"]
                < (p2[0] - p1[0]) * (point["longitude"] - p1[1]) / (p2[1] - p1[1])
                + p1[0]
            ):
                inside = not inside

        if geofence_type == "zone_entry" and inside:
            violated_geofences.append(point)

        elif geofence_type == "zone_exit" and not inside:
            violated_geofences.append(point)

    return violated_geofences


def haversine(coord1, coord2):
    """
    Calculate the great-circle distance between two points on the Earth using the Haversine formula.

    Parameters:
    coord1, coord2: tuple of floats
        Coordinates of the two points in the format (latitude, longitude).

    Returns:
    float
        Distance between the two points in kilometers.
    """
    rad = 6371  # Radius of the Earth in kilometers

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = rad * c
    return distance


def calculate_time_traveled(asset_coordinates_events, unit="minutes"):
    """
    Calculate the total time traveled given a set of asset coordinates and their speeds.

    Parameters:
    asset_coordinates_events: list of dictionaries
        List of asset coordinates in the format [{"lat": lat1, "lng": lon1, "speed": speed1}, ...].
    unit: str
        Unit of time to return the result in ('minutes' or 'seconds').

    Returns:
    float
        Total time traveled in the specified unit, rounded to the nearest whole number.
    """
    total_time_hours = 0.0

    # Calculate the time for each segment and sum them
    for i in range(len(asset_coordinates_events) - 1):
        point1 = asset_coordinates_events[i]
        point2 = asset_coordinates_events[i + 1]

        # Extract coordinates and speeds
        lat1, lon1, speed1 = point1["latitude"], point1["longitude"], point1["speed"]
        lat2, lon2, speed2 = point2["latitude"], point2["longitude"], point2["speed"]

        # Calculate distance between points using Haversine formula
        distance = haversine((lat1, lon1), (lat2, lon2))

        # Avoid division by zero: check if both speeds are zero
        if speed1 == 0 and speed2 == 0:
            continue

        # Use the average speed for the segment
        average_speed = (speed1 + speed2) / 2
        time_for_segment = distance / average_speed

        total_time_hours += time_for_segment

    # Convert total time to the specified unit
    if unit == "minutes":
        total_time = total_time_hours * 60
    elif unit == "seconds":
        total_time = total_time_hours * 3600
    else:
        raise ValueError("Invalid unit. Use 'minutes' or 'seconds'.")

    # Round the total time to the nearest whole number
    total_time_rounded = round(total_time)

    return total_time_rounded


def check_overspeeding(asset_coordinates_events, speed_limit):
    """
    Check for overspeeding in the given set of asset coordinates and their speeds.

    Parameters:
    asset_coordinates_events: list of dictionaries
        List of asset coordinates in the format [{"lat": lat1, "lng": lon1, "speed": speed1}, ...].
    speed_limit: float
        The speed limit to check against.

    Returns:
    list of dictionaries
        List of dictionaries containing the points and speeds that are greater than the speed limit.
    """
    overspeeding_points = []

    for point in asset_coordinates_events:
        if point["speed"] > speed_limit:
            overspeeding_points.append(point)

    return overspeeding_points


def calculate_average_speed(speeds: List[float]) -> float:
    if not speeds:
        return 0

    average_speed = sum(speeds) / len(speeds)
    return round(average_speed, 2)


def get_content_type(file_format: FileFormat) -> str:
    content_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "pdf": "application/pdf",
        "csv": "text/csv",
    }
    content_type = content_types.get(file_format.value)
    return content_type


def check_idle_time_exceeds_limit(events, idle_time_limit_minutes):
    """
    Check for idle periods exceeding the given limit.

    Parameters:
    events: list of dictionaries
        List of events in the format
        [{"lat": ..., "lng": ..., "speed": ..., "course": ..., "timestamp": ..., "event_type": ...}, ...].
    idle_time_limit_minutes: int
        The minimum idle time in minutes to be considered a violation.

    Returns:
    dict
        A dictionary with sorted events and a list of idle periods that exceed
        the given limit along with the total idle time for each period.
    """
    # Convert idle time limit from minutes to seconds
    idle_time_limit_seconds = idle_time_limit_minutes * 60

    # Sort events by timestamp
    events_sorted = sorted(
        events, key=lambda x: datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S")
    )

    idle_periods = []
    current_idle_period = []
    current_idle_start_time = None
    current_idle_end_time = None

    # Iterate through sorted events to detect idle periods
    for event in events_sorted:
        if event["event_type"] == "idle":
            if not current_idle_period:
                current_idle_start_time = datetime.strptime(
                    event["timestamp"], "%Y-%m-%d %H:%M:%S"
                )
            current_idle_period.append(event)
            current_idle_end_time = datetime.strptime(
                event["timestamp"], "%Y-%m-%d %H:%M:%S"
            )
        else:
            if current_idle_period:
                idle_duration = (
                    current_idle_end_time - current_idle_start_time
                ).total_seconds()
                if idle_duration > idle_time_limit_seconds:
                    idle_periods.append(
                        {
                            "events": current_idle_period,
                            "total_idle_time_seconds": idle_duration,
                        }
                    )
                current_idle_period = []
                current_idle_start_time = None
                current_idle_end_time = None

    # Check for any remaining idle period after the loop
    if current_idle_period:
        idle_duration = (
            current_idle_end_time - current_idle_start_time
        ).total_seconds()
        if idle_duration > idle_time_limit_seconds:
            idle_periods.append(
                {
                    "events": current_idle_period,
                    "total_idle_time_seconds": idle_duration,
                }
            )

    return idle_periods


def is_time_to_send_maintenance_alert(
    date_created_str, alert_schedule_period_days, alert_start_days_before: int = 3
):
    """
    Determines if it is time to send a maintenance alert for recurring alerts.

    :param date_created_str: The datetime string of when the policy was created in the format 'YYYY-MM-DD HH:MM:SS.sss +0000'.
    :param alert_schedule_period_days: The maintenance alert schedule period in days (int).
    :param alert_start_days_before: The number of days before the alert period to start notifying (int).
    :return: True if it's time to send the maintenance alert, False otherwise.
    """
    # Parse the datetime string to a datetime object
    date_created = datetime.fromisoformat(str(date_created_str)).date()

    current_date = datetime.now().date()  # Current date

    # Calculate the first alert date
    first_alert_date = date_created + timedelta(days=alert_schedule_period_days)
    next_alert_date = first_alert_date

    # Iterate to find the alert period that includes the current date
    while next_alert_date < current_date:
        next_alert_date += timedelta(days=alert_schedule_period_days)

    # Calculate the start date for sending alerts for the current alert period
    alert_start_date = next_alert_date - timedelta(days=alert_start_days_before)

    # Check if current date is within the alert start period
    return alert_start_date <= current_date <= next_alert_date


def calculate_total_idle_time_and_movement(
    events, idle_time_unit="minutes", accel_threshold=10, brake_threshold=-10
):
    """
    Calculate the total idle time, rapid acceleration, and braking events from a list of events.

    Parameters:
    events: list of dictionaries
        List of events in the format
        [{"lat": ..., "lng": ..., "speed": ..., "course": ..., "timestamp": ..., "event_type": ...}, ...].
    idle_time_unit: str, optional
        The time unit for the total idle time ('seconds', 'minutes', or 'hours'). Defaults to 'minutes'.
    accel_threshold: float, optional
        Speed change threshold for rapid acceleration. Defaults to 10 units (e.g., km/h).
    brake_threshold: float, optional
        Speed change threshold for rapid braking. Defaults to -10 units (e.g., km/h).

    Returns:
    dict
        A dictionary with sorted events, total idle time in the specified unit,
        and counts of rapid acceleration and braking events.
    """
    # Convert time unit to a factor
    time_unit_factors = {
        "seconds": 1,
        "minutes": 60,
        "hours": 3600,
    }
    if idle_time_unit not in time_unit_factors:
        raise ValueError(
            f"Unsupported time unit: {idle_time_unit}. Use 'seconds', 'minutes', or 'hours'."
        )

    events_sorted = sort_events_by_timestamp(events)
    total_idle_time_seconds = calculate_idle_time(events_sorted)
    rapid_acceleration_count, rapid_braking_count = detect_rapid_events(
        events_sorted, accel_threshold, brake_threshold
    )

    total_idle_time = round(
        total_idle_time_seconds / time_unit_factors[idle_time_unit], 2
    )

    return {
        "events_sorted": events_sorted,
        "total_idle_time": total_idle_time,
        "idle_time_unit": idle_time_unit,
        "rapid_acceleration_count": rapid_acceleration_count,
        "rapid_braking_count": rapid_braking_count,
    }


def sort_events_by_timestamp(events):
    """
    Sort events by timestamp.

    Parameters:
    events: list of dictionaries
        List of events with timestamps.

    Returns:
    list
        Sorted list of events by timestamp.
    """
    return sorted(
        events, key=lambda x: datetime.strptime(x["timestamp"], "%Y-%m-%d %H:%M:%S")
    )


def calculate_idle_time(events_sorted):
    """
    Calculate total idle time from sorted events.

    Parameters:
    events_sorted: list of dictionaries
        Sorted list of events.

    Returns:
    float
        Total idle time in seconds.
    """
    total_idle_time_seconds = 0
    idle_start_time = None

    for event in events_sorted:
        if event["event_type"] == "idle":
            if idle_start_time is None:
                idle_start_time = datetime.strptime(
                    event["timestamp"], "%Y-%m-%d %H:%M:%S"
                )
        else:
            if idle_start_time is not None:
                idle_end_time = datetime.strptime(
                    event["timestamp"], "%Y-%m-%d %H:%M:%S"
                )
                total_idle_time_seconds += (
                    idle_end_time - idle_start_time
                ).total_seconds()
                idle_start_time = None

    # Check for any remaining idle period after the loop
    if idle_start_time is not None:
        idle_end_time = datetime.strptime(
            events_sorted[-1]["timestamp"], "%Y-%m-%d %H:%M:%S"
        )
        total_idle_time_seconds += (idle_end_time - idle_start_time).total_seconds()

    return total_idle_time_seconds


def detect_rapid_events(events_sorted, accel_threshold, brake_threshold):
    """
    Detect rapid acceleration and braking events from sorted events.

    Parameters:
    events_sorted: list of dictionaries
        Sorted list of events.
    accel_threshold: float
        Speed change threshold for rapid acceleration.
    brake_threshold: float
        Speed change threshold for rapid braking.

    Returns:
    tuple
        Counts of rapid acceleration and braking events.
    """
    rapid_acceleration_count = 0
    rapid_braking_count = 0

    for i in range(1, len(events_sorted)):
        current_event = events_sorted[i]
        prev_event = events_sorted[i - 1]

        time_diff = (
            datetime.strptime(current_event["timestamp"], "%Y-%m-%d %H:%M:%S")
            - datetime.strptime(prev_event["timestamp"], "%Y-%m-%d %H:%M:%S")
        ).total_seconds()

        if time_diff > 0:
            speed_diff = current_event["speed"] - prev_event["speed"]
            acceleration_rate = speed_diff / time_diff

            if acceleration_rate >= accel_threshold:
                rapid_acceleration_count += 1
            elif acceleration_rate <= brake_threshold:
                rapid_braking_count += 1

    return rapid_acceleration_count, rapid_braking_count


async def upload_to_s3(file_name: str, file_content: bytes, content_type: str) -> str:
    s3_client = S3Client(
        aws_access_key=settings.AWS_ACCESS_KEY_ID,
        aws_secret_key=settings.AWS_SECRET_ACCESS_KEY,
        bucket_name=settings.S3_BUCKET,
    )
    return await s3_client.upload_file(file_name, file_content, content_type)


def calculate_gas_level_percentage(
    weight_of_empty_gas_cylinder: float,
    weight_of_full_gas_cylinder_and_gas: float,
    current_weight_of_cylinder_and_gas: float,
):
    """
    Calculate the gas level in percentage.

    Args:
    weight_of_empty_gas_cylinder (float): The weight of the empty gas cylinder.
    weight_of_full_gas_cylinder (float): The weight of the full gas cylinder.
    current_weight_of_cylinder (float): The current weight of the gas cylinder (with the gas).

    Returns:
    float: The gas level in percentage.
    """
    # calculate the current gas weight without cylinder weight
    current_gas_weight_only = (
        current_weight_of_cylinder_and_gas - weight_of_empty_gas_cylinder
    )

    # calculate total gas weight without cylinder
    total_gas_weight_only = (
        weight_of_full_gas_cylinder_and_gas - weight_of_empty_gas_cylinder
    )

    # calculate total gas weight in percentage
    gas_level_percentage = (current_gas_weight_only / total_gas_weight_only) * 100

    return gas_level_percentage


def load_gas_device_serial_number_from_csv(csv_url: str):
    try:
        df = pd.read_csv(csv_url)
        return df["device_serial_number"].tolist()
    except Exception as e:
        raise e


def convert_date_format(date_str):
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Format the datetime object into the desired string format
    formatted_date = date_obj.strftime("%d/%m/%Y")

    return formatted_date

