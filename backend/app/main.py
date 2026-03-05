# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.models import domain
from app.api.routes import router as logging_router
from app.api.analytics import router as analytics_router  # Import the new router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Academic Reporting System API",
    description="Backend services for the AI-driven academic reporting pipeline.",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routing modules
app.include_router(logging_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")  # Register analytics


@app.get("/health")
async def health_check() -> dict:
    return {"status": "operational", "service": "academic-reporting-api"}
