from fastapi import FastAPI

from src.risk_platform.api.routes import router


app = FastAPI(
    title="Risk Analytics API",
    description="API for the Risk Analytics Platform",
    version="1.0.0"
)

app.include_router(router)