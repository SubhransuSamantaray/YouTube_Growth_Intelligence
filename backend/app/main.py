"""
Main FastAPI Application Entrypoint.
Initializes database tables, mounts API routes, static frontend assets,
and handles startup auto-seeding.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.api import api_router
from backend.app.services.ingestion_service import IngestionService
from backend.app.models.schema import DerivedVideoMetrics

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables are created
    Base.metadata.create_all(bind=engine)
    
    # Check if database is empty; if so, automatically seed synthetic channel data
    db = SessionLocal()
    try:
        video_count = db.query(DerivedVideoMetrics).count()
        if video_count == 0:
            print("[INFO] Database empty. Seeding realistic sample channel data...")
            service = IngestionService(db)
            service.seed_synthetic_channel("DevPulse Systems")
            print("[INFO] Database seeded successfully.")
    except Exception as e:
        print(f"[ERROR] Auto-seed failed: {e}")
    finally:
        db.close()

    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware (Explicit allowlist)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows local dev and testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_PREFIX)

# Mount Static Frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
