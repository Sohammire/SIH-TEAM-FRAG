from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.all_schemas import MaintenancePriorityOut
from app.services import maintenance_service

router = APIRouter(prefix="/maintenance", tags=["Maintenance Priority"])

@router.get("/priorities", response_model=List[MaintenancePriorityOut])
def get_maintenance_priority_queue(db: Session = Depends(get_db)):
    """
    Get priority-ranked maintenance queue.
    Rule: Severe damage + pressure loss outranks TKPH-only warning.
    """
    return maintenance_service.get_maintenance_priorities(db)
