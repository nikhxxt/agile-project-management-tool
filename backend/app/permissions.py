from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models import ProjectMember, User


def require_project_membership(
    db: Session,
    project_id: int,
    current_user: User,
) -> None:
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
    ).first()

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )
