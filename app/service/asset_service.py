import uuid

from app.core import messages
from app.core.constants import FREE_PACKAGE, FREE_PACKAGE_ITEMS
from app.core.exceptions import NotFoundError, UnAuthorizedError, BadRequestError
from app.repository.asset_repository import AssetRepository
from app.repository.asset_type_repository import AssetTypeRepository
from app.repository.device_repository import DeviceRepository
from app.repository.driver_repository import DriverRepository
from app.repository.equipment_repository import EquipmentRepository
from app.repository.equipment_type_repository import EquipmentTypeRepository
from app.repository.gas_cylinder_event_repository import GasCylinderEventRepository
from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.repository.immobilizer_report_repository import ImmobilizerReportRepository
from app.repository.subscription_repository import SubscriptionRepository
from app.repository.theft_incidence_repository import TheftIncidenceRepository
from app.repository.theft_report_repository import TheftReportRepository
from app.repository.tracking_event_repository import TrackingEventRepository
from app.repository.user_repository import UserRepository
from app.repository.user_subscription_repository import UserSubscriptionRepository
from app.repository.vehicle_owner_repository import VehicleOwnerRepository
from app.service.asset_operator_assignment_service import AssetOperatorAssignmentService
from app.repository.activity_log_repository import ActivityLogRepository

from app.schema.asset_schema import (
    AssetInput,
    AssetPayload,
    AssignDeviceInputPayload,
    PatchAssetPayload,
    TheftIncidencePayload,
    TheftReportPayload,
    ThirdPartyAssetInput,
    ThirdPartyAssetPayload,
    VehicleOwnerInput,
)
from app.service.base_service import BaseService
from app.transfomers.asset_transformer import asset_transformer
from app.util.enums import (
    AccountType,
    AlertPolicy,
    AssetCreators,
    AssetStatus,
    GeofenceTypeUuid,
    PackageItemTrackerType,
    ActivityLogClass,
    ActivityLogType,
)
from app.util.utils import (
    calculate_average_speed,
    calculate_time_traveled,
    calculate_total_fuel_used,
    calculate_total_idle_time_and_movement,
    convert_date_format_to_iso,
    get_distance_travelled_by_coordinates,
    get_status,
)
from app.schema.activity_log_schema import ActivityLogSchema
from app.core import activity_log_constants
from fastapi import Request

