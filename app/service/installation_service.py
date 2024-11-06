from app.repository.installation_repository import InstallationRepository
from app.repository.user_repository import UserRepository
from app.schema.installation_schema import InstallationPayload
from app.schema.user_schema import InstallerResponse

from app.schema.installation_schema import InstallationResponse, AssignInstallerPayload
from app.events.subscriber import subscriber
from app.events.installation import InstallationCreated
from app.util.enums import InstallationStatus


class InstallationService:
    def __init__(self, installation_repository: InstallationRepository,user_repository:UserRepository):
        self.installation_repository = installation_repository
        self.user_repository = user_repository


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
            installer = self.user_repository.read_by_uuid(uuid=payload.installer_uuid)
            installation = self.installation_repository.get_installation(payload.installation_uuid)

            subscriber.publish(InstallationCreated,InstallationCreated(installation=installation,user=installer))
            return self.installation_repository.assign_installer_to_installation(
                payload
            )
        except Exception as e:
            raise e

    def update_installation_status(self, installation_uuid: str, status: InstallationStatus):
        try:
            return self.installation_repository.update_installation_status(installation_uuid, status)
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
                installer_name=f"{data.installer.first_name} {data.installer.last_name}"
                if data.installer
                else None,
                installer_image_url=data.installer.avatar_url
                if data.installer
                else None,
                installer_phone=data.installer.phone_number if data.installer else None,
                first_name=order_shipping_address.first_name
                if order_shipping_address
                else None,
                last_name=order_shipping_address.last_name
                if order_shipping_address
                else None,
                location=order_shipping_address.address
                if order_shipping_address
                else None,
                date_of_installation=order.date_of_installation if order else None,
                time_of_installation=order.time_of_installation if order else None,
                devices=[
                    {
                        "device_uuid": inventory.inventory.uuid,
                        "device_name": inventory.inventory.device_name,
                    }
                    for inventory in order.order_inventories
                ]
                if order and order.order_inventories
                else [],
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

        
    def fetch_installations(self,
                            page,
                            page_size,
                            installer_uuid: str = None,
                            status: InstallationStatus = None,
                            start_date: str = None,
                            end_date: str = None,
                            search_parameter: str = None):
        try:
            installations = self.installation_repository.get_installations(page, page_size, installer_uuid, status, start_date, end_date, search_parameter)

            installation_responses = []
            for installation in installations.get("data"):
                order = installation.order
                order_shipping_address = order.order_shipping_address if order else None
                installation_response = InstallationResponse(
                    installation_uuid=str(installation.uuid),
                    status=installation.status,
                    installer_name=f"{installation.installer.first_name} {installation.installer.last_name}"
                    if installation.installer
                    else None,
                    installer_image_url=installation.installer.avatar_url
                    if installation.installer
                    else None,
                    installer_phone=installation.installer.phone_number
                    if installation.installer
                    else None,
                    first_name=order_shipping_address.first_name
                    if order_shipping_address
                    else None,
                    last_name=order_shipping_address.last_name
                    if order_shipping_address
                    else None,
                    location=order_shipping_address.address
                    if order_shipping_address
                    else None,
                    date_of_installation=order.date_of_installation if order else None,
                    time_of_installation=order.time_of_installation if order else None,
                    devices=[
                        {
                            "device_uuid": inventory.inventory.uuid,
                            "device_name": inventory.inventory.device_name,
                        }
                        for inventory in order.order_inventories
                    ]
                    if order and order.order_inventories
                    else [],
                )
                # Apply search filter to installation_response if search_parameter is provided
                if search_parameter:
                    search_text = search_parameter.lower()
                    # Check if search parameter matches relevant fields
                    if (search_text in (installation_response.installer_name or "").lower() or
                            search_text in (installation_response.first_name or "").lower() or
                            search_text in (installation_response.last_name or "").lower()):
                        installation_responses.append(installation_response)
                else:
                    # Append response if no search filter is provided
                    installation_responses.append(installation_response)
                # installation_responses.append(installation_response)
            return {
                "installations": installation_responses,
                "current_page": installations.get("current_page"),
                "page_size": installations.get("page_size"),
                "total_records": installations.get("total_records"),
                "total_pages": installations.get("total_pages"),
            }
        except Exception as e:
            raise e
