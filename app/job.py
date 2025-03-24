from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.api.v1.endpoints.alert_policy import (
    check_geofence_violation_handler,
    check_idling_violation_handler,
    check_maintenance_handler,
    check_over_speeding_violation_handler,
)
from app.api.v1.endpoints.driver import check_drivers_license_expiry
from app.api.v1.endpoints.report import generate_smart_report_handler
from app.api.v1.endpoints.users import check_admin_invitation_handler
from app.core.container import Container
from app.core.logger import get_logger
from app.core.settings import settings
from app.util.class_object import singleton

# Create an instance of the scheduler
scheduler = AsyncIOScheduler()


@singleton
class AppCreator:
    def __init__(self):
        # set app default
        self.app = FastAPI(
            title=settings.PROJECT_NAME + " - Jobs",
            version=settings.API_VERSION,
        )

        # set db and container
        self.container = Container()
        self.db = self.container.db()

        # set routes
        @self.app.get("/")
        def root():
            return "job is working"


app_creator = AppCreator()
app = app_creator.app
db = app_creator.db
container = app_creator.container


@app.on_event("startup")
async def startup_event():
    get_logger().info("Starting the job schedulers")
    try:
        await db.create_database()
        if await db.connected():
            get_logger().info("Successfully connected to the PostgreSQL database")
        else:
            get_logger().error("Failed to connect to the PostgreSQL database")
    except Exception as e:
        get_logger().error(f"Failed to connect to the PostgreSQL database: {e}")
        raise e
    scheduler.start()
    if settings.ENV != "test":
        # check over speeding every 2 minutes
        scheduler.add_job(
            check_over_speeding_violation_handler,
            "interval",
            minutes=2,
            id="check_over_speeding_violation",
        )

        # check geofence violation for every 3 minutes
        scheduler.add_job(
            check_geofence_violation_handler,
            "interval",
            minutes=3,
            id="check_geofence_violation",
        )

        # check maintenance alert
        scheduler.add_job(
            check_maintenance_handler,
            "interval",
            minutes=10,
            id="check_maintenance",
        )

        # check idling violation for every 5 minutes
        scheduler.add_job(
            check_idling_violation_handler,
            "interval",
            minutes=5,
            id="check_idling_violation",
        )

        # get new smart reports and generate report
        # scheduler.add_job(
        #     generate_smart_report_handler,
        #     "interval",
        #     minutes=10,
        #     id="smart_report_generation",
        # )

        # Check driver licences expiry
        scheduler.add_job(
            check_drivers_license_expiry,
            "interval",
            hours=3,
            id="check_license_expiry",
        )

        scheduler.add_job(
            check_admin_invitation_handler,
            "interval",
            hours=6,
            id="update invitation statuses",
        )


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    try:
        await db.close()
        get_logger().info("Successfully closed the PostgreSQL database")
    except Exception as e:
        get_logger().error(f"Failed to close the PostgreSQL database: {e}")
        raise e
