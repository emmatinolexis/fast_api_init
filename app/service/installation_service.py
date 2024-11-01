from app.repository.installation_repository import InstallationRepository
from app.schema.installation_schema import InstallationPayload
from app.schema.user_schema import InstallerResponse
from app.schema.installation_schema import InstallationResponse, AssignInstallerPayload

class InstallationService:
    def __init__(self, installation_repository: InstallationRepository):
        self.installation_repository = installation_repository

    def create_installation(self, installation_payload: InstallationPayload):
        try:
            return self.installation_repository.create_installation(
                installation_payload
            )
        except Exception as e:
            raise e

    def get_installation_by_order_uuid(self, order_uuid: str):
        try:
            return self.installation_repository.get_installation_by_order_uuid(
                order_uuid
            )
        except Exception as e:
            raise e

    def assign_installer_to_installation(self, payload: AssignInstallerPayload):
        try:
            return self.installation_repository.assign_installer_to_installation(
                payload
            )
        except Exception as e:
            raise e

    def get_installation(self, installation_uuid: str):
        try:
            data = self.installation_repository.get_installation(installation_uuid)
            if data is None:
                return None
            order = data.order
            order_shipping_address = order.order_shipping_address if order else None
            installation = InstallationResponse(
                    installation_uuid=str(data.uuid),
                    status=data.status,
                    installer_name=f"{data.installer.first_name} {data.installer.last_name}" if data.installer else None,
                    installer_image_url=data.installer.avatar_url if data.installer else None,
                    installer_phone=data.installer.phone_number if data.installer else None,
                    first_name=order_shipping_address.first_name if order_shipping_address else None,
                    last_name=order_shipping_address.last_name if order_shipping_address else None,
                    location=order_shipping_address.address if order_shipping_address else None,
                    date_of_installation=order.date_of_installation if order else None,
                    time_of_installation=order.time_of_installation if order else None,
                    devices=[
                        {
                            "device_uuid": inventory.inventory.uuid,
                            "device_name": inventory.inventory.device_name
                        }
                        for inventory in order.order_inventories
                    ] if order and order.order_inventories else []
                )
            return installation
        except Exception as e:
            raise e

    def fetch_all_installers(self):
        try:
            installers = self.installation_repository.get_installers()
            return [
                InstallerResponse(
                    **{
                        "uuid": installer.uuid,
                        "first_name": installer.first_name,
                        "last_name": installer.last_name,
                        "avatar_url": installer.avatar_url,
                    }
                )
                for installer in installers
            ]
        except Exception as e:
            raise e
        
    def fetch_installations(self, page, page_size):
        try:
            installations = self.installation_repository.get_installations(page, page_size)

            installation_responses = []
            for installation in installations.get("data"):
                order = installation.order
                order_shipping_address = order.order_shipping_address if order else None
                installation_response = InstallationResponse(
                    installation_uuid=str(installation.uuid),
                    status=installation.status,
                    installer_name=f"{installation.installer.first_name} {installation.installer.last_name}" if installation.installer else None,
                    installer_image_url=installation.installer.avatar_url if installation.installer else None,
                    installer_phone=installation.installer.phone_number if installation.installer else None,
                    first_name=order_shipping_address.first_name if order_shipping_address else None,
                    last_name=order_shipping_address.last_name if order_shipping_address else None,
                    location=order_shipping_address.address if order_shipping_address else None,
                    date_of_installation=order.date_of_installation if order else None,
                    time_of_installation=order.time_of_installation if order else None,
                    devices=[
                                {
                                    "device_uuid": inventory.inventory.uuid,
                                    "device_name": inventory.inventory.device_name,
                                }
                                for inventory in order.order_inventories
                        ] if order and order.order_inventories else []
                )
                installation_responses.append(installation_response)
            return {
                "installations": installation_responses,
                "current_page": installations.get("current_page"),
                "page_size": installations.get("page_size"),
                "total_records": installations.get("total_records"),
                "total_pages": installations.get("total_pages")
            }
        except Exception as e:
            raise e
