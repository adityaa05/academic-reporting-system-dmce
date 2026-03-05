# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.models import domain
from app.api.routes import router as api_router


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

# Register the API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "operational", "service": "academic-reporting-api"}
