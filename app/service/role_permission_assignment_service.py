from app.repository.role_permission_assignment_repository import (
    RolePermissionAssignment,
)
from app.service.base_service import BaseService


class RolePermissionAssignmentService(BaseService):
    def __init__(self, role_permission_assignment_repository: RolePermissionAssignment):
        self.role_permission_assignment_repository = (
            role_permission_assignment_repository
        )
        super().__init__(role_permission_assignment_repository)
