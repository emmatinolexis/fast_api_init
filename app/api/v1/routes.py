from fastapi import APIRouter

from app.api.v1.endpoints.activity_logs import (
    admin_router as admin_activity_logs_router,
)
from app.api.v1.endpoints.activity_logs import router as activity_logs_router
from app.api.v1.endpoints.admin_notification import router as admin_notification_router
from app.api.v1.endpoints.alert_maintenance_type import (
    router as alert_maintenance_type_router,
)
from app.api.v1.endpoints.alert_policy import router as alert_policy_router
from app.api.v1.endpoints.alert_policy_type import router as alert_policy_type_router
from app.api.v1.endpoints.asset import router as asset_router
from app.api.v1.endpoints.asset_location import router as asset_location_router
from app.api.v1.endpoints.asset_type import router as asset_type_router
from app.api.v1.endpoints.authentication import router as auth_router
from app.api.v1.endpoints.contact_sales import router as contact_sales_router
from app.api.v1.endpoints.device import router as device_router
from app.api.v1.endpoints.device_manufacturers import (
    router as device_manufacturers_router,
)
from app.api.v1.endpoints.driver import router as driver_router
from app.api.v1.endpoints.equipment import router as equipment_router
from app.api.v1.endpoints.equipment_type import router as equipment_type_router
from app.api.v1.endpoints.external_app import router as external_app_router
from app.api.v1.endpoints.feature import router as feature_router
from app.api.v1.endpoints.fine_report import router as fine_report_router
from app.api.v1.endpoints.fire_device import router as fire_device_router
from app.api.v1.endpoints.fuel_log import router as fuel_log_router
from app.api.v1.endpoints.gas_cylinder import router as gas_cylinder_router
from app.api.v1.endpoints.gas_cylinder_type import router as gas_cylinder_type_router
from app.api.v1.endpoints.gas_device import router as gas_device_router
from app.api.v1.endpoints.gateway_configuration import (
    router as gateway_configuration_router,
)
from app.api.v1.endpoints.health_check import router as health_check_router
from app.api.v1.endpoints.incident import router as incident_router
from app.api.v1.endpoints.installation import router as installlation_router
from app.api.v1.endpoints.inventory import router as inventory_router
from app.api.v1.endpoints.marker_icon import router as marker_icon_router
from app.api.v1.endpoints.notification import router as notification_router
from app.api.v1.endpoints.onboarding import router as onboarding_router
from app.api.v1.endpoints.order import router as order_router
from app.api.v1.endpoints.organisation_contact import (
    router as organisation_contact_router,
)
from app.api.v1.endpoints.package import router as package_router
from app.api.v1.endpoints.package_item import router as package_item_router
from app.api.v1.endpoints.payment import router as payment_router
from app.api.v1.endpoints.peripheral_device import router as peripheral_device_router
from app.api.v1.endpoints.permission import router as permission_router
from app.api.v1.endpoints.report import router as report_router
from app.api.v1.endpoints.rnd_images import router as rnd_image_router
from app.api.v1.endpoints.subscription import router as subscription_router

# from app.api.v1.endpoints.subscription_payment import (
#     router as subscription_payment_router,
# )
from app.api.v1.endpoints.third_party_app import router as third_party_router
from app.api.v1.endpoints.tracking import router as tracking_router
from app.api.v1.endpoints.upload import router as upload_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.vehicle_make import router as vehicle_make_router

routers = APIRouter()
router_list = [
    health_check_router,
    auth_router,
    upload_router,
    users_router,
    package_item_router,
    package_router,
    alert_policy_type_router,
    alert_maintenance_type_router,
    equipment_type_router,
    equipment_router,
    marker_icon_router,
    asset_type_router,
    asset_router,
    asset_location_router,
    alert_policy_router,
    driver_router,
    device_router,
    inventory_router,
    device_manufacturers_router,
    feature_router,
    organisation_contact_router,
    onboarding_router,
    tracking_router,
    subscription_router,
    payment_router,
    # subscription_payment_router,
    order_router,
    external_app_router,
    permission_router,
    vehicle_make_router,
    third_party_router,
    fine_report_router,
    report_router,
    gas_cylinder_router,
    gas_device_router,
    gas_cylinder_type_router,
    fuel_log_router,
    fire_device_router,
    incident_router,
    peripheral_device_router,
    gateway_configuration_router,
    installlation_router,
    notification_router,
    contact_sales_router,
    admin_notification_router,
    activity_logs_router,
    admin_activity_logs_router,
    rnd_image_router,
]

for router in router_list:
    routers.include_router(router)
