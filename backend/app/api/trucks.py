from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.all_schemas import TruckOut, TruckLiveTelemetry
from app.services import truck_service

router = APIRouter(prefix="/trucks", tags=["Truck Fleet"])

@router.get("", response_model=List[TruckOut])
def list_trucks(db: Session = Depends(get_db)):
    """
    Get all dump trucks in fleet with live status.
    """
    return truck_service.get_all_trucks(db)

@router.get("/{truck_id}", response_model=TruckOut)
def get_truck(truck_id: str, db: Session = Depends(get_db)):
    """
    Get single truck details.
    """
    truck = truck_service.get_truck_by_id(db, truck_id)
    if not truck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Truck {truck_id} not found")
    return truck

@router.get("/{truck_id}/live", response_model=TruckLiveTelemetry)
def get_truck_live(truck_id: str, db: Session = Depends(get_db)):
    """
    Get real-time live telemetry stream for a specific truck and its 6 tyres.
    """
    live_data = truck_service.get_truck_live_telemetry(db, truck_id)
    if not live_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Truck {truck_id} not found")
    return live_data
