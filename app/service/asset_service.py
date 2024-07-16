import uuid

from app.core import messages
from app.core.constants import FREE_PACKAGE
from app.core.exceptions import NotFoundError
from app.repository.asset_repository import AssetRepository
from app.repository.asset_type_repository import AssetTypeRepository
from app.repository.device_repository import DeviceRepository
from app.repository.driver_repository import DriverRepository
from app.repository.equipment_repository import EquipmentRepository
from app.repository.equipment_type_repository import EquipmentTypeRepository
from app.repository.immobilizer_report_repository import ImmobilizerReportRepository
from app.repository.subscription_repository import SubscriptionRepository
from app.repository.theft_incidence_repository import TheftIncidenceRepository
from app.repository.theft_report_repository import TheftReportRepository
from app.repository.tracking_event_repository import TrackingEventRepository
from app.repository.user_repository import UserRepository
from app.repository.vehicle_owner_repository import VehicleOwnerRepository
from app.schema.asset_schema import (
    AssetInput,
    AssetPayload,
    AssignDeviceInputPayload,
    TheftIncidencePayload,
    TheftReportPayload,
    ThirdPartyAssetInput,
    ThirdPartyAssetPayload,
    VehicleOwnerInput,
)
from app.service.base_service import BaseService
from app.util.enums import (
    AccountType,
    AssetCreators,
    AssetStatus,
    PackageItemTrackerType,
)
from app.util.utils import get_distance_travelled_by_coordinates


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
    ):
        self.asset_repository = asset_repository
        self.asset_type_repository = asset_type_repository
        self.user_repository = user_repository
        self.equipment_repository = equipment_repository
        self.equipment_type_repository = equipment_type_repository
        self.driver_repository = driver_repository
        self.subscription_repository = subscription_repository
        self.device_repository = device_repository
        self.immobilizer_report_repository = immobilizer_report_repository
        self.theft_incidence_repository = theft_incidence_repository
        self.theft_report_repository = theft_report_repository
        self.vehicle_owner_repository = vehicle_owner_repository
        self.tracking_event_repository = tracking_event_repository
        super().__init__(asset_repository)

    def create_asset(self, asset: AssetPayload):
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

            self.check_asset_dependencies(asset)

            if asset.add_driver:
                created_asset = self.create_asset_with_driver(asset)
            else:
                created_asset = self.create_asset_without_driver(asset)

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
        user_subscription = (
            self.subscription_repository.get_paystack_subscription_by_email(
                email=email_address
            )
        )
        return user_subscription

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
            raise Exception(
                "You have reached the maximum number of assets you can create. Please subscribe for a higher package."
            )

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
        if self.driver_repository.read_by_uuid(asset.driver_uuid) is None:
            raise NotFoundError(
                detail=messages.DRIVER_NOT_FOUND + str(asset.driver_uuid)
            )
        created_asset = self.asset_repository.create(AssetInput(**asset.dict()))
        updated_driver = self.driver_repository.update_driver_asset(
            created_asset.uuid, asset.driver_uuid
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
            "driver": updated_driver,
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
    ):
        try:
            return self.asset_repository.read_all_assets_by_uuid(
                business_uuid=business_uuid,
                page_size=page_size,
                page=page,
                asset_type_uuid=asset_type_uuid,
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

    def get_all_theft_incidence(self):
        try:
            report = self.theft_incidence_repository.get_all_incidence()
            return report
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

    def generate_distance_traveled_user_report(self, user_uuid: str):
        try:
            user_assets = self.asset_repository.read_all_assets_by_uuid_no_pagination(
                user_uuid=user_uuid
            )
            return user_assets
        except Exception as e:
            raise e

    def generate_distance_traveled_report(
        self,
        start_date: str,
        end_date: str,
        business_uuid: str = None,
        user_uuid: str = None,
    ):
        try:
            report = []
            if business_uuid:
                assets = self.asset_repository.read_all_assets_by_uuid_no_pagination(
                    business_uuid=business_uuid
                )
            if user_uuid:
                assets = self.asset_repository.read_all_assets_by_uuid_no_pagination(
                    user_uuid=user_uuid
                )

            for asset in assets:
                if asset.device_imei:
                    # Get asset points for today in tracking events table
                    asset_events = self.tracking_event_repository.read_all_events_by_device_imei_date_range(
                        asset.device_imei, start_date, end_date
                    )

                    # Extract coordinates from asset events
                    coordinates = [
                        {"latitude": event.latitude, "longitude": event.longitude}
                        for event in asset_events
                    ]

                    # Calculate distance traveled
                    distance_traveled = get_distance_travelled_by_coordinates(
                        coordinates
                    )

                    # Append the result
                    report.append(
                        {
                            "asset_name": asset.asset_name,
                            "distance_traveled": distance_traveled,
                        }
                    )

            return report

        except Exception as e:
            raise e
