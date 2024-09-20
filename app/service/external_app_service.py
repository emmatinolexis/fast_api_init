from app.core.security import generate_access_token_for_third_party_app
from app.repository.device_configuration_repository import DeviceConfigurationRepository
from app.repository.external_app_repository import ExternalAppRepository
from app.repository.peripheral_devices_repository import PeripheralDeviceRepository
from app.schema.external_app_schema import (
    ExternalAppGenerateTokenPayload,
    ExternalAppPayload,
)
from app.service.base_service import BaseService
from app.util.enums import PeripheralDeviceType, UserRole
from app.util.utils import days_to_minutes


class ExternalAppService(BaseService):
    def __init__(
        self,
        external_app_repository: ExternalAppRepository,
        peripheral_devices_repository: PeripheralDeviceRepository,
        device_configuration_repository: DeviceConfigurationRepository,
    ):
        self.external_app_repository = external_app_repository
        self.peripheral_devices_repository = peripheral_devices_repository
        self.device_configuration_repository = device_configuration_repository
        super().__init__(external_app_repository)

    def create_external_app(self, payload: ExternalAppPayload):
        try:
            external_app = self.external_app_repository.create_external_app(payload)
            return external_app
        except Exception as e:
            raise e

    def get_app_service_by_secret_key(self, secret_key: str):
        try:
            external_app = self.external_app_repository.get_app_service_by_secret_key(
                secret_key
            )
            return external_app
        except Exception as e:
            raise e

    def generate_token(self, payload: ExternalAppGenerateTokenPayload):
        try:
            external_app = self.external_app_repository.get_app_service(payload)
            expiry_minutes = days_to_minutes(external_app.no_of_days_to_expire)
            if payload.requires_conf:
                device_configuration = (
                    self.device_configuration_repository.get_configuration_by_type(
                        PeripheralDeviceType.GATEWAY_DEVICE
                    )
                )
                gateway_device = (
                    self.peripheral_devices_repository.get_by_serial_number(
                        payload.serial_number
                    )
                )
                # return device_configuration.configuration.get("upload_interval")
                conf = {
                    "opconf": {
                        "upint": device_configuration.configuration.get(
                            "upload_interval"
                        ),
                    },
                    "devinfo": {
                        "gtwyid": gateway_device.node_id,
                        "version": device_configuration.configuration.get("version"),
                        "model": "m1",
                        "mnfdate": "2024-09-21",
                        "devloc": gateway_device.location,
                        "devtype": "MVI-GATEWAY",
                    },
                    "serverconf": {
                        "hostname": device_configuration.configuration.get("hostname"),
                        "apiurl": device_configuration.configuration.get("api_url"),
                        "tokenurl": device_configuration.configuration.get("token_url"),
                        "dataurl": device_configuration.configuration.get("data_url"),
                        "alerturl": device_configuration.configuration.get("alert_url"),
                        "confurl": device_configuration.configuration.get(
                            "configuration_url"
                        ),
                        "sslurl": device_configuration.configuration.get("ssl_url"),
                    },
                    "wifi": {},
                }
                generated_token = generate_access_token_for_third_party_app(
                    external_app.secret_key,
                    expiry_minutes,
                    UserRole.THIRD_PARTY_APP,
                    conf,
                )
                app_service_data = {
                    "access_token": generated_token[0],
                    "expiry_date": generated_token[1],
                    "conf": generated_token[2],
                }
            else:
                generated_token = generate_access_token_for_third_party_app(
                    external_app.secret_key,
                    expiry_minutes,
                    UserRole.THIRD_PARTY_APP,
                )
                app_service_data = {
                    "access_token": generated_token[0],
                    "expiry_date": generated_token[1],
                }
            return app_service_data
        except Exception as e:
            raise e
