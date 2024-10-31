from app.repository.installation_repository import InstallationRepository
from app.schema.installation_schema import InstallationPayload
from app.schema.user_schema import InstallerResponse
from app.schema.installation_schema import InstallationResponse

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
        
    def fetch_installations(self):
        try:
            installations = self.installation_repository.get_installations()
            installation_responses = []
            for installation in installations:
                order = installation.order
                order_shipping_address = order.order_shipping_address if order else None
                installation_response = InstallationResponse(
                    installation_uuid=str(installation.uuid),
                    order_status=order.order_status.value if order and order.order_status else None,
                    first_name=order_shipping_address.first_name if order_shipping_address else None,
                    last_name=order_shipping_address.last_name if order_shipping_address else None,
                    location=order_shipping_address.address if order_shipping_address else None,
                    date_of_installation=order.date_of_installation if order else None,
                    time_of_installation=order.time_of_installation if order else None,
                )
                installation_responses.append(installation_response)
            return installation_responses
        except Exception as e:
            raise e