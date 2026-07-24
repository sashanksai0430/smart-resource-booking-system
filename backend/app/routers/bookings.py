from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..services.overlap import has_overlap

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=schemas.BookingOut, status_code=201)
def create_booking(
    payload: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    resource = db.query(models.Resource).filter(models.Resource.id == payload.resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    if resource.status != models.ResourceStatusEnum.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Resource is currently {resource.status.value}")

    if has_overlap(db, payload.resource_id, payload.start_time, payload.end_time):
        raise HTTPException(status_code=409, detail="Resource is already booked for the selected time slot")

    # Admins/Managers auto-approve their own bookings; regular users need approval
    # unless the resource is flagged as not requiring it.
    auto_approve = (
        current_user.role in (models.RoleEnum.ADMIN, models.RoleEnum.MANAGER)
        or not resource.requires_approval
    )

    booking = models.Booking(
        resource_id=payload.resource_id,
        user_id=current_user.id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        purpose=payload.purpose,
        status=models.BookingStatusEnum.APPROVED if auto_approve else models.BookingStatusEnum.PENDING,
        approved_by=current_user.id if auto_approve else None,
        approved_at=datetime.utcnow() if auto_approve else None,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/", response_model=List[schemas.BookingOut])
def list_bookings(
    resource_id: Optional[int] = Query(None),
    status: Optional[models.BookingStatusEnum] = Query(None),
    start: Optional[datetime] = Query(None, description="Filter bookings overlapping this range start"),
    end: Optional[datetime] = Query(None, description="Filter bookings overlapping this range end"),
    mine_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Also serves as the calendar-view data feed: pass start/end to fetch bookings for a visible date range."""
    query = db.query(models.Booking)

    if current_user.role == models.RoleEnum.USER or mine_only:
        query = query.filter(models.Booking.user_id == current_user.id)
    if resource_id:
        query = query.filter(models.Booking.resource_id == resource_id)
    if status:
        query = query.filter(models.Booking.status == status)
    if start and end:
        query = query.filter(models.Booking.start_time < end, models.Booking.end_time > start)

    return query.order_by(models.Booking.start_time).all()


@router.get("/pending-approvals", response_model=List[schemas.BookingOut])
def pending_approvals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(models.RoleEnum.ADMIN, models.RoleEnum.MANAGER)),
):
    return db.query(models.Booking).filter(
        models.Booking.status == models.BookingStatusEnum.PENDING
    ).order_by(models.Booking.start_time).all()


@router.post("/{booking_id}/decision", response_model=schemas.BookingOut)
def decide_booking(
    booking_id: int,
    payload: schemas.BookingDecision,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(models.RoleEnum.ADMIN, models.RoleEnum.MANAGER)),
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != models.BookingStatusEnum.PENDING:
        raise HTTPException(status_code=400, detail="Booking has already been decided")

    if payload.approve:
        # re-check overlap at decision time in case another booking was approved meanwhile
        if has_overlap(db, booking.resource_id, booking.start_time, booking.end_time, exclude_booking_id=booking.id):
            raise HTTPException(status_code=409, detail="Slot is no longer available")
        booking.status = models.BookingStatusEnum.APPROVED
    else:
        booking.status = models.BookingStatusEnum.REJECTED

    booking.approved_by = current_user.id
    booking.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{booking_id}/cancel", response_model=schemas.BookingOut)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and current_user.role == models.RoleEnum.USER:
        raise HTTPException(status_code=403, detail="Not your booking")
    if booking.status in (models.BookingStatusEnum.COMPLETED, models.BookingStatusEnum.CANCELLED):
        raise HTTPException(status_code=400, detail=f"Cannot cancel a {booking.status.value.lower()} booking")

    booking.status = models.BookingStatusEnum.CANCELLED
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{booking_id}/return", response_model=schemas.BookingOut)
def mark_returned(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_roles(models.RoleEnum.ADMIN, models.RoleEnum.MANAGER)),
):
    """Manager/Admin confirms the asset was physically returned, closing out the booking."""
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status not in (models.BookingStatusEnum.APPROVED, models.BookingStatusEnum.OVERDUE):
        raise HTTPException(status_code=400, detail="Booking is not currently checked out")

    booking.status = models.BookingStatusEnum.COMPLETED
    booking.returned_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking
