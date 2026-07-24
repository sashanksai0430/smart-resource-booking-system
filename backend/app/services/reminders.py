import os
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from ..database import SessionLocal
from .. import models

logger = logging.getLogger("reminders")

GRACE_HOURS = float(os.getenv("OVERDUE_GRACE_HOURS", 2))
PENALTY_PER_HOUR = float(os.getenv("PENALTY_PER_HOUR", 50))


def check_overdue_and_reminders():
    """
    Runs periodically:
    1. Flags approved bookings whose end_time has passed as OVERDUE.
    2. Creates/updates a Penalty for bookings overdue beyond the grace period.
    3. Logs upcoming-return reminders for bookings ending within the next hour
       (in a real deployment this would send email/SMS/push notifications).
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # 1 & 2: overdue detection + fines
        approved_or_overdue = db.query(models.Booking).filter(
            models.Booking.status.in_([
                models.BookingStatusEnum.APPROVED,
                models.BookingStatusEnum.OVERDUE,
            ])
        ).all()

        for booking in approved_or_overdue:
            if booking.end_time < now:
                if booking.status != models.BookingStatusEnum.OVERDUE:
                    booking.status = models.BookingStatusEnum.OVERDUE
                    logger.info(f"Booking {booking.id} marked OVERDUE")

                hours_late = (now - booking.end_time).total_seconds() / 3600
                if hours_late > GRACE_HOURS:
                    existing_penalty = db.query(models.Penalty).filter(
                        models.Penalty.booking_id == booking.id
                    ).first()
                    fine_amount = round((hours_late - GRACE_HOURS) * PENALTY_PER_HOUR, 2)
                    if existing_penalty:
                        existing_penalty.amount = fine_amount
                    else:
                        db.add(models.Penalty(
                            booking_id=booking.id,
                            user_id=booking.user_id,
                            amount=fine_amount,
                            reason="Late return beyond grace period",
                        ))
        db.commit()

        # 3: upcoming return reminders (next 60 minutes)
        soon = now + timedelta(hours=1)
        upcoming = db.query(models.Booking).filter(
            models.Booking.status == models.BookingStatusEnum.APPROVED,
            models.Booking.end_time >= now,
            models.Booking.end_time <= soon,
        ).all()
        for booking in upcoming:
            logger.info(
                f"[REMINDER] Booking {booking.id} (user {booking.user_id}) "
                f"due back at {booking.end_time.isoformat()}"
            )
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_overdue_and_reminders, "interval", minutes=15, id="overdue_check")
    scheduler.start()
    return scheduler
