from app.core import messages
from app.core.exceptions import NotFoundError, UnAuthorizedError
from app.events.subscriber import subscriber
from app.events.user import VehicleAssignment
from app.repository.asset_operator_assignment_repository import (
    AssetOperatorTypeAssignmentRepository,
)
from app.repository.asset_repository import AssetRepository
from app.repository.user_repository import UserRepository
from app.schema.asset_schema import AssignAssetPayload
from app.service.base_service import BaseService


class AssetOperatorAssignmentService(BaseService):
    def __init__(
        self,
        asset_operator_assignment: AssetOperatorTypeAssignmentRepository,
        asset_repository: AssetRepository,
        user_repository: UserRepository,
    ):
        self.asset_operator_assignment = asset_operator_assignment
        self.asset_repository = asset_repository
        self.user_repository = user_repository
        super().__init__(asset_operator_assignment)

    def assign_operator_to_asset(
        self,
        asset_uuid: str,
        operator_uuid: str,
        user_uuid: str,
        business_profile_uuid: str = None,
    ):
        try:
            asset = self.asset_repository.read_by_uuid(asset_uuid)

            if asset is None:
                raise NotFoundError(messages.NO_ASSET_FOUND)

            if str(asset.business_profile_uuid) != business_profile_uuid:
                # If not, check if the asset's user_uuid matches the provided user_uuid
                raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)

                # if asset.user_uuid != user_uuid:
                #     raise UnAuthorizedError(messages.ACTION_NOT_ALLOWED)

            operator = self.user_repository.read_by_uuid(operator_uuid)
            if operator is None:
                raise NotFoundError(messages.NO_OPERATOR_FOUND)

            existing_operator_asset_assignment = (
                self.asset_operator_assignment.get_assignment_by_operator_uuid(
                    operator_uuid=operator_uuid
                )
            )
            existing_asset_operator_assignment = (
                self.asset_operator_assignment.get_assignment_by_asset_uuid(
                    asset_uuid=asset_uuid
                )
            )

            # Update assignment if existing, else create new
            if existing_operator_asset_assignment or existing_asset_operator_assignment:
                if existing_operator_asset_assignment is not None:
                    self.asset_operator_assignment.update_attr_by_uuid(
                        existing_operator_asset_assignment.uuid,
                        "asset_uuid",
                        asset_uuid,
                    )
                    self.asset_operator_assignment.update_attr_by_uuid(
                        existing_operator_asset_assignment.uuid,
                        "operator_uuid",
                        operator_uuid,
                    )
                elif existing_asset_operator_assignment is not None:
                    self.asset_operator_assignment.update_attr_by_uuid(
                        existing_asset_operator_assignment.uuid,
                        "asset_uuid",
                        asset_uuid,
                    )
                    self.asset_operator_assignment.update_attr_by_uuid(
                        existing_asset_operator_assignment.uuid,
                        "operator_uuid",
                        operator_uuid,
                    )

            else:
                # Create a new assignment if none exists
                schema = AssignAssetPayload(
                    asset_uuid=asset_uuid, operator_uuid=operator_uuid
                )
                self.asset_operator_assignment.create(schema=schema)
            subscriber.publish(
                VehicleAssignment, VehicleAssignment(asset=asset, user=operator)
            )

            return messages.ASSIGNMENT_SUCCESS

        except Exception as e:
            # Handle exceptions as needed
            raise e
