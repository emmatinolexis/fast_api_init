from app.repository.asset_operator_assignment_repository import AssetOperatorTypeAssignmentRepository
from app.service.base_service import BaseService


class AssetOperatorAssignmentService(BaseService):
    def __init__(self, asset_operator_assignment: AssetOperatorTypeAssignmentRepository):
        self.asset_operator_assignment = asset_operator_assignment
        super().__init__(asset_operator_assignment)