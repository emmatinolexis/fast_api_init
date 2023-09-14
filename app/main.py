from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import system
from app.routers import users
from app.routers import packages
from app.routers import asset_types
from app.routers import assets

from app.routers import authentication
from app.database.core import init_db

app = FastAPI()

app.include_router(system.router)
app.include_router(users.router)
app.include_router(packages.router)
app.include_router(asset_types.router)
app.include_router(assets.router)
app.include_router(authentication.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "https://localhost:8000",
        "http://localhost",
        "https://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
