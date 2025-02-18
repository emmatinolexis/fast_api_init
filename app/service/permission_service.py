from app.core.constants import PERMISSIONS
from app.model.permission import Permission
from app.repository.permission_repository import PermissionRepository
from app.service.base_service import BaseService
from app.util.enums import PermissionType
from app.util.utils import format_compound_words


class PermissionService(BaseService):
    def __init__(self, permission_repository: PermissionRepository):
        self.permission_repository = permission_repository
        super().__init__(permission_repository)

    async def synchronize_permissions(self):
        # Get all existing permissions from the database
        existing_permissions = await self.permission_repository.get_list()

        for model, permissions in PERMISSIONS.items():
            for permission in permissions:
                permission_name = permission["permission_name"]
                permission_type = permission["permission_type"]

                # Check if the permission already exists
                existing_permission = next(
                    (
                        ep
                        for ep in existing_permissions
                        if ep.permission_name == permission_name and ep.model == model
                    ),
                    None,
                )

                if existing_permission:
                    # Update the permission_type if it's None
                    if existing_permission.permission_type is None:
                        await self.permission_repository.update_attr_by_uuid(
                            existing_permission.uuid, "permission_type", permission_type
                        )
                else:
                    # Create a new Permission object if it doesn't exist
                    permission_obj = Permission(
                        permission_name=permission_name,
                        model=model,
                        permission_type=permission_type,
                    )
                    # Save it to the database
                    await self.permission_repository.create(permission_obj)

        return await self.permission_repository.get_list()

    async def get_permissions(self, permission_type: PermissionType):
        try:
            data = await self.permission_repository.get_all_permissions(permission_type)

            permissions = {}

            for entry in data:
                model = entry.model
                permission = {
                    "permission_name": entry.permission_name,
                    "uuid": entry.uuid,
                    "permission_type": entry.permission_type,
                }

                if model not in permissions:
                    permissions[model] = []

                permissions[model].append(permission)

            formatted_data = [
                {"name": format_compound_words(model), "permission": permissions}
                for model, permissions in permissions.items()
            ]

            return formatted_data

        except Exception as e:
            raise e
