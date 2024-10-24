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
    asset_operator_assignment_repository,
    asset_repository,
    asset_type_repository,
    building_repository,
    business_profile_repository,
    contact_sale_repository,
    default_device_gateway_configuration_repository,
    device_alert_notification_repository,
    device_configuration_repository,
    device_events_repository,
    device_image_repository,
    device_manufacturer_repository,
    device_node_configuration_repository,
    device_repository,
    driver_license_repository,
    driver_repository,
    email_verification_repository,
    equipment_repository,
    equipment_type_repository,
    external_app_repository,
    feature_repository,
    fine_report_repository,
    fuel_log_repository,
    gas_cylinder_event_repository,
    gas_cylinder_repository,
    gas_cylinder_type_repository,
    gas_device_repository,
    gateway_configuration_repository,
    geofence_violation_tracker_repository,
    immobilizer_report_repository,
    incident_repository,
    inventory_repository,
    maintenance_alert_repository,
    marker_icon_repository,
    onboarding_asset_type_assignment_repository,
    onboarding_feature_assignment_repository,
    onboarding_repository,
    order_device_assignment_repository,
    order_repository,
    order_shipping_address_repository,
    organisation_contact_repository,
    other_cylinder_types_repository,
    package_item_assignments_repository,
    package_item_repository,
    package_repository,
    payment_repository,
    peripheral_devices_repository,
    permission_repository,
    phone_otp_repository,
    plan_upgrade_repository,
    reset_password_repository,
    role_permission_assignment_repository,
    role_repository,
    smart_report_repository,
    subscription_payment_repository,
    subscription_repository,
    team_member_invitation_repository,
    theft_incidence_repository,
    theft_report_repository,
    third_party_app_repository,
    third_party_app_user_repository,
    tracking_event_repository,
    user_organisation_assignment_repository,
    user_repository,
    user_subscription_repository,
    vehicle_make_repository,
    vehicle_model_repository,
    vehicle_owner_repository,
)
from app.service import (
    alert_maintenance_type_service,
    alert_policy_service,
    alert_policy_type_service,
    asset_device_request_service,
    asset_location_service,
    asset_operator_assignment_service,
    asset_service,
    asset_type_service,
    auth_service,
    building_service,
    business_profile_service,
    contact_sale_service,
    default_device_gateway_configuration_service,
    device_alert_notification_service,
    device_configuration_service,
    device_events_service,
    device_image_service,
    device_manufacturer_service,
    device_service,
    driver_license_service,
    driver_service,
    equipment_service,
    equipment_type_service,
    external_app_service,
    feature_service,
    fine_report_service,
    fuel_log_service,
    gas_cylinder_event_service,
    gas_cylinder_service,
    gas_cylinder_type_service,
    gas_device_service,
    gateway_configuration_service,
    geofence_violation_tracker_service,
    immobilizer_report_service,
    incident_service,
    inventory_service,
    invitation_service,
    maintenance_alert_service,
    marker_icon_service,
    onboarding_service,
    order_device_assignment_service,
    order_service,
    order_shipping_address_service,
    organisation_contact_service,
    other_cylinder_type_service,
    package_item_assignments_service,
    package_item_service,
    package_service,
    payment_service,
    peripheral_device_service,
    permission_service,
    phone_otp_service,
    plan_updgrade_service,
    reset_password_service,
    role_permission_assignment_service,
    role_service,
    smart_report_service,
    subscription_payment_service,
    subscription_service,
    theft_incidence_service,
    theft_report_service,
    third_party_app_service,
    third_party_app_user_service,
    tracking_event_service,
    user_service,
    user_subscription_service,
    vehicle_make_service,
    vehicle_model_service,
    vehicle_owner_service,
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
            "app.api.v1.endpoints.permission",
            "app.api.v1.endpoints.vehicle_make",
            "app.api.v1.endpoints.third_party_app",
            "app.api.v1.endpoints.fine_report",
            "app.api.v1.endpoints.report",
            "app.api.v1.endpoints.gas_cylinder",
            "app.api.v1.endpoints.gas_device",
            "app.api.v1.endpoints.gas_cylinder_type",
            "app.api.v1.endpoints.fuel_log",
            "app.api.v1.endpoints.fire_device",
            "app.api.v1.endpoints.incident",
            "app.api.v1.endpoints.peripheral_device",
            "app.api.v1.endpoints.gateway_configuration",
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
    package_item_assignments_repository = providers.Factory(
        package_item_assignments_repository.PackageItemAssignmentRepository,
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
    theft_incidence_repository = providers.Factory(
        theft_incidence_repository.TheftIncidenceRepository,
        session_factory=db.provided.session,
    )

    theft_report_repository = providers.Factory(
        theft_report_repository.TheftReportRepository,
        session_factory=db.provided.session,
    )

    vehicle_model_repository = providers.Factory(
        vehicle_model_repository.VehicleModelRepository,
        session_factory=db.provided.session,
    )
    vehicle_make_repository = providers.Factory(
        vehicle_make_repository.VehicleMakeRepository,
        session_factory=db.provided.session,
    )
    third_party_app_repository = providers.Factory(
        third_party_app_repository.ThirdPartyAppRepository,
        session_factory=db.provided.session,
    )
    third_party_app_user_repository = providers.Factory(
        third_party_app_user_repository.ThirdPartAppUserRepository,
        session_factory=db.provided.session,
    )
    vehicle_owner_repository = providers.Factory(
        vehicle_owner_repository.VehicleOwnerRepository,
        session_factory=db.provided.session,
    )
    fine_report_repository = providers.Factory(
        fine_report_repository.FineReportRepository,
        session_factory=db.provided.session,
    )
    geofence_violation_tracker_repository = providers.Factory(
        geofence_violation_tracker_repository.GeofenceViolationTrackerRepository,
        session_factory=db.provided.session,
    )
    maintenance_alert_repository = providers.Factory(
        maintenance_alert_repository.MaintenanceAlertRepository,
        session_factory=db.provided.session,
    )
    gas_cylinder_repository = providers.Factory(
        gas_cylinder_repository.GasCylinderRepository,
        session_factory=db.provided.session,
    )
    gas_cylinder_event_repository = providers.Factory(
        gas_cylinder_event_repository.GasCylinderEventRepository,
        session_factory=db.provided.session,
    )
    gas_device_repository = providers.Factory(
        gas_device_repository.GasDeviceRepository,
        session_factory=db.provided.session,
    )
    gas_cylinder_type_repository = providers.Factory(
        gas_cylinder_type_repository.GasCylinderTypeRepository,
        session_factory=db.provided.session,
    )

    other_cylinder_types_repository = providers.Factory(
        other_cylinder_types_repository.OtherCylinderTypeRepository,
        session_factory=db.provided.session,
    )

    building_repository = providers.Factory(
        building_repository.BuildingRepository,
        session_factory=db.provided.session,
    )
    smart_report_repository = providers.Factory(
        smart_report_repository.SmartReportRepository,
        session_factory=db.provided.session,
    )
    fuel_log_repository = providers.Factory(
        fuel_log_repository.FuelLogRepository,
        session_factory=db.provided.session,
    )
    device_event_repository = providers.Factory(
        device_events_repository.DeviceEventRepository,
        session_factory=db.provided.session,
    )

    incident_repository = providers.Factory(
        incident_repository.IncidentRepository, session_factory=db.provided.session
    )

    peripheral_devices_repository = providers.Factory(
        peripheral_devices_repository.PeripheralDeviceRepository,
        session_factory=db.provided.session,
    )
    gateway_configuration_repository = providers.Factory(
        gateway_configuration_repository.GatewayConfigurationRepository,
        session_factory=db.provided.session,
    )

    default_device_gateway_configuration_repository = providers.Factory(
        default_device_gateway_configuration_repository.DefaultDeviceGatewayConfigurationRepository,
        session_factory=db.provided.session,
    )

    device_configuration_repository = providers.Factory(
        device_configuration_repository.DeviceConfigurationRepository,
        session_factory=db.provided.session,
    )

    device_node_configuration_repository = providers.Factory(
        device_node_configuration_repository.DeviceNodeConfigRepository,
        session_factory=db.provided.session,
    )

    device_alert_notification_repository = providers.Factory(
        device_alert_notification_repository.DeviceAlertNotificationRepository,
        session_factory=db.provided.session,
    )

    asset_operator_assignment_repository = providers.Factory(
        asset_operator_assignment_repository.AssetOperatorTypeAssignmentRepository,
        session_factory=db.provided.session,
    )

    driver_license_repository = providers.Factory(
        driver_license_repository.DriverLicenseRepository,
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
        asset_repository=asset_repository,
        driver_license_repository=driver_license_repository,
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
    package_item_assignments_service = providers.Factory(
        package_item_assignments_service.PackageItemAssignmentService,
        package_item_assignments_repository=package_item_assignments_repository,
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
        theft_incidence_repository=theft_incidence_repository,
        theft_report_repository=theft_report_repository,
        vehicle_owner_repository=vehicle_owner_repository,
        tracking_event_repository=tracking_event_repository,
        gas_cylinder_repository=gas_cylinder_repository,
        gas_cylinder_event_repository=gas_cylinder_event_repository,
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
        peripheral_devices_repository=peripheral_devices_repository,
        device_configuration_repository=device_configuration_repository,
    )
    immobilizer_report_service = providers.Factory(
        immobilizer_report_service.ImmobilizerReportService,
        immobilizer_report_repository=immobilizer_report_repository,
    )
    permission_service = providers.Factory(
        permission_service.PermissionService,
        permission_repository=permissions_repository,
    )
    role_service = providers.Factory(
        role_service.RoleService,
        role_repository=role_repository,
        role_permission_assignment_repository=role_permission_assignment_repository,
    )
    role_permission_assignment_service = providers.Factory(
        role_permission_assignment_service.RolePermissionAssignmentService,
        role_permission_assignment_repositoryrepository=role_permission_assignment_repository,
    )
    theft_incidence_service = providers.Factory(
        theft_incidence_service.TheftIncidenceService,
        theft_incidence_repository=theft_incidence_repository,
    )
    theft_report_service = providers.Factory(
        theft_report_service.TheftReportService,
        theft_report_repository=theft_report_repository,
    )
    vehicle_model_service = providers.Factory(
        vehicle_model_service.VehicleModelService,
        vehicle_model_repository=vehicle_model_repository,
    )
    vehicle_make_service = providers.Factory(
        vehicle_make_service.VehicleMakeService,
        vehicle_make_repository=vehicle_make_repository,
        vehicle_model_repository=vehicle_model_repository,
    )
    third_party_app_service = providers.Factory(
        third_party_app_service.ThirdPartyAppService,
        third_party_app_repository=third_party_app_repository,
    )
    third_party_app_user_service = providers.Factory(
        third_party_app_user_service.ThirdPartyAppUserService,
        third_party_app_user_repository=third_party_app_user_repository,
    )
    vehicle_owner_service = providers.Factory(
        vehicle_owner_service.VehicleOwnerService,
        vehicle_owner_repository=vehicle_owner_repository,
    )
    business_profile_service = providers.Factory(
        business_profile_service.BusinessProfileService,
        package_item_assignments_service=package_item_assignments_service,
        business_profile_repository=business_profile_repository,
    )
    fine_report_service = providers.Factory(
        fine_report_service.FineReportService,
        fine_report_repository=fine_report_repository,
    )
    geofence_violation_tracker_service = providers.Factory(
        geofence_violation_tracker_service.GeofenceViolationTrackerService,
        geofence_violation_tracker_repository=geofence_violation_tracker_repository,
    )
    maintenance_alert_service = providers.Factory(
        maintenance_alert_service.MaintenanceAlertService,
        maintenance_alert_repository=maintenance_alert_repository,
    )
    gas_cylinder_service = providers.Factory(
        gas_cylinder_service.GasCylinderService,
        gas_cylinder_repository=gas_cylinder_repository,
        gas_device_repository=gas_device_repository,
    )
    gas_cylinder_event_service = providers.Factory(
        gas_cylinder_event_service.GasCylinderEventService,
        gas_cylinder_event_repository=gas_cylinder_event_repository,
        gas_cylinder_repository=gas_cylinder_repository,
        gas_cylinder_type_repository=gas_cylinder_type_repository,
    )
    gas_device_service = providers.Factory(
        gas_device_service.GasDeviceService,
        gas_device_repository=gas_device_repository,
    )
    gas_cylinder_type_service = providers.Factory(
        gas_cylinder_type_service.GasCylinderTypeService,
        gas_cylinder_type_repository=gas_cylinder_type_repository,
    )

    other_cylinder_type_service = providers.Factory(
        other_cylinder_type_service.OtherCylinderTypeService,
        other_cylinder_type_repository=other_cylinder_types_repository,
        user_repository=user_repository,
    )

    building_service = providers.Factory(
        building_service.BuildingService,
        building_repository=building_repository,
        gas_device_repository=gas_device_repository,
        gas_cylinder_repository=gas_cylinder_repository,
        user_repository=user_repository,
        peripheral_device_repository=peripheral_devices_repository,
    )

    smart_report_service = providers.Factory(
        smart_report_service.SmartReportService,
        smart_report_repository=smart_report_repository,
        asset_repository=asset_repository,
        tracking_event_repository=tracking_event_repository,
        equipment_repository=equipment_repository,
        alert_policy_repository=alert_policy_repository,
        user_repository=user_repository,
        fuel_log_repository=fuel_log_repository,
    )

    fuel_log_service = providers.Factory(
        fuel_log_service.FuelLogService,
        fuel_log_repository=fuel_log_repository,
        asset_repository=asset_repository,
        driver_repository=driver_repository,
        user_repository=user_repository,
        asset_operator_assignment_repository=asset_operator_assignment_repository
    )

    device_events_service = providers.Factory(
        device_events_service.DeviceEventService,
        device_event_repository=device_event_repository,
    )

    incident_service = providers.Factory(
        incident_service.IncidentService,
        incident_repository=incident_repository,
    )

    peripheral_device_service = providers.Factory(
        peripheral_device_service.PeripheralDeviceService,
        peripheral_device_repository=peripheral_devices_repository,
        user_repository=user_repository,
        device_events_service=device_events_service,
        device_node_config_repository=device_node_configuration_repository,
        device_event_repository=device_event_repository,
        gas_cylinder_repository=gas_cylinder_repository,
    )

    device_configuration_service = providers.Factory(
        device_configuration_service.DeviceConfigurationService,
        device_configuration_repository=device_configuration_repository,
    )

    gateway_configuration_service = providers.Factory(
        gateway_configuration_service.GateWayConfigurationService,
        gateway_configuration_repository=gateway_configuration_repository,
    )

    default_device_gateway_configuration_service = providers.Factory(
        default_device_gateway_configuration_service.DefaultDeviceGatewayConfigurationService,
        default_device_gateway_configuration_repository=default_device_gateway_configuration_repository,
    )

    device_alert_notification_service = providers.Factory(
        device_alert_notification_service.DeviceAlertNotificationService,
        device_alert_notification_repository=device_alert_notification_repository,
    )

    asset_operator_assignment_service = providers.Factory(
        asset_operator_assignment_service.AssetOperatorAssignmentService,
        asset_operator_assignment=asset_operator_assignment_repository,
        asset_repository=asset_repository,
        user_repository=user_repository,
    )

    driver_license_service = providers.Factory(
        driver_license_service.DriverLicenseService,
        driver_license_repository=driver_license_repository,
    )
