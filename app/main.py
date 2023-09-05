from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

allowed_origins = [
    "http://localhost:8000",
    "https://localhost:8000",
    "http://localhost",
    "https://localhost",
]

app.add_middleware(
    CORSMiddleware(
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
)

@app.get("/health")
async def health():
    return {
        "status": "available",
        "version": "0.0.1",
    }