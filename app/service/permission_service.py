from app.core.constants import PERMISSIONS
from app.model.permission import Permission
from app.repository.permission_repository import PermissionRepository
from app.service.base_service import BaseService


class PermissionService(BaseService):
    def __init__(self, permission_repository: PermissionRepository):
        self.permission_repository = permission_repository
        super().__init__(permission_repository)

    def synchronize_permissions(self):
        # Get all existing permissions from the database
        existing_permissions = self.permission_repository.get_list()
        existing_permission_names = set(p.permission_name for p in existing_permissions)

        # Iterate over the PERMISSIONS dictionary
        for model, permissions in PERMISSIONS.items():
            for permission_name in permissions:
                if permission_name not in existing_permission_names:
                    # Create a new Permission object
                    permission = Permission(
                        permission_name=permission_name, model=model
                    )
                    # Save it to the database
                    self.permission_repository.create(permission)
                    existing_permission_names.add(permission_name)
        # Return all permissions
        return self.permission_repository.get_list()
