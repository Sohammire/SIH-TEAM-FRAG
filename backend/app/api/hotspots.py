from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.all_schemas import HotspotResponse
from app.services import hotspot_service

router = APIRouter(prefix="/hotspots", tags=["Geographical Hotspots"])

@router.get("", response_model=List[HotspotResponse])
def get_road_hotspots(
    traffic_multiplier: float = Query(1.0, description="Traffic multiplier for exposure testing (1.0 = base, 2.0 = doubled traffic)"),
    db: Session = Depends(get_db)
):
    """
    Get mine-road risk hotspots normalized per 100 truck-km exposure.
    Supports traffic doubling testing (doubling traffic without extra events decreases normalized rate).
    """
    return hotspot_service.get_hotspots(db, traffic_multiplier=traffic_multiplier)
