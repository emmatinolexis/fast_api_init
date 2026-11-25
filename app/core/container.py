from dependency_injector import containers, providers

from app.core.database import Database
from app.core.settings import settings
from app.repository import (
    email_verification_repository,
    permission_repository,
    phone_otp_repository,
    reset_password_repository,
    role_permission_assignment_repository,
    role_repository,
    user_organisation_assignment_repository,
    user_repository,
    business_profile_repository,
    team_member_invitation_repository,
)
from app.service import (
    auth_service,
    permission_service,
    phone_otp_service,
    role_permission_assignment_service,
    role_service,
    user_service,
    business_profile_service,
    invitation_service,
    reset_password_service,
)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.endpoints.authentication",
            "app.api.v1.endpoints.users",
            "app.api.v1.endpoints.permissions",
            "app.core.dependencies",
        ]
    )

    db = providers.Singleton(Database, db_url=settings.DATABASE_URI)

    # Repositories
    user_repository = providers.Factory(
        user_repository.UserRepository, session_factory=db.provided.session
    )

    business_profile_repository = providers.Factory(
        business_profile_repository.BusinessProfileRepository,
        session_factory=db.provided.session,
    )

    email_verfication_repository = providers.Factory(
        email_verification_repository.EmailVerificationRepository,
        session_factory=db.provided.session,
    )

    phone_otp_repository = providers.Factory(
        phone_otp_repository.PhoneOtpTokenRepository,
        session_factory=db.provided.session,
    )
    user_organisation_assignment_repository = providers.Factory(
        user_organisation_assignment_repository.UserOrganisationAssignmentRepository,
        session_factory=db.provided.session,
    )
    reset_password_repository = providers.Factory(
        reset_password_repository.PasswordResetRepository,
        session_factory=db.provided.session,
    )
    permissions_repository = providers.Factory(
        permission_repository.PermissionRepository,
        session_factory=db.provided.session,
    )
    role_repository = providers.Factory(
        role_repository.RoleRepository,
        session_factory=db.provided.session,
    )
    role_permission_assignment_repository = providers.Factory(
        role_permission_assignment_repository.RolePermissionAssignmentRepository,
        session_factory=db.provided.session,
    )

    # Services
    auth_service = providers.Factory(
        auth_service.AuthService,
        user_repository=user_repository,
        email_verification_repository=email_verfication_repository,
    )
    user_service = providers.Factory(
        user_service.UserService,
        user_repository=user_repository,
        role_repository=role_repository,
    )

    phone_otp_service = providers.Factory(
        phone_otp_service.PhoneOTPService,
        phone_otp_repository=phone_otp_repository,
        user_repository=user_repository,
    )

    invitation_service = providers.Factory(
        invitation_service.InvitationService,
        invitation_repository=team_member_invitation_repository,
    )

    permission_service = providers.Factory(
        permission_service.PermissionService,
        permission_repository=permissions_repository,
    )
    reset_password_service = providers.Factory(
        reset_password_service.ResetPassword,
        reset_password_repository=reset_password_repository,
    )
    business_profile_service = providers.Factory(
        business_profile_service.BusinessProfileService,
        business_profile_repository=business_profile_repository,
    )

    role_service = providers.Factory(
        role_service.RoleService,
        role_repository=role_repository,
        role_permission_assignment_repository=role_permission_assignment_repository,
    )
    role_permission_assignment_service = providers.Factory(
        role_permission_assignment_service.RolePermissionAssignmentService,
        role_permission_assignment_repository=role_permission_assignment_repository,
    )
