from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.alert_policy import (
    check_geofence_violation_handler,
    check_over_speeding_violation_handler,
)
from app.api.v1.routes import routers as v1_routers
from app.core.container import Container
from app.core.logger import get_logger, init_logger
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

        # set logger
        init_logger(settings.PROJECT_NAME, settings.GRAYLOG_HOST, settings.GRAYLOG_PORT)

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

    # check geofence vilation for every 3 minutes
    scheduler.add_job(
        check_geofence_violation_handler,
        "interval",
        minutes=3,
        id="check_geofence_violation",
    )

    # check over speeding every 2 minutes
    scheduler.add_job(
        check_over_speeding_violation_handler,
        "interval",
        minutes=2,
        id="check_over_speeding_violation",
    )


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
