from dependency_injector import containers, providers

from app.client.echo_parrot import EchoParrot
from app.client.mqtt_service import MQTTService
from app.core.database import Database
from app.core.settings import settings
from app.repository import (
    alert_maintenance_type_repository,
    alert_notification_assignment_repository,
    alert_policy_asset_assignment_repository,
    alert_policy_notification_type_assignment_repository,
    alert_policy_repository,
    alert_policy_type_repository,
    asset_device_request_repository,
    asset_location_repository,
    asset_repository,
    asset_type_repository,
    business_profile_repository,
    contact_sale_repository,
    device_image_repository,
    device_manufacturer_repository,
    device_repository,
    driver_repository,
    email_verification_repository,
    equipment_repository,
    equipment_type_repository,
    external_app_repository,
    feature_repository,
    immobilizer_report_repository,
    inventory_repository,
    marker_icon_repository,
    onboarding_asset_type_assignment_repository,
    onboarding_feature_assignment_repository,
    onboarding_repository,
    order_device_assignment_repository,
    order_repository,
    order_shipping_address_repository,
    organisation_contact_repository,
    package_item_repository,
    package_repository,
    payment_repository,
    phone_otp_repository,
    plan_upgrade_repository,
    reset_password_repository,
    subscription_payment_repository,
    subscription_repository,
    team_member_invitation_repository,
    tracking_event_repository,
    user_organisation_assignment_repository,
    user_repository,
    user_subscription_repository,
)
from app.service import (
    alert_maintenance_type_service,
    alert_policy_service,
    alert_policy_type_service,
    asset_device_request_service,
    asset_location_service,
    asset_service,
    asset_type_service,
    auth_service,
    contact_sale_service,
    device_image_service,
    device_manufacturer_service,
    device_service,
    driver_service,
    equipment_service,
    equipment_type_service,
    external_app_service,
    feature_service,
    immobilizer_report_service,
    inventory_service,
    invitation_service,
    marker_icon_service,
    onboarding_service,
    order_device_assignment_service,
    order_service,
    order_shipping_address_service,
    organisation_contact_service,
    package_item_service,
    package_service,
    payment_service,
    phone_otp_service,
    plan_updgrade_service,
    reset_password_service,
    subscription_payment_service,
    subscription_service,
    tracking_event_service,
    user_service,
    user_subscription_service,
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
            "app.api.v1.endpoints.onboarding",
            "app.api.v1.endpoints.tracking",
            "app.core.dependencies",
            "app.api.v1.endpoints.device",
            "app.api.v1.endpoints.device_manufacturers",
            "app.api.v1.endpoints.subscription",
            "app.api.v1.endpoints.payment",
            "app.api.v1.endpoints.subscription_payment",
            "app.api.v1.endpoints.inventory",
            "app.api.v1.endpoints.order",
            "app.api.v1.endpoints.external_app",
        ]
    )

    db = providers.Singleton(Database, db_url=settings.DATABASE_URI)
    mqtt_service = providers.Factory(
        MQTTService,
        host=settings.MQTT_HOST,
        port=settings.MQTT_PORT,
        username=settings.MQTT_USERNAME,
        password=settings.MQTT_PASSWORD,
        topic=settings.MQTT_TOPIC,
        session_factory=db.provided.session,
    )
    echo_parrot = providers.Factory(
        EchoParrot,
        host=settings.ECHO_PARROT_HOST,
        port=settings.ECHO_PARROT_PORT,
        sender_id=settings.SMS_SENDER_ID,
        sender_app=settings.SMS_SENDER_APP,
        sender_email=settings.SENDER_EMAIL,
        sender_name=settings.SENDER_NAME,
    )

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
    asset_device_request_repository = providers.Factory(
        asset_device_request_repository.AssetDeviceRequestRepository,
        session_factory=db.provided.session,
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
    device_repository = providers.Factory(
        device_repository.DeviceRepository, session_factory=db.provided.session
    )
    device_manufacturer_repository = providers.Factory(
        device_manufacturer_repository.DeviceManufacturerRepository,
        session_factory=db.provided.session,
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
    onboarding_asset_type_assignment_repository = providers.Factory(
        onboarding_asset_type_assignment_repository.OnboardingAssetTypeAssignmentRepository,
        session_factory=db.provided.session,
    )
    organisation_contact_repository = providers.Factory(
        organisation_contact_repository.OrganisationContactRepository,
        session_factory=db.provided.session,
    )
    phone_otp_repository = providers.Factory(
        phone_otp_repository.PhoneOtpTokenRepository,
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
    team_member_invitation_repository = providers.Factory(
        team_member_invitation_repository.TeamMemberInvitationRepository,
        session_factory=db.provided.session,
    )
    tracking_event_repository = providers.Factory(
        tracking_event_repository.TrackingEventRepository,
        session_factory=db.provided.session,
    )
    subscription_repository = providers.Factory(
        subscription_repository.SubscriptionRepository,
        session_factory=db.provided.session,
    )
    subscription_payment_repository = providers.Factory(
        subscription_payment_repository.SubscriptionPaymentRepository,
        session_factory=db.provided.session,
    )
    payment_repository = providers.Factory(
        payment_repository.PaymentRepository,
        session_factory=db.provided.session,
    )
    reset_password_repository = providers.Factory(
        reset_password_repository.PasswordResetRepository,
        session_factory=db.provided.session,
    )
    plan_upgrade_repository = providers.Factory(
        plan_upgrade_repository.PlanUpgradeRepository,
        session_factory=db.provided.session,
    )
    user_subscription_repository = providers.Factory(
        user_subscription_repository.UserSubscriptionRepository,
        session_factory=db.provided.session,
    )
    inventory_repository = providers.Factory(
        inventory_repository.InventoryRepository,
        session_factory=db.provided.session,
    )
    device_image_repository = providers.Factory(
        device_image_repository.DeviceImageRepository,
        session_factory=db.provided.session,
    )
    order_repository = providers.Factory(
        order_repository.OrderRepository,
        session_factory=db.provided.session,
    )
    order_device_assignment_repository = providers.Factory(
        order_device_assignment_repository.OrderDeviceAssignmentRepository,
        session_factory=db.provided.session,
    )
    order_shipping_address_repository = providers.Factory(
        order_shipping_address_repository.OrderShippingAddressRepository,
        session_factory=db.provided.session,
    )
    external_app_repository = providers.Factory(
        external_app_repository.ExternalAppRepository,
        session_factory=db.provided.session,
    )
    immobilizer_report_repository = providers.Factory(
        immobilizer_report_repository.ImmobilizerReportRepository,
        session_factory=db.provided.session,
    )

    # Services
    auth_service = providers.Factory(
        auth_service.AuthService,
        user_repository=user_repository,
        email_verification_repository=email_verfication_repository,
        user_subscription_repository=user_subscription_repository,
        subscription_repository=subscription_repository,
    )
    user_service = providers.Factory(
        user_service.UserService,
        user_repository=user_repository,
        user_subscription_repository=user_subscription_repository,
        subscription_repository=subscription_repository,
        invitation_repository=team_member_invitation_repository,
    )
    alert_policy_type_service = providers.Factory(
        alert_policy_type_service.AlertPolicyTypeService,
        alert_policy_type_repository=alert_policy_type_repository,
    )
    alert_policy_service = providers.Factory(
        alert_policy_service.AlertPolicyService,
        alert_policy_repository=alert_policy_repository,
        alert_policy_type_repository=alert_policy_type_repository,
        alert_maintenance_type_repository=alert_maintenance_type_repository,
        alert_notification_assignment_repository=alert_notification_assignment_repository,
        alert_policy_notification_type_assignment_repository=alert_policy_notification_type_assignment_repository,
        alert_policy_asset_assignment_repository=alert_policy_asset_assignment_repository,
        asset_repository=asset_repository,
    )
    alert_maintenance_type_service = providers.Factory(
        alert_maintenance_type_service.AlertMaintenanceTypeService,
        alert_maintenance_type_repository=alert_maintenance_type_repository,
    )
    asset_location_service = providers.Factory(
        asset_location_service.AssetLocationService,
        asset_location_repository=asset_location_repository,
        asset_repository=asset_repository,
    )
    asset_type_service = providers.Factory(
        asset_type_service.AssetTypeService, asset_type_repository=asset_type_repository
    )
    asset_service = providers.Factory(
        asset_service.AssetService,
        asset_repository=asset_repository,
        asset_type_repository=asset_type_repository,
        user_repository=user_repository,
        equipment_repository=equipment_repository,
        equipment_type_repository=equipment_type_repository,
        driver_repository=driver_repository,
        subscription_repository=subscription_repository,
        device_repository=device_repository,
        immobilizer_report_repository=immobilizer_report_repository,
    )
    asset_device_request_service = providers.Factory(
        asset_device_request_service.AssetDeviceRequestService,
        asset_device_request_repository=asset_device_request_repository,
        asset_repository=asset_repository,
    )
    contact_sale_service = providers.Factory(
        contact_sale_service.ContactSaleService,
        contact_sale_repository=contact_sale_repository,
    )
    driver_service = providers.Factory(
        driver_service.DriverService,
        driver_repository=driver_repository,
        asset_repository=asset_repository,
    )
    device_manufacturer_service = providers.Factory(
        device_manufacturer_service.DeviceManufacturerService,
        device_manufacturer_repository=device_manufacturer_repository,
    )
    device_service = providers.Factory(
        device_service.DeviceService, device_repository=device_repository
    )
    equipment_type_service = providers.Factory(
        equipment_type_service.EquipmentTypeService,
        equipment_type_repository=equipment_type_repository,
        equipment_repository=equipment_repository,
    )
    equipment_service = providers.Factory(
        equipment_service.EquipmentService,
        equipment_repository=equipment_repository,
    )
    feature_service = providers.Factory(
        feature_service.FeatureService,
        feature_repository=feature_repository,
    )
    invitation_service = providers.Factory(
        invitation_service.InvitationService,
        invitation_repository=team_member_invitation_repository,
    )
    marker_icon_service = providers.Factory(
        marker_icon_service.MarkerIconService,
        marker_icon_repository=marker_icon_repository,
    )
    onboarding_service = providers.Factory(
        onboarding_service.OnboardingService,
        asset_type_repository=asset_type_repository,
        package_repository=package_repository,
        user_repository=user_repository,
        feature_repository=feature_repository,
        onboarding_repository=onboarding_repository,
        onboarding_feature_assignment_repository=onboarding_feature_assignment_repository,
        onboarding_asset_type_assignment_repository=onboarding_asset_type_assignment_repository,
    )
    organisation_contact_service = providers.Factory(
        organisation_contact_service.OrganisationContactService,
        organisation_contact_repository=organisation_contact_repository,
        user_repository=user_repository,
    )
    phone_otp_service = providers.Factory(
        phone_otp_service.PhoneOTPService,
        phone_otp_repository=phone_otp_repository,
        user_repository=user_repository,
    )
    package_item_service = providers.Factory(
        package_item_service.PackageItemService,
        package_item_repository=package_item_repository,
    )
    package_service = providers.Factory(
        package_service.PackageService,
        package_repository=package_repository,
    )
    tracking_event_service = providers.Factory(
        tracking_event_service.TrackingEventService,
        tracking_event_repository=tracking_event_repository,
    )
    subscription_service = providers.Factory(
        subscription_service.SubscriptionService,
        subscription_repository=subscription_repository,
    )
    subscription_payment_service = providers.Factory(
        subscription_payment_service.SubscriptionPaymentService,
        subscription_payment_repository=subscription_payment_repository,
    )
    payment_service = providers.Factory(
        payment_service.PaymentService,
        payment_repository=payment_repository,
    )
    reset_password_service = providers.Factory(
        reset_password_service.ResetPassword,
        reset_password_repository=reset_password_repository,
    )
    plan_upgrade_service = providers.Factory(
        plan_updgrade_service.PlanUpgradeService,
        plan_upgrade_repository=plan_upgrade_repository,
    )
    user_subscription_service = providers.Factory(
        user_subscription_service.UserSubscriptionService,
        user_subscription_repository=user_subscription_repository,
    )
    inventory_service = providers.Factory(
        inventory_service.InventoryService,
        inventory_repository=inventory_repository,
        device_repository=device_repository,
        device_image_repository=device_image_repository,
    )
    device_image_service = providers.Factory(
        device_image_service.DeviceImageService,
        device_image_repository=device_image_repository,
    )
    order_service = providers.Factory(
        order_service.OrderService,
        order_repository=order_repository,
        order_device_assignment_repository=order_device_assignment_repository,
        order_shipping_address_repository=order_shipping_address_repository,
        inventory_repository=inventory_repository,
        device_repository=device_repository,
    )
    order_device_assignment_service = providers.Factory(
        order_device_assignment_service.OrderDeviceAssignmentService,
        order_device_assignment_repository=order_device_assignment_repository,
    )
    order_shipping_address_service = providers.Factory(
        order_shipping_address_service.OrderShippingAddressService,
        order_shipping_address_repository=order_shipping_address_repository,
    )
    external_app_service = providers.Factory(
        external_app_service.ExternalAppService,
        external_app_repository=external_app_repository,
    )
    immobilizer_report_service = providers.Factory(
        immobilizer_report_service.ImmobilizerReportService,
        immobilizer_report_repository=immobilizer_report_repository,
    )
