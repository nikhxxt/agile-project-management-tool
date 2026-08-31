from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import SessionLocal, get_db
from ..models import Notification, Task, User
from ..schemas import NotificationResponse

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


def process_notification(notification_id: int, max_attempts: int = 3):
    db = SessionLocal()

    try:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

        if not notification:
            return None

        if notification.status in {"SENT", "FAILED"}:
            return notification

        for attempt in range(1, max_attempts + 1):
            try:
                if notification.task is None:
                    raise ValueError("Task not found")

                notification.status = "SENT"
                notification.retry_count = 0
                db.commit()
                return notification
            except Exception:
                notification.retry_count += 1

                if notification.retry_count >= max_attempts:
                    notification.status = "FAILED"
                    db.commit()
                    return notification

                db.commit()

        notification.status = "FAILED"
        db.commit()
        return notification
    finally:
        db.close()


@router.get(
    "",
    response_model=list[NotificationResponse]
)
def get_notifications(
    db: Session = Depends(get_db)
):
    return db.query(Notification).order_by(Notification.created_at.desc()).all()


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return notification


@router.get(
    "/tasks/{task_id}",
    response_model=list[NotificationResponse]
)
def get_task_notifications(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return (
        db.query(Notification)
        .filter(Notification.task_id == task_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.post(
    "/{notification_id}/process",
    response_model=NotificationResponse
)
def process_notification_route(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    processed = process_notification(notification_id)

    if processed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db.refresh(notification)
    return notification
