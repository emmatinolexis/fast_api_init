from app.repository.role_permission_assignment_repository import \
    RolePermissionAssignmentRepository
from app.repository.role_repository import RoleRepository
from app.schema.permission_schema import RolePayload
from app.service.base_service import BaseService


class RoleService(BaseService):
    def __init__(
        self,
        role_repository: RoleRepository,
        role_permission_assignment_repository: RolePermissionAssignmentRepository,
    ):
        self.role_repository = role_repository
        self.role_permission_assignment_repository = (
            role_permission_assignment_repository
        )
        super().__init__(role_repository)

    def get_all_roles(self, role_type: str = None) -> RolePayload:
        return self.role_repository.get_all_roles(role_type)

    def get_role(self, role_uuid: str):
        try:
            role = self.role_repository.get_role(role_uuid)
            return role
        except Exception as e:
            raise e

    def create_role_permission(self, payload: RolePayload):
        try:
            # Create the role
            role = self.role_repository.create_role(payload)
            # Check if the role was successfully created
            if role:
                # Iterate over the permissions in the payload
                for permission_uuid in payload.permissions:
                    # Prepare the permission assignment data
                    permission_assignment_data = {
                        "role_uuid": role.uuid,
                        "permission_uuid": permission_uuid,
                    }
                    # Create the permission assignment
                    self.role_permission_assignment_repository.create_role_permission(
                        permission_assignment_data
                    )

                return role
        except Exception as e:
            # Log or handle the exception as needed
            raise e

    def update_role(self, payload: RolePayload, role_uuid: str):
        try:
            # update role
            role = self.role_repository.update_role(payload, role_uuid)
            if role:
                # delete current permissions to this role
                self.role_permission_assignment_repository.delete_role_permission(
                    role_uuid
                )

                # assign incoming permissions to role
                for permission_uuid in payload.permissions:
                    # Prepare the permission assignment data
                    permission_assignment_data = {
                        "role_uuid": role.uuid,
                        "permission_uuid": permission_uuid,
                    }
                    # Create the permission assignment
                    self.role_permission_assignment_repository.create_role_permission(
                        permission_assignment_data
                    )

                return role
        except Exception as e:
            # Log or handle the exception as needed
            raise e
