from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.risk_platform.api.routes import router


app = FastAPI(
    title="Risk Analytics API",
    description="API for the Risk Analytics Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)