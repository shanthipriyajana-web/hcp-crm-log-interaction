from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Interaction
from app.schemas import SubmitRequest, InteractionOut

router = APIRouter()


@router.post("/interactions", response_model=InteractionOut)
def submit_interaction(payload: SubmitRequest, db: Session = Depends(get_db)):
    data = payload.form_state.model_dump()
    if not data.get("hcp_name") or not data.get("date") or not data.get("interaction_type") or not data.get("sentiment"):
        raise HTTPException(status_code=400, detail="Form is missing required fields")

    record = Interaction(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/interactions", response_model=List[InteractionOut])
def list_interactions(db: Session = Depends(get_db)):
    return db.query(Interaction).order_by(Interaction.created_at.desc()).all()
