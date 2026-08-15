import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.connection import engine, Base, SessionLocal
from app.database.seed import seed_database
from app.api import telemetry, trucks, tyres, inspections, hotspots, maintenance, alerts, dashboard, analytics

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tyreiq_backend")

# Initialize DB tables
Base.metadata.create_all(bind=engine)

# Auto seed database if empty
with SessionLocal() as db_session:
    seed_database(db_session)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Explainable Mining Dumper Tyre Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev/prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )

# Register API Routers
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(telemetry.router, prefix=settings.API_V1_STR)
app.include_router(trucks.router, prefix=settings.API_V1_STR)
app.include_router(tyres.router, prefix=settings.API_V1_STR)
app.include_router(inspections.router, prefix=settings.API_V1_STR)
app.include_router(hotspots.router, prefix=settings.API_V1_STR)
app.include_router(maintenance.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)

@app.get("/")
@app.get(settings.API_V1_STR)
@app.get(f"{settings.API_V1_STR}/")
def root():
    return {
        "message": "Welcome to TyreIQ Mining Dumper Tyre Intelligence API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "endpoints": [
            f"{settings.API_V1_STR}/dashboard/summary",
            f"{settings.API_V1_STR}/trucks",
            f"{settings.API_V1_STR}/tyres",
            f"{settings.API_V1_STR}/telemetry",
            f"{settings.API_V1_STR}/vision/predict",
            f"{settings.API_V1_STR}/hotspots",
            f"{settings.API_V1_STR}/maintenance/priorities",
            f"{settings.API_V1_STR}/alerts"
        ]
    }
