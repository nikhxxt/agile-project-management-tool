from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import SessionLocal, get_db
from ..models import Notification, ProjectMember, Task, User, UserStory
from ..permissions import require_project_membership
from ..schemas import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])
MAX_NOTIFICATION_ATTEMPTS = 3


def _notification_for_recipient(db: Session, notification_id: int, current_user: User) -> Notification:
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == current_user.id,
    ).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    task = db.query(Task).filter(Task.id == notification.task_id).first()
    story = db.query(UserStory).filter(UserStory.id == task.user_story_id).first() if task else None
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    require_project_membership(db, story.project_id, current_user)
    return notification


def _deliver_in_app_notification(db: Session, notification: Notification) -> None:
    """Validate delivery to the recipient's authenticated in-app inbox."""
    task = db.query(Task).filter(Task.id == notification.task_id).first()
    recipient = db.query(User).filter(User.id == notification.recipient_id).first()
    if not task or not recipient:
        raise ValueError("Notification task or recipient no longer exists")
    story = db.query(UserStory).filter(UserStory.id == task.user_story_id).first()
    if not story:
        raise ValueError("Notification task has no user story")
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == story.project_id,
        ProjectMember.user_id == recipient.id,
    ).first()
    if not membership:
        raise ValueError("Notification recipient is not a project member")


def process_notification(notification_id: int) -> None:
    """Perform one persistent delivery attempt from a FastAPI background task."""
    db = SessionLocal()
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification or notification.status == "SENT":
            return
        if notification.retry_count >= MAX_NOTIFICATION_ATTEMPTS:
            notification.status = "FAILED"
            db.commit()
            return

        now = datetime.utcnow()
        notification.status = "PROCESSING"
        notification.last_attempt_at = now
        try:
            _deliver_in_app_notification(db, notification)
            notification.status = "SENT"
            notification.next_retry_at = None
        except Exception:
            notification.retry_count += 1
            notification.status = "FAILED"
            notification.next_retry_at = now + timedelta(seconds=2 ** notification.retry_count)
        db.commit()
    finally:
        db.close()


def create_task_notification(task_id: int, recipient_id: int, message: str) -> None:
    db = SessionLocal()
    try:
        notification = Notification(
            task_id=task_id,
            recipient_id=recipient_id,
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
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Notification).join(Task).join(UserStory).join(
        ProjectMember, ProjectMember.project_id == UserStory.project_id
    ).filter(
        Notification.recipient_id == current_user.id,
        ProjectMember.user_id == current_user.id,
    ).order_by(Notification.created_at.desc()).all()


@router.get("/tasks/{task_id}", response_model=list[NotificationResponse])
def get_task_notifications(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    story = db.query(UserStory).filter(UserStory.id == task.user_story_id).first()
    require_project_membership(db, story.project_id, current_user)
    return db.query(Notification).filter(
        Notification.task_id == task_id,
        Notification.recipient_id == current_user.id,
    ).order_by(Notification.created_at.desc()).all()


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _notification_for_recipient(db, notification_id, current_user)


@router.post("/{notification_id}/process", response_model=NotificationResponse)
def process_notification_route(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = _notification_for_recipient(db, notification_id, current_user)
    if notification.status == "SENT":
        return notification
    if notification.retry_count >= MAX_NOTIFICATION_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Notification retry limit reached")
    process_notification(notification_id)
    db.expire_all()
    return _notification_for_recipient(db, notification_id, current_user)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = _notification_for_recipient(db, notification_id, current_user)
    db.delete(notification)
    db.commit()
    return None