class AssetService(BaseService):
    def __init__(
        self,
        asset_repository: AssetRepository,
        asset_type_repository: AssetTypeRepository,
        user_repository: UserRepository,
        equipment_repository: EquipmentRepository,
        equipment_type_repository: EquipmentTypeRepository,
        driver_repository: DriverRepository,
        subscription_repository: SubscriptionRepository,
        device_repository: DeviceRepository,
        immobilizer_report_repository: ImmobilizerReportRepository,
        theft_incidence_repository: TheftIncidenceRepository,
        theft_report_repository: TheftReportRepository,
        vehicle_owner_repository: VehicleOwnerRepository,
        tracking_event_repository: TrackingEventRepository,
        gas_cylinder_repository: GasCylinderRepository,
        gas_cylinder_event_repository: GasCylinderEventRepository,
        user_subscription_repository: UserSubscriptionRepository,
        asset_operator_assignment_service: AssetOperatorAssignmentService,
        activity_log_repository: ActivityLogRepository,

    ):
        self.asset_repository = asset_repository
        self.asset_type_repository = asset_type_repository
        self.user_repository = user_repository
        self.equipment_repository = equipment_repository
        self.equipment_type_repository = equipment_type_repository
        self.driver_repository = driver_repository
        self.subscription_repository = subscription_repository
        self.user_subscription_repository = user_subscription_repository
        self.device_repository = device_repository
        self.immobilizer_report_repository = immobilizer_report_repository
        self.theft_incidence_repository = theft_incidence_repository
        self.theft_report_repository = theft_report_repository
        self.vehicle_owner_repository = vehicle_owner_repository
        self.tracking_event_repository = tracking_event_repository
        self.gas_cylinder_repository = gas_cylinder_repository
        self.gas_cylinder_event_repository = gas_cylinder_event_repository
        self.asset_operator_assignment_service = asset_operator_assignment_service
        self.activity_log_repository = activity_log_repository

        super().__init__(asset_repository)

    def create_asset(self, asset: AssetPayload,request: Request):
        try:
            user = self.get_user(asset.user_uuid)

            email_address = user.get("email_address")

            user_subscription = self.get_user_subscription(email_address)

            number_of_assets = self.get_filtered_package_item(user_subscription)

            if user.get("account_type") == AccountType.INDIVIDUAL:
                self.check_asset_creation_limit(
                    user_uuid=user.get("uuid"), number_of_assets=number_of_assets
                )

            if user.get("account_type") == AccountType.BUSINESS:
                self.check_asset_creation_limit(
                    business_uuid=user.get("business_profile").uuid,
                    number_of_assets=number_of_assets,
                )

            self.check_existing_asset(asset)

            if asset.add_driver:
                created_asset = self.create_asset_with_driver(asset)
            else:
                created_asset = self.create_asset_without_driver(asset)

            self.activity_log_repository.create(
                ActivityLogSchema(
                   activity_title=activity_log_constants.CREATE_ASSET,
                   activity_class=ActivityLogClass.USER,
                   activity_type=ActivityLogType.CREATE_ASSET,
                   activity_description=activity_log_constants.CREATE_ASSET_DESC.format(
                          email=user.get("email_address"), asset_name=asset.asset_name
                    ),
                    user_uuid=str(user.get("uuid")),
                    business_profile_uuid=str(user.get("business_profile").uuid),
                    ip_address=request.client.host
                )
            )

            return created_asset

        except Exception as e:
            raise e

    def create_third_party_asset(self, asset: ThirdPartyAssetPayload):
        try:
            self.asset_repository.read_by_vin_serial_number_license_no(
                vehicle_license_no=asset.vehicle_license_no, vin=asset.vin
            )

            if self.equipment_repository.read_by_uuid(asset.equipment_uuid) is None:
                raise NotFoundError(
                    detail=messages.EQUIPMENT_NOT_FOUND + str(asset.equipment_uuid)
                )

            created_asset = self.create_asset_with_vehicle_owner(asset)

            return created_asset

        except Exception as e:
            raise e

    def get_user(self, user_uuid):
        user = self.user_repository.get_user_by_uuid(user_uuid)
        if not user:
            raise Exception("User not found")
        return user

    def get_user_subscription(self, email_address: str):
        user_subscription = self.user_subscription_repository.get_user_subscription(
            email_address
        )

        if user_subscription and user_subscription.subscription_code:
            paystack_subscription = (
                self.subscription_repository.get_paystack_subscription(
                    user_subscription.subscription_code
                )
            )

            user_package = {
                "package_name": paystack_subscription["plan"]["name"],
                "package_items": paystack_subscription["package_items"],
            }
            return user_package
        else:
            user_package = {
                "package_name": FREE_PACKAGE,
                "package_items": FREE_PACKAGE_ITEMS,
            }
            return user_package

    def get_filtered_package_item(self, user_subscription: dict):
        package_name = user_subscription.get("package_name")
        package_items = user_subscription.get("package_items")

        if package_name == FREE_PACKAGE:
            filtered_package_item = next(
                (
                    item.get("package_item")
                    for item in package_items
                    if item.get("package_item").get("type")
                    == PackageItemTrackerType.ASSET_QUANTITY_TRACKER
                ),
                None,
            )
            number_of_asset = filtered_package_item.get("number_of_assets")
        else:
            filtered_package_item = next(
                (
                    item.package_item
                    for item in package_items
                    if item.package_item.type
                    == PackageItemTrackerType.ASSET_QUANTITY_TRACKER
                ),
                None,
            )
            number_of_asset = filtered_package_item.number_of_assets
        return number_of_asset

    def check_asset_creation_limit(
        self, number_of_assets: int, user_uuid: str = None, business_uuid: str = None
    ):
        if business_uuid is not None:
            user_assets = len(
                self.get_assets_by_business_uuid_no_pagination(business_uuid)
            )

        if user_uuid is not None:
            user_assets = len(self.get_assets_by_user_uuid_no_pagination(user_uuid))

        if user_assets >= number_of_assets:
            raise BadRequestError("You have reached the maximum number of assets you can create. Please subscribe for a higher package.")

    def check_existing_asset(self, asset):
        existing_asset = self.asset_repository.read_by_vin_serial_number_license_no(
            asset.vin, asset.serial_number, asset.vehicle_license_no
        )
        if existing_asset:
            raise Exception(
                "Asset with provided VIN, serial number, or vehicle license number already exists."
            )
        return existing_asset

    def check_asset_dependencies(self, asset):
        if self.user_repository.read_by_uuid(asset.user_uuid) is None:
            raise NotFoundError(detail=messages.USER_NOT_FOUND + str(asset.user_uuid))

        if self.asset_type_repository.read_by_uuid(asset.asset_type_uuid) is None:
            raise NotFoundError(
                detail=messages.ASSET_TYPE_NOT_FOUND + str(asset.asset_type_uuid)
            )

        if self.equipment_repository.read_by_uuid(asset.equipment_uuid) is None:
            raise NotFoundError(
                detail=messages.EQUIPMENT_NOT_FOUND + str(asset.equipment_uuid)
            )

    def create_asset_with_driver(self, asset):
        if self.user_repository.read_by_uuid(asset.driver_uuid) is None:
            raise NotFoundError(
                detail=messages.DRIVER_NOT_FOUND + str(asset.driver_uuid)
            )

        created_asset = self.asset_repository.create(AssetInput(**asset.dict()))

        self.asset_operator_assignment_service.assign_operator_to_asset(
            str(created_asset.uuid),
            str(asset.driver_uuid),
            str(created_asset.user_uuid),
            str(created_asset.business_profile_uuid)
        )

        created_asset_data = {
            "user_uuid": created_asset.user_uuid,
            "business_profile_uuid": created_asset.business_profile_uuid,
            "asset_type_uuid": created_asset.asset_type_uuid,
            "asset_name": created_asset.asset_name,
            "image_url": created_asset.image_url,
            "vehicle_license_no": created_asset.vehicle_license_no,
            "asset_status": created_asset.asset_status,
            "equipment_type_uuid": created_asset.equipment_type_uuid,
            "device_imei": created_asset.device_imei,
            "vin": created_asset.vin,
            "marker_color": created_asset.marker_color,
            "equipment_uuid": created_asset.equipment_uuid,
            "serial_number": created_asset.serial_number,
            "make": created_asset.make,
            "model": created_asset.model,
        }
        return created_asset_data

    def create_asset_with_vehicle_owner(self, asset):
        vehicle_owner_data = VehicleOwnerInput(
            first_name=asset.first_name,
            last_name=asset.last_name,
            phone_number=asset.phone_number,
            email_address=asset.email_address,
            residential_address=asset.residential_address,
        )
        created_vehicle_owner = self.vehicle_owner_repository.create(vehicle_owner_data)
        if created_vehicle_owner:
            asset_data = ThirdPartyAssetInput(
                asset_type_uuid="fb1e96de-d79d-463b-b6c7-aeab8235d676",
                asset_status=AssetStatus.PENDING_INSTALLATION,
                usage_type=asset.usage_type,
                created_by=AssetCreators.DVLA,
                vin=asset.vin,
                vehicle_license_no=asset.vehicle_license_no,
                equipment_uuid=asset.equipment_uuid,
                make=asset.make,
                model=asset.model,
                image_url=asset.image_url,
                vehicle_owner_uuid=created_vehicle_owner.uuid,
            )

            created_asset = self.asset_repository.create(asset_data)

            created_asset_data = {
                "usage_type": created_asset.usage_type,
                "vehicle_license_no": created_asset.vehicle_license_no,
                "asset_status": created_asset.asset_status,
                "vin": created_asset.vin,
                "equipment_uuid": created_asset.equipment_uuid,
                "make": created_asset.make,
                "model": created_asset.model,
                "image_url": created_asset.image_url,
                "vehicle_owner": created_vehicle_owner,
            }
            return created_asset_data

    def create_asset_without_driver(self, asset):
        created_asset = self.asset_repository.create(AssetInput(**asset.dict()))
        return created_asset

    def get_assets_by_user_uuid(
        self, user_uuid: str, asset_type_uuid: str = None, page=1, page_size=10
    ):
        try:
            return self.asset_repository.read_all_assets_by_uuid(
                user_uuid=user_uuid,
                page_size=page_size,
                page=page,
                asset_type_uuid=asset_type_uuid,
            )
        except Exception as e:
            raise e

    def get_assets_by_business_uuid(
        self,
        business_uuid: str,
        asset_type_uuid: str = None,
        page=1,
        page_size=10,
        search: str = None,
        status: str = None,
    ):
        try:
            return self.asset_repository.read_all_assets_by_uuid(
                business_uuid=business_uuid,
                page_size=page_size,
                page=page,
                asset_type_uuid=asset_type_uuid,
                search_query=search,
                status=status
            )
        except Exception as e:
            raise e

    def read_assigned_assets(
        self,
        operator_uuid: str,
        business_uuid: str,
        asset_type_uuid: str = None,
        page=1,
        page_size=10,
        search: str = None,
    ):
        try:
            return self.asset_repository.read_assigned_assets_by_uuid(
                operator_uuid=operator_uuid,
                business_uuid=business_uuid,
                page_size=page_size,
                page=page,
                asset_type_uuid=asset_type_uuid,
                search_query=search,
            )
        except Exception as e:
            raise e

    def get_assets_by_user_uuid_no_pagination(self, user_uuid: str):
        try:
            return self.asset_repository.read_all_assets_by_uuid_no_pagination(
                user_uuid=user_uuid
            )
        except Exception as e:
            raise e

    def get_assets_by_business_uuid_no_pagination(self, business_uuid: str):
        try:
            return self.asset_repository.read_all_assets_by_uuid_no_pagination(
                business_uuid=business_uuid
            )
        except Exception as e:
            raise e

    def get_third_stolen_assets(
        self, asset_type_uuid: str = None, page=1, page_size=10
    ):
        try:
            return self.asset_repository.read_all_stolen_assets(
                asset_type_uuid, page, page_size
            )
        except Exception as e:
            raise e

    def get_third_party_assets(self, asset_type_uuid: str = None, page=1, page_size=10):
        try:
            return self.asset_repository.read_all_third_party_assets(
                asset_type_uuid, page, page_size
            )
        except Exception as e:
            raise e

    def assign_device_imei(self, uuid: str, payload: AssignDeviceInputPayload):
        try:
            asset = self.asset_repository.assign_device_imei(uuid, payload)
            return asset
        except Exception as e:
            raise e

    def get_assets_by_license_no(self, vehicle_license_no: str):
        try:
            return self.asset_repository.get_asset_by_license_no(vehicle_license_no)
        except Exception as e:
            raise e

    def report_immobilizer_activity(self, payload):
        try:
            report = self.immobilizer_report_repository.create(payload)
            return report
        except Exception as e:
            raise e

    def report_theft_activity(self, payload: TheftIncidencePayload):
        try:
            report = self.theft_incidence_repository.create(payload)
            return report
        except Exception as e:
            raise e

    def update_asset_stolen_status_to_true(self, asset_uuid: str):
        try:
            report = self.asset_repository.update_asset_stolen_status_to_true(
                asset_uuid
            )
            return report
        except Exception as e:
            raise e

    def update_asset_stolen_status_to_false(self, asset_uuid: str):
        try:
            report = self.asset_repository.update_asset_stolen_status_to_false(
                asset_uuid
            )
            return report
        except Exception as e:
            raise e

    def create_initial_incident_report(self, payload: TheftReportPayload):
        try:
            report = self.theft_report_repository.create(payload)
            return report
        except Exception as e:
            raise e

    def get_all_theft_incidence(
        self,
        page=1,
        page_size=10,
        search_query=None,
        start_date=None,
        end_date=None,
        status=None,
    ):
        try:
            incidences = self.theft_incidence_repository.get_all_incidence(
                page=page,
                page_size=page_size,
                search_query=search_query,
                status=status,
                start_date=start_date,
                end_date=end_date,
            )
            return incidences
        except Exception as e:
            raise e

    def mark_as_resolved(self, incidence_uuid: str):
        try:
            incident = self.theft_incidence_repository.mark_as_resolve(incidence_uuid)
            return incident
        except Exception as e:
            raise e

    def get_incident_reports(self, incidence_uuid: str):
        try:
            report = self.theft_report_repository.get_incident_reports(incidence_uuid)
            return report
        except Exception as e:
            raise e

    def get_last_immobilizer_action(self, asset_uuid: str):
        try:
            action = self.immobilizer_report_repository.get_last_immobilizer_action(
                asset_uuid
            )
            return action
        except Exception as e:
            raise e

    def shutdown_engine(self, asset_uuid: uuid):
        try:
            asset = self.get_by_uuid(asset_uuid)
            if asset.device_imei:
                asset_device = self.device_repository.get_device_for_engine_shutdown(
                    asset.device_imei
                )
                return asset_device
            else:
                raise NotFoundError(
                    f"There is no device associated with this asset:{asset.asset_name} "
                )
        except Exception as e:
            raise e

    def generate_gas_cylinder_report(
        self,
        start_date: str,
        end_date: str,
        business_uuid: str = None,
        user_uuid: str = None,
        cylinder_uuid: str = None,
    ):
        try:
            report = []

            # Initialize assets as an empty list
            gas_cylinders = []

            # Fetch assets based on provided parameters
            if business_uuid or user_uuid or cylinder_uuid:
                gas_cylinders = self.get_gas_cylinders(
                    business_uuid, user_uuid, cylinder_uuid
                )

            for cylinder in gas_cylinders:
                if cylinder.gas_device_serial_number:
                    # Get asset points for today in tracking events table
                    cylinder_events = self.gas_cylinder_event_repository.read_all_gas_events_by_date_range(
                        cylinder.gas_device_serial_number, start_date, end_date
                    )
                    return cylinder_events

            return report

        except Exception as e:
            raise e

    def generate_distance_speed_report(
        self,
        start_date: str,
        end_date: str,
        business_uuid: str = None,
        user_uuid: str = None,
        asset_uuid: str = None,
        asset_type_uuid: str = None,
    ):
        try:
            report = []

            # Initialize assets as an empty list
            assets = []

            # Fetch assets based on provided parameters
            if business_uuid or user_uuid or asset_uuid or asset_type_uuid:
                assets = self.get_assets(
                    business_uuid=business_uuid,
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                )

            for asset in assets:
                if asset.device_imei:
                    # Get asset points for today in tracking events table
                    asset_events = self.tracking_event_repository.read_all_events_by_device_imei_date_range(
                        asset.device_imei, start_date, end_date
                    )

                    speed_violations = (
                        self.asset_repository.get_over_speeding_violations(
                            asset.uuid,
                            GeofenceTypeUuid.OVER_SPEEDING_ALERT_POLICY,
                            start_date,
                            end_date,
                        )
                    )

                    # Extract coordinates from asset events
                    coordinates = [
                        {
                            "latitude": event.latitude,
                            "longitude": event.longitude,
                            "speed": event.speed,
                            "timestamp": str(event.event_datetime),
                            "event_type": get_status(event.event_type),
                            "fuel_level": event.fuel_level,
                        }
                        for event in asset_events
                    ]

                    # Calculate distance traveled
                    distance_traveled = get_distance_travelled_by_coordinates(
                        coordinates
                    )

                    # Extract speeds from asset tracking event
                    speeds = [event.speed for event in asset_events]

                    # Calculate average speed
                    average_speed = calculate_average_speed(speeds)

                    # Calculate time traveled
                    time_traveled = calculate_time_traveled(coordinates)

                    total_fuel_used = calculate_total_fuel_used(coordinates)

                    # Calculate total idle time
                    total_idle_time = calculate_total_idle_time_and_movement(
                        coordinates
                    )

                    # Append the result
                    report.append(
                        {
                            "asset_name": asset.asset_name,
                            "asset_type_uuid": asset.asset_type_uuid,
                            "distance_traveled": distance_traveled,
                            "average_speed": average_speed,
                            "time_traveled": time_traveled,
                            "total_idle_time": total_idle_time.get("total_idle_time"),
                            "rapid_acceleration": total_idle_time.get(
                                "rapid_acceleration_count"
                            ),
                            "rapid_breaking": total_idle_time.get(
                                "rapid_braking_count"
                            ),
                            "speed_violations": len(speed_violations),
                            "fuel_used": total_fuel_used,  # Placeholder for fuel used
                        }
                    )
            return report

        except Exception as e:
            raise e

    def get_assets(
        self, business_uuid=None, user_uuid=None, asset_uuid=None, asset_type_uuid=None
    ):
        assets = []

        if business_uuid:
            if asset_type_uuid:
                assets = self.asset_repository.read_all_assets_by_uuid_no_pagination(
                    business_uuid=business_uuid, asset_type_uuid=asset_type_uuid
                )
            elif asset_uuid:
                assets = self.asset_repository.read_all_assets_by_uuid_no_pagination(
                    asset_uuid=asset_uuid, business_uuid=business_uuid
                )
            else:
                assets = self.asset_repository.read_all_assets_by_uuid_no_pagination(
                    business_uuid=business_uuid
                )
        elif user_uuid:
            if asset_type_uuid:
                assets = self.asset_repository.read_all_assets_by_uuid_no_pagination(
                    user_uuid=user_uuid, asset_type_uuid=asset_type_uuid
                )
            elif asset_uuid:
                assets = self.asset_repository.read_all_assets_by_uuid_no_pagination(
                    asset_uuid=asset_uuid, user_uuid=user_uuid
                )
            else:
                assets = self.asset_repository.read_all_assets_by_uuid_no_pagination(
                    user_uuid=user_uuid
                )

        return assets

    def get_gas_cylinders(self, business_uuid=None, user_uuid=None, cylinder_uuid=None):
        assets = []

        if business_uuid:
            if cylinder_uuid:
                assets = self.gas_cylinder_repository.read_all_cylinders_no_pagination(
                    cylinder_uuid=cylinder_uuid, business_uuid=business_uuid
                )
            else:
                assets = self.gas_cylinder_repository.read_all_cylinders_no_pagination(
                    business_uuid=business_uuid
                )
        elif user_uuid:
            if cylinder_uuid:
                assets = self.gas_cylinder_repository.read_all_cylinders_no_pagination(
                    cylinder_uuid=cylinder_uuid, user_uuid=user_uuid
                )
            else:
                assets = self.gas_cylinder_repository.read_all_cylinders_no_pagination(
                    user_uuid=user_uuid
                )

        return assets

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
                    convert_date_format_to_iso(start_date),
                    convert_date_format_to_iso(end_date),
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "over_speeding_violations": self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.OVER_SPEEDING_ALERT_POLICY,
                    convert_date_format_to_iso(start_date),
                    convert_date_format_to_iso(end_date),
                    business_uuid=business_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "idling_violations": self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.IDLING_ALERT_POLICY,
                    convert_date_format_to_iso(start_date),
                    convert_date_format_to_iso(end_date),
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
                    convert_date_format_to_iso(start_date),
                    convert_date_format_to_iso(end_date),
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "over_speeding_violations": self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.OVER_SPEEDING_ALERT_POLICY,
                    convert_date_format_to_iso(start_date),
                    convert_date_format_to_iso(end_date),
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                ),
                "idling_violations": self.asset_repository.get_violations_by_alert_type(
                    GeofenceTypeUuid.IDLING_ALERT_POLICY,
                    convert_date_format_to_iso(start_date),
                    convert_date_format_to_iso(end_date),
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

    def generate_violation_reminder_report(
        self,
        start_date: str,
        end_date: str,
        business_uuid: str = None,
        user_uuid: str = None,
        asset_uuid: str = None,
        asset_type_uuid: str = None,
    ):
        try:
            # Fetch violations reminders based on provided parameters
            violations = self.get_violations_reminders(
                start_date,
                end_date,
                business_uuid,
                user_uuid,
                asset_uuid,
                asset_type_uuid,
            )

            if not violations:
                violations = {}
            # Initialize assets as an empty list
            assets = []

            if business_uuid or user_uuid or asset_uuid or asset_type_uuid:
                assets = self.get_assets(
                    business_uuid=business_uuid,
                    user_uuid=user_uuid,
                    asset_uuid=asset_uuid,
                    asset_type_uuid=asset_type_uuid,
                )

            # Calculate total distances for current and past ranges
            (
                total_distance_traveled_current_range,
                total_distance_traveled_past_range,
                fuel_level_current_range,
                fuel_level_past_range,
            ) = self.calculate_total_distance(assets, start_date, end_date)

            if fuel_level_current_range == 0:
                fuel_efficiency_current_range = 0
            else:
                fuel_efficiency_current_range = round(
                    total_distance_traveled_current_range / fuel_level_current_range, 2
                )
            if fuel_level_past_range == 0:
                fuel_efficiency_past_range = 0
            else:
                fuel_efficiency_past_range = round(
                    total_distance_traveled_past_range / fuel_level_past_range, 2
                )

            # Construct the report dictionary
            report = {
                "geofence_violations": len(violations.get("geofence_violations", [])),
                "over_speeding_violations": len(
                    violations.get("over_speeding_violations", [])
                ),
                "idling_violations": len(violations.get("idling_violations", [])),
                "oil_change": len(violations.get("oil_change", [])),
                "break_inspection": len(violations.get("break_inspection", [])),
                "tire_rotation": len(violations.get("tire_rotation", [])),
                "general_servicing": len(violations.get("general_servicing", [])),
                "others": len(violations.get("others", [])),
                "total_distance_traveled_current_range": round(
                    total_distance_traveled_current_range, 2
                ),
                "total_distance_traveled_past_range": round(
                    total_distance_traveled_past_range, 2
                ),
                "total_fuel_used_current_range": fuel_level_current_range,
                "total_fuel_used_past_range": fuel_level_past_range,
                "fuel_efficiency_current_range": fuel_efficiency_current_range,
                "fuel_efficiency_past_range": fuel_efficiency_past_range,
            }

            return report

        except Exception as e:
            raise e

    def edit_asset(
        self,
        asset_uuid: str,
        payload: PatchAssetPayload,
        user_uuid: str = None,
        business_uuid: str = None,
    ):
        try:
            asset = self.asset_repository.read_by_uuid(asset_uuid)
            if not asset:
                raise NotFoundError(detail=messages.ASSET_NOT_FOUND + str(asset_uuid))

            if user_uuid and asset.user_uuid != user_uuid:
                raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)

            if business_uuid and asset.business_profile_uuid != business_uuid:
                print(type(business_uuid))
                print(type(asset.business_profile_uuid))
                raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)

            update_asset = self.asset_repository.update_by_uuid(asset_uuid, payload)

            return asset_transformer(update_asset)

        except Exception as e:
            raise e
