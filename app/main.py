from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import system
from app.routers import users
from app.routers import packages
from app.routers import package_items
from app.routers import asset_types
from app.routers import assets
from app.routers import features

from app.routers import authentication
from app.database.core import init_db

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
app.include_router(authentication.router)
app.include_router(features.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "https://localhost:8000",
        "http://localhost:3000",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
