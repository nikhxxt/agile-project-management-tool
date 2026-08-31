from sqlalchemy.orm import Session

from .models import ActivityLog


def log_activity(
    db: Session,
    user_id: int | None,
    project_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    details: str | None = None,
):
    activity = ActivityLog(
        user_id=user_id,
        project_id=project_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(activity)
    db.flush()
    return activity
