from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.all_schemas import TyreOut, RiskResponse
from app.services import tyre_service

router = APIRouter(prefix="/tyres", tags=["Tyres & Analytics"])

@router.get("", response_model=List[TyreOut])
def list_tyres(db: Session = Depends(get_db)):
    """
    Get all tyres with telemetry, position, wear, and risk status.
    """
    return tyre_service.get_all_tyres(db)

@router.get("/{tyre_id}", response_model=TyreOut)
def get_tyre(tyre_id: str, db: Session = Depends(get_db)):
    """
    Get single tyre master data and latest telemetry.
    """
    tyre = tyre_service.get_tyre_by_id(db, tyre_id)
    if not tyre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tyre {tyre_id} not found")
    return tyre

@router.get("/{tyre_id}/risk", response_model=RiskResponse)
def get_tyre_risk_assessment(tyre_id: str, db: Session = Depends(get_db)):
    """
    Get explainable Mamdani fuzzy failure-risk score, reasons, and recommended action.
    """
    return tyre_service.get_tyre_risk(db, tyre_id)
