from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {
        "status": "available",
        "version": "0.0.1",
    }