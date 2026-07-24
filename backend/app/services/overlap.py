from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .. import models


def has_overlap(db: Session, resource_id: int, start_time: datetime, end_time: datetime,
                 exclude_booking_id: int | None = None) -> bool:
    """
    Returns True if the requested [start_time, end_time) window overlaps with any
    existing PENDING or APPROVED booking for the same resource.
    Two ranges overlap if: existing.start < new.end AND existing.end > new.start
    """
    query = db.query(models.Booking).filter(
        models.Booking.resource_id == resource_id,
        models.Booking.status.in_([
            models.BookingStatusEnum.PENDING,
            models.BookingStatusEnum.APPROVED,
            models.BookingStatusEnum.OVERDUE,
        ]),
        models.Booking.start_time < end_time,
        models.Booking.end_time > start_time,
    )
    if exclude_booking_id is not None:
        query = query.filter(models.Booking.id != exclude_booking_id)

    return db.query(query.exists()).scalar()
