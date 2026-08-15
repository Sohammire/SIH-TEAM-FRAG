from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.all_schemas import DashboardSummaryOut
from app.services import truck_service, tyre_service, alert_service, hotspot_service

router = APIRouter(tags=["Dashboard & Health"])

@router.get("/dashboard/summary", response_model=DashboardSummaryOut)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Get aggregated dashboard summary metrics.
    """
    trucks = truck_service.get_all_trucks(db)
    tyres = tyre_service.get_all_tyres(db)
    alerts = alert_service.get_alerts(db)
    hotspots = hotspot_service.get_hotspots(db)

    active_trucks = sum(1 for t in trucks if t["status"] == "active")
    high_risk = sum(1 for t in tyres if t["risk_label"] == "HIGH")
    med_risk = sum(1 for t in tyres if t["risk_label"] == "MEDIUM")
    low_risk = sum(1 for t in tyres if t["risk_label"] == "LOW")

    active_alerts_cnt = sum(1 for a in alerts if a["status"] == "active")
    crit_maint_cnt = sum(1 for t in tyres if t["risk_label"] == "HIGH")

    avg_temp = sum(t["current_temp_c"] for t in tyres) / len(tyres) if tyres else 65.0
    avg_press = sum(t["current_pressure_kpa"] for t in tyres) / len(tyres) if tyres else 725.0
    avg_tkph = sum(t["tkph_current"] for t in tyres) / len(tyres) if tyres else 1450.0

    return DashboardSummaryOut(
        total_trucks=len(trucks),
        active_trucks=active_trucks,
        total_tyres=len(tyres),
        high_risk_tyres=high_risk,
        medium_risk_tyres=med_risk,
        low_risk_tyres=low_risk,
        active_alerts=active_alerts_cnt,
        critical_maintenance=crit_maint_cnt,
        avg_temperature_c=round(avg_temp, 1),
        avg_pressure_kpa=round(avg_press, 1),
        avg_tkph=round(avg_tkph, 1),
        road_hotspot_count=sum(1 for h in hotspots if h["hotspot_score"] >= 60.0)
    )

@router.get("/health")
def health_check():
    """
    System health status check.
    """
    return {
        "status": "healthy",
        "service": "TyreIQ FastAPI Backend",
        "version": "1.0.0",
        "database": "connected"
    }
