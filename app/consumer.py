from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware

from app.core.container import Container
from app.core.logger import get_logger
from app.core.settings import settings
from app.util.class_object import singleton


@singleton
class AppCreator:
    def __init__(self):
        # set app default
        self.app = FastAPI(
            title=settings.PROJECT_NAME + " - Consumer",
            version=settings.API_VERSION
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
            return "consumer is working"


app_creator = AppCreator()
app = app_creator.app
db = app_creator.db
container = app_creator.container
mqtt_service = app_creator.mqtt_service
