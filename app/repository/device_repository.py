from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.device import Device
from app.model.inventory import Inventory
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import AccountType


class DeviceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Device)

    def get_all_devices(self):
        with self.session_factory() as session:
            try:
                devices = (
                    session.query(self.model)
                    .options(
                        joinedload(Device.inventory).joinedload(Inventory.manufacturer),
                        joinedload(Device.inventory).joinedload(Inventory.images),
                    )
                    .all()
                )
                return devices
            except Exception as e:
                session.rollback()
                raise e

    def get_user_data_by_device_uuid(self, device_imei: str):
        with self.session_factory() as session:
            try:
                device = (
                    session.query(self.model)
                    .filter(self.model.device_imei == device_imei)
                    .options(
                        joinedload(Device.inventory).joinedload(Inventory.manufacturer),
                        joinedload(Device.user),
                    )
                    .first()
                )
                if device:
                    if device.user_uuid:
                        return device
                    else:
                        raise Exception("There is no user assigned to this device")
                else:
                    raise Exception(
                        f"There is no device with the given imei: {device_imei}"
                    )
            except Exception as e:
                raise e

    def create_devices(self, inventory):
        with self.session_factory() as session:
            devices = []
            for _ in range(inventory.quantity):
                device = Device(device_inventory_uuid=inventory.uuid)
                devices.append(device)
            session.add_all(devices)
            session.commit()

    def get_devices_by_user_uuid(self, user_uuid):
        with self.session_factory() as session:
            user = session.query(User).filter(User.uuid == user_uuid).first()

            if not user:
                raise Exception("User not found")

            if user.account_type == AccountType.INDIVIDUAL:
                devices = (
                    session.query(self.model)
                    .filter(self.model.user_uuid == user.uuid)
                    .options(joinedload(Device.asset))
                    .options(joinedload(Device.inventory).joinedload(Inventory.images))
                    .all()
                )

            if user.account_type == AccountType.BUSINESS:
                devices = (
                    session.query(self.model)
                    .filter(
                        self.model.business_profile_uuid == user.business_profile_uuid
                    )
                    .options(joinedload(Device.asset))
                    .options(joinedload(Device.inventory).joinedload(Inventory.images))
                    .all()
                )

            return devices

    def assign_imei(self, device_uuid, imei):
        with self.session_factory() as session:
            try:
                device = (
                    session.query(self.model)
                    .filter(self.model.uuid == device_uuid)
                    .first()
                )
                if not device:
                    raise Exception(f"Device not found for the ID: {device_uuid}")
                device.device_imei = imei
                session.commit()
                session.refresh(device)
                return device
            except Exception as e:
                session.rollback()
                raise e
