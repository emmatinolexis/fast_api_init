import math
import secrets
import uuid
from typing import Any, List, Union

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from geopy.distance import geodesic

from app.client.s3_client import S3Client
from app.core.constants import ADMIN_USER_ROLE, CUSTOMER_USER_ROLE, THIRD_PARTY_APP_ROLE
from app.core.logger import get_logger
from app.core.security import JWTBearer
from app.core.settings import settings
from app.util.enums import ActiveStatus

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


def get_distance_travelled_by_coordinates(coordinates: Union[List[dict], List[tuple]]):
    """
    Calculate the total distance traveled given sets of coordinates
    :param coordinates: List of dictionaries or list of tuples where each dictionary contains "latitude" and "longitude"
    :return: Total distance traveled as float
    """
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


def check_violated_geofence(asset_coordinates, geofence_coordinates, geofence_type):
    """
    Check which geofences are violated by the given set of car points.

    Args:
    - asset_coordinates: list of tuples representing the points from the car (latitude, longitude)
    - geofence_coordinates: list of tuples representing the coordinates of the geofence
    - geofence_type: string indicating the type of geofence ('zone_exit' or 'zone_entry')

    Returns:
    - list of tuples representing the coordinates of violated geofences
    """
    violated_geofences = []
    for point in asset_coordinates:
        # Check if the point is inside or outside the geofence based on geofence_type
        inside = False
        for i in range(len(geofence_coordinates) - 1):
            p1 = geofence_coordinates[i]
            p2 = geofence_coordinates[i + 1]
            if ((p1[1] > point[1]) != (p2[1] > point[1])) and (
                    point[0]
                    < (p2[0] - p1[0]) * (point[1] - p1[1]) / (p2[1] - p1[1]) + p1[0]
            ):
                inside = not inside

        if geofence_type == "zone_entry" and inside:
            # violated_geofences.append(point)
            violated_geofences.append(point)

        elif geofence_type == "zone_exit" and not inside:
            # violated_geofences.append(point)
            violated_geofences.append(point)

    return violated_geofences


async def upload_to_s3(file_name: str, file_content: bytes, content_type: str) -> str:
    s3_client = S3Client(
        aws_access_key=settings.AWS_ACCESS_KEY_ID,
        aws_secret_key=settings.AWS_SECRET_ACCESS_KEY,
        bucket_name=settings.S3_BUCKET,
    )
    return await s3_client.upload_file(file_name, file_content, content_type)
