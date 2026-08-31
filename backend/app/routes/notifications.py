from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
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
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if not notification or notification.status in {"SENT", "FAILED"}:
            return

        for attempt in range(1, max_attempts + 1):
            try:
                if notification.task is None:
                    raise ValueError("Task not found")
                notification.status = "SENT"
                notification.retry_count = attempt - 1
                db.commit()
                return
            except Exception:
                notification.retry_count = attempt
                if attempt >= max_attempts:
                    notification.status = "FAILED"
                db.commit()
    finally:
        db.close()


def create_task_notification(task_id: int, message: str):
    db = SessionLocal()
    try:
        notification = Notification(
            task_id=task_id,
            message=message,
            status="PENDING",
            retry_count=0,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        process_notification(notification.id)
    finally:
        db.close()


@router.get("", response_model=list[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Notification)
        .order_by(Notification.created_at.desc())
        .all()
    )


# NOTE: /tasks/{task_id} must be registered BEFORE /{notification_id}
# to avoid FastAPI matching "tasks" as an integer notification_id.
@router.get("/tasks/{task_id}", response_model=list[NotificationResponse])
def get_task_notifications(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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


@router.post("/{notification_id}/process", response_model=NotificationResponse)
def process_notification_route(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    process_notification(notification_id)
    db.refresh(notification)
    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    db.delete(notification)
    db.commit()
    return None
