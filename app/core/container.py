from dependency_injector import containers, providers

from app.core.config import configs
from app.core.database import Database
from app.repository import (
    alert_maintenance_type_repository,
    alert_notification_assignment_repository,
    alert_policy_asset_assignment_repository,
    alert_policy_notification_type_assignment_repository,
    alert_policy_repository,
    alert_policy_type_repository,
    asset_location_repository,
    asset_repository,
    asset_type_repository,
    business_profile_repository,
    contact_sale_repository,
    driver_repository,
    email_verification_repository,
    equipment_repository,
    equipment_type_repository,
    feature_repository,
    marker_icon_repository,
    onboarding_feature_assignment_repository,
    onboarding_repository,
    organisation_contact_repository,
    package_item_repository,
    package_repository,
    user_organisation_assignment_repository,
    user_repository,
)
from app.service import (
    alert_maintenance_type_service,
    alert_policy_service,
    alert_policy_type_service,
    asset_location_service,
    asset_service,
    asset_type_service,
    auth_service,
    contact_sale_service,
    driver_service,
    equipment_service,
    equipment_type_service,
    feature_service,
    marker_icon_service,
    onboarding_service,
    organisation_contact_service,
    package_item_service,
    package_service,
    user_service,
)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.endpoints.authentication",
            "app.api.v1.endpoints.users",
            "app.api.v1.endpoints.alert_policy_type",
            "app.api.v1.endpoints.alert_maintenance_type",
            "app.api.v1.endpoints.equipment_type",
            "app.api.v1.endpoints.equipment",
            "app.api.v1.endpoints.marker_icon",
            "app.api.v1.endpoints.asset_type",
            "app.api.v1.endpoints.asset",
            "app.api.v1.endpoints.asset_location",
            "app.api.v1.endpoints.alert_policy",
            "app.api.v1.endpoints.driver",
            "app.api.v1.endpoints.feature",
            "app.api.v1.endpoints.organisation_contact",
            "app.api.v1.endpoints.package",
            "app.api.v1.endpoints.package_item",
            "app.core.dependencies",
        ]
    )

    db = providers.Singleton(Database, db_url=configs.DATABASE_URI)

    # Repositories
    user_repository = providers.Factory(
        user_repository.UserRepository, session_factory=db.provided.session
    )
    email_verfication_repository = providers.Factory(
        email_verification_repository.EmailVerificationRepository,
        session_factory=db.provided.session,
    )
    alert_policy_type_repository = providers.Factory(
        alert_policy_type_repository.AlertPolicyTypeRepository,
        session_factory=db.provided.session,
    )
    alert_policy_repository = providers.Factory(
        alert_policy_repository.AlertPolicyRepository,
        session_factory=db.provided.session,
    )
    alert_notification_assignment_repository = providers.Factory(
        alert_notification_assignment_repository.AlertNotificationAssignmentRepository,
        session_factory=db.provided.session,
    )
    alert_policy_notification_type_assignment_repository = providers.Factory(
        alert_policy_notification_type_assignment_repository.AlertPolicyNotificationTypeAssignmentRepository,
        session_factory=db.provided.session,
    )
    alert_policy_asset_assignment_repository = providers.Factory(
        alert_policy_asset_assignment_repository.AlertPolicyAssetAssignmentRepository,
        session_factory=db.provided.session,
    )
    alert_maintenance_type_repository = providers.Factory(
        alert_maintenance_type_repository.AlertMaintenanceTypeRepository,
        session_factory=db.provided.session,
    )
    asset_location_repository = providers.Factory(
        asset_location_repository.AssetLocationRepository,
        session_factory=db.provided.session,
    )
    asset_type_repository = providers.Factory(
        asset_type_repository.AssetTypeRepository, session_factory=db.provided.session
    )
    asset_repository = providers.Factory(
        asset_repository.AssetRepository, session_factory=db.provided.session
    )
    business_profile_repository = providers.Factory(
        business_profile_repository.BusinessProfileRepository,
        session_factory=db.provided.session,
    )
    contact_sale_repository = providers.Factory(
        contact_sale_repository.ContactSaleRepository,
        session_factory=db.provided.session,
    )
    driver_repository = providers.Factory(
        driver_repository.DriverRepository, session_factory=db.provided.session
    )
    equipment_type_repository = providers.Factory(
        equipment_type_repository.EquipmentTypeRepository,
        session_factory=db.provided.session,
    )
    equipment_repository = providers.Factory(
        equipment_repository.EquipmentRepository, session_factory=db.provided.session
    )
    feature_repository = providers.Factory(
        feature_repository.FeatureRepository, session_factory=db.provided.session
    )
    marker_icon_repository = providers.Factory(
        marker_icon_repository.MarkerIconRepository, session_factory=db.provided.session
    )
    onboarding_repository = providers.Factory(
        onboarding_repository.OnboardingRepository, session_factory=db.provided.session
    )
    onboarding_feature_assignment_repository = providers.Factory(
        onboarding_feature_assignment_repository.OnboardingFeatureAssignmentRepository,
        session_factory=db.provided.session,
    )
    organisation_contact_repository = providers.Factory(
        organisation_contact_repository.OrganisationContactRepository,
        session_factory=db.provided.session,
    )
    package_item_repository = providers.Factory(
        package_item_repository.PackageItemRepository,
        session_factory=db.provided.session,
    )
    package_repository = providers.Factory(
        package_repository.PackageRepository, session_factory=db.provided.session
    )
    user_organisation_assignment_repository = providers.Factory(
        user_organisation_assignment_repository.UserOrganisationAssignmentRepository,
        session_factory=db.provided.session,
    )

    # Services
    auth_service = providers.Factory(
        auth_service.AuthService,
        user_repository=user_repository,
        email_verification_repository=email_verfication_repository,
    )
    user_service = providers.Factory(
        user_service.UserService, user_repository=user_repository
    )
    alert_policy_type_service = providers.Factory(
        alert_policy_type_service.AlertPolicyTypeService,
        alert_policy_type_repository=alert_policy_type_repository,
    )
    alert_policy_service = providers.Factory(
        alert_policy_service.AlertPolicyService,
        alert_policy_repository=alert_policy_repository,
        alert_notification_assignment_repository=alert_notification_assignment_repository,
        alert_policy_notification_type_assignment_repository=alert_policy_notification_type_assignment_repository,
        alert_policy_asset_assignment_repository=alert_policy_asset_assignment_repository,
    )
    alert_maintenance_type_service = providers.Factory(
        alert_maintenance_type_service.AlertMaintenanceTypeService,
        alert_maintenance_type_repository=alert_maintenance_type_repository,
    )
    asset_location_service = providers.Factory(
        asset_location_service.AssetLocationService,
        asset_location_repository=asset_location_repository,
    )
    asset_type_service = providers.Factory(
        asset_type_service.AssetTypeService, asset_type_repository=asset_type_repository
    )
    asset_service = providers.Factory(
        asset_service.AssetService,
        asset_repository=asset_repository,
        driver_repository=driver_repository,
    )
    contact_sale_service = providers.Factory(
        contact_sale_service.ContactSaleService,
        contact_sale_repository=contact_sale_repository,
    )
    driver_service = providers.Factory(
        driver_service.DriverService,
        driver_repository=driver_repository,
    )
    equipment_type_service = providers.Factory(
        equipment_type_service.EquipmentTypeService,
        equipment_type_repository=equipment_type_repository,
    )
    equipment_service = providers.Factory(
        equipment_service.EquipmentService,
        equipment_repository=equipment_repository,
    )
    feature_service = providers.Factory(
        feature_service.FeatureService,
        feature_repository=feature_repository,
    )
    marker_icon_service = providers.Factory(
        marker_icon_service.MarkerIconService,
        marker_icon_repository=marker_icon_repository,
    )
    onboarding_service = providers.Factory(
        onboarding_service.OnboardingService,
        onboarding_repository=onboarding_repository,
        onboarding_feature_assignment_repository=onboarding_feature_assignment_repository,
        business_profile_repository=business_profile_repository,
        user_organisation_assignment_repository=user_organisation_assignment_repository,
    )
    organisation_contact_service = providers.Factory(
        organisation_contact_service.OrganisationContactService,
        organisation_contact_repository=organisation_contact_repository,
    )
    package_item_service = providers.Factory(
        package_item_service.PackageItemService,
        package_item_repository=package_item_repository,
    )
    package_service = providers.Factory(
        package_service.PackageService,
        package_repository=package_repository,
    )
