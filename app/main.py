from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import system

app = FastAPI()

app.include_router(system.router)

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

# @app.on_event("startup")
# def on_startup():
#     pass
#     # TODO initialize database here
