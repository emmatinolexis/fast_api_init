from app.core import messages
from app.core.exceptions import BadRequestError, NotFoundError
from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.repository.gas_device_repository import GasDeviceRepository
from app.service.base_service import BaseService
from app.util.enums import ActiveStatus, DeviceStatus


class GasCylinderService(BaseService):
    def __init__(
        self,
        gas_cylinder_repository: GasCylinderRepository,
        gas_device_repository: GasDeviceRepository,
    ):
        self.gas_cylinder_repository = gas_cylinder_repository
        self.gas_device_repository = gas_device_repository
        super().__init__(gas_cylinder_repository)

    def link_to_gas_device(self, gas_cylinder_uuid: str, gas_device_uuid: str):
        gas_device = self.gas_device_repository.get_by_uuid(gas_device_uuid)
        cylinder = self.get_by_uuid(gas_cylinder_uuid)

        if not gas_device:
            raise NotFoundError(messages.GAS_DEVICE_NOT_FOUND + gas_device_uuid)

        if not cylinder:
            raise NotFoundError(messages.GAS_CYLINDER_NOT_FOUND + gas_cylinder_uuid)

        if gas_device.status == DeviceStatus.ASSIGNED:
            raise BadRequestError(messages.DEVICE_ALREADY_ASSIGNED)

        if cylinder.status == ActiveStatus.INACTIVE:
            raise BadRequestError(messages.GAS_CYLINDER_INACTIVE)

        self.gas_cylinder_repository.update_attr_by_uuid(
            gas_cylinder_uuid, "gas_device_uuid", gas_device_uuid
        )

        self.gas_device_repository.update_attr_by_uuid(
            gas_device_uuid, "status", DeviceStatus.ASSIGNED
        )

        return cylinder

    def unlink_gas_cylinder(self, gas_cylinder_uuid: str):
        cylinder = self.get_by_uuid(gas_cylinder_uuid)
        gas_device_uuid = cylinder.gas_device_uuid

        if not cylinder:
            raise NotFoundError(messages.GAS_CYLINDER_NOT_FOUND + gas_cylinder_uuid)

        if not gas_device_uuid:
            raise BadRequestError(messages.ALREADY_UNLINKED)

        self.gas_cylinder_repository.update_attr_by_uuid(
            gas_cylinder_uuid, "gas_device_uuid", None
        )

        self.gas_device_repository.update_attr_by_uuid(
            gas_device_uuid, "status", DeviceStatus.NOT_ASSIGNED
        )

        return cylinder
