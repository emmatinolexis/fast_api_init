from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.core import init_db
from app.routers import (
    alert_maintenance_types,
    alert_policy,
    alert_policy_asset,
    alert_policy_notifications,
    alert_policy_type,
    alert_recipient,
    asset_location,
    asset_types,
    assets,
    authentication,
    contact,
    driver,
    equipment_type,
    equipments,
    features,
    marker_icon,
    onboarding,
    organisation_contact,
    package_items,
    packages,
    system,
    tracking,
    users,
)

app = FastAPI(
    title="MVI Tracking",
    description=None,
    summary="",
    version="0.0.1",
)

app.include_router(system.router)
app.include_router(users.router)
app.include_router(packages.router)
app.include_router(package_items.router)
app.include_router(asset_types.router)
app.include_router(assets.router)
app.include_router(onboarding.router)
app.include_router(authentication.router)
app.include_router(features.router)
app.include_router(contact.router)
app.include_router(organisation_contact.router)
app.include_router(marker_icon.router)
app.include_router(asset_location.router)
app.include_router(equipment_type.router)
app.include_router(driver.router)
app.include_router(tracking.router)
app.include_router(alert_policy_type.router)
app.include_router(equipments.router)
app.include_router(alert_policy.router)
app.include_router(alert_policy_asset.router)
app.include_router(alert_recipient.router)
app.include_router(alert_policy_notifications.router)
app.include_router(alert_maintenance_types.router)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     "http://localhost:8000",
    #     "https://localhost:8000",
    #     "http://localhost:3000",
    #     "http://localhost",
    # ],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
