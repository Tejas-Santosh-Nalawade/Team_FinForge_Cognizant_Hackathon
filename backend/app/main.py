from fastapi import FastAPI

from backend.app.api.v1.analytics import router as analytics_router

app = FastAPI(title="AuditAI Backend", version="1.0.0")
app.include_router(analytics_router)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}
