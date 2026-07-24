from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/penalties", tags=["penalties"])


@router.get("/", response_model=List[schemas.PenaltyOut])
def list_penalties(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.Penalty)
    if current_user.role == models.RoleEnum.USER:
        query = query.filter(models.Penalty.user_id == current_user.id)
    return query.order_by(models.Penalty.created_at.desc()).all()


@router.patch("/{penalty_id}/pay", response_model=schemas.PenaltyOut)
def mark_paid(
    penalty_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(models.RoleEnum.ADMIN, models.RoleEnum.MANAGER)),
):
    penalty = db.query(models.Penalty).filter(models.Penalty.id == penalty_id).first()
    if not penalty:
        raise HTTPException(status_code=404, detail="Penalty not found")
    penalty.is_paid = True
    db.commit()
    db.refresh(penalty)
    return penalty
