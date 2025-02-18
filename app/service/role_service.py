# The RoleService class in the provided Python code handles operations related to roles, permissions,
# and role-permission assignments.
from app.repository.role_permission_assignment_repository import (
    RolePermissionAssignmentRepository,
)
from app.repository.role_repository import RoleRepository
from app.schema.permission_schema import RolePayload
from app.service.base_service import BaseService
from app.util.utils import format_compound_words


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

    async def get_all_roles(self, role_type: str = None):
        try:
            roles_data = []
            roles = await self.role_repository.get_all_roles(role_type)
            for role in roles:
                permissions = {}

                for entry in role.permissions:
                    model = entry.model
                    permission = {
                        "permission_name": entry.permission_name,
                        "uuid": entry.uuid,
                    }

                    if model not in permissions:
                        permissions[model] = []

                    permissions[model].append(permission)

                formatted_data = [
                    {"name": format_compound_words(model), "permission": permissions}
                    for model, permissions in permissions.items()
                ]
                updated_role = {
                    "role_name": role.role_name,
                    "role_uuid": role.uuid,
                    "permissions": formatted_data,
                }
                roles_data.append(updated_role)

            return roles_data
        except Exception as e:
            raise e

    async def get_role(self, role_uuid: str):
        try:
            role = await self.role_repository.get_role(role_uuid)
            return role
        except Exception as e:
            raise e

    async def create_role_permission(self, payload: RolePayload):
        try:
            # Create the role
            role = await self.role_repository.create_role(payload)
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
                    await self.role_permission_assignment_repository.create_role_permission(
                        permission_assignment_data
                    )

                return role
        except Exception as e:
            # Log or handle the exception as needed
            raise e

    async def update_role(self, payload: RolePayload, role_uuid: str):
        try:
            # update role
            role = await self.role_repository.update_role(payload, role_uuid)
            if role:
                # delete current permissions to this role
                await self.role_permission_assignment_repository.delete_role_permission(
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
                    await self.role_permission_assignment_repository.create_role_permission(
                        permission_assignment_data
                    )

                return role
        except Exception as e:
            # Log or handle the exception as needed
            raise e
