from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.alert_policy import (
    check_geofence_violation_handler,
    check_idling_violation_handler,
    check_maintenance_handler,
    check_over_speeding_violation_handler,
)
from app.api.v1.endpoints.report import generate_smart_report_handler
from app.api.v1.routes import routers as v1_routers
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
            title=settings.PROJECT_NAME,
            openapi_url=f"{settings.API}/openapi.json",
            version=settings.API_VERSION,
        )

        # Initialize prometheus middleware
        Instrumentator().instrument(self.app).expose(self.app)

        # set db and container
        self.container = Container()
        self.db = self.container.db()
        self.db.create_database()

        if self.db.connected():
            get_logger().info("Successfully connected to the PostgreSQL database")
        else:
            get_logger().error("Failed to connect to the PostgreSQL database")

        # set mqtt service
        self.mqtt_service = self.container.mqtt_service()
        self.mqtt_client = self.mqtt_service.connect_mqtt()
        self.mqtt_service.subscribe(self.mqtt_client)

        # set cors
        if settings.BACKEND_CORS_ORIGINS:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        # set routes
        @self.app.get("/")
        def root():
            return "service is working"

        self.app.include_router(v1_routers, prefix=settings.API_V1_STR)


app_creator = AppCreator()
app = app_creator.app
db = app_creator.db
container = app_creator.container
mqtt_service = app_creator.mqtt_service


@app.on_event("startup")
async def startup_event():
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

        # check geofence violation for every 3 minutes
        scheduler.add_job(
            check_idling_violation_handler,
            "interval",
            minutes=4,
            id="check_idling_violation",
        )

        # get new smart reports and generate report
        scheduler.add_job(
            generate_smart_report_handler,
            "interval",
            minutes=5,
            id="smart_report_generation",
        )


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
