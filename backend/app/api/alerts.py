from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.all_schemas import AlertOut
from app.services import alert_service

router = APIRouter(prefix="/alerts", tags=["Alert Center"])

@router.get("", response_model=List[AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    """
    Get active and resolved alerts.
    """
    return alert_service.get_alerts(db)
