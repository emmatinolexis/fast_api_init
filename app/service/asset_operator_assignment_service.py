from app.repository.asset_operator_assignment_repository import AssetOperatorTypeAssignmentRepository
from app.repository.user_repository import UserRepository
from app.repository.asset_repository import AssetRepository
from app.service.base_service import BaseService
from app.core.exceptions import NotFoundError,UnAuthorizedError
from app.core import messages
from app.schema.asset_schema import AssignAssetPayload


class AssetOperatorAssignmentService(BaseService):
    def __init__(self, asset_operator_assignment: AssetOperatorTypeAssignmentRepository,asset_repository:AssetRepository,user_repository: UserRepository,):
        self.asset_operator_assignment = asset_operator_assignment
        self.asset_repository =asset_repository
        self.user_repository = user_repository
        super().__init__(asset_operator_assignment)


    def assign_operator_to_asset(self,asset_uuid:str,operator_uuid:str,user_uuid:str,business_profile_uuid: str = None):
        try:
            asset = self.asset_repository.read_by_uuid(asset_uuid)
            if asset is None:
                raise NotFoundError(messages.NO_ASSET_FOUND)
            

            if asset.business_profile_uuid != business_profile_uuid:
                # If not, check if the asset's user_uuid matches the provided user_uuid
                if asset.user_uuid != user_uuid:
                    raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)
                

            operator = self.user_repository.read_by_uuid(operator_uuid)
            if operator is None:
                raise NotFoundError(messages.NO_OPERATOR_FOUND)
            
            existing_operator_asset_assignment = self.asset_operator_assignment.get_assignment_by_operator_uuid(operator_uuid=operator_uuid)
            existing_asset_operator_assignment = self.asset_operator_assignment.get_assignment_by_asset_uuid(asset_uuid=asset_uuid)
            if existing_operator_asset_assignment or existing_asset_operator_assignment:
                self.asset_operator_assignment.update_attr_by_uuid(existing_operator_asset_assignment.uuid,"asset_uuid",asset_uuid)
                self.asset_operator_assignment.update_attr_by_uuid(existing_operator_asset_assignment.uuid, "operator_uuid", operator_uuid)
            else:
                # Create a new assignment if none exists
                schema = AssignAssetPayload(
                    asset_uuid=asset_uuid,
                    operator_uuid=operator_uuid
                )
                self.asset_operator_assignment.create(schema=schema)
            return messages.ASSIGNMENT_SUCCESS

        except Exception as e:
            # Handle exceptions as needed
            raise e

            




