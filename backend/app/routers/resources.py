from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/", response_model=schemas.ResourceOut, status_code=201)
def create_resource(
    payload: schemas.ResourceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(models.RoleEnum.ADMIN, models.RoleEnum.MANAGER)),
):
    resource = models.Resource(**payload.model_dump(), created_by=current_user.id)
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get("/", response_model=List[schemas.ResourceOut])
def list_resources(
    type: Optional[models.ResourceTypeEnum] = Query(None),
    status: Optional[models.ResourceStatusEnum] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.Resource)
    if type:
        query = query.filter(models.Resource.type == type)
    if status:
        query = query.filter(models.Resource.status == status)
    return query.all()


@router.get("/{resource_id}", response_model=schemas.ResourceOut)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.patch("/{resource_id}", response_model=schemas.ResourceOut)
def update_resource(
    resource_id: int,
    payload: schemas.ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(models.RoleEnum.ADMIN, models.RoleEnum.MANAGER)),
):
    resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(resource, field, value)
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/{resource_id}", status_code=204)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(models.RoleEnum.ADMIN)),
):
    resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    db.delete(resource)
    db.commit()
