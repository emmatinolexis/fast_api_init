from app.model.activity_log import ActivityLog
from app.model.user import User
from app.repository.role_repository import RoleRepository
from app.repository.user_repository import UserRepository


def activity_log_transformer(
    activity_log: ActivityLog, user_repo: UserRepository, role_repo: RoleRepository
) -> dict:
    user: User = user_repo.read_by_uuid(activity_log.user_uuid)

    user_data = {
        "full_name": f"{user.first_name} {user.last_name}",
        "email": user.email_address,
    }

    user_role = role_repo.read_by_uuid(user.user_role_uuid)
    user_data["role"] = user_role.role_name

    return {
        "uuid": activity_log.uuid,
        "user": user_data,
        "business_profile_uuid": activity_log.business_profile_uuid,
        "activity_title": activity_log.activity_title,
        "activity_class": activity_log.activity_class,
        "activity_type": activity_log.activity_type,
        "activity_description": activity_log.activity_description,
        "ip_address": activity_log.ip_address,
        "created_at": activity_log.created_at,
    }
