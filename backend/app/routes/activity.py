from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import ActivityLog, Project, User
from ..schemas import ActivityLogResponse


router = APIRouter(
    prefix="/activity",
    tags=["Activity Log"]
)


# GET PROJECT ACTIVITY
@router.get(
    "/projects/{project_id}",
    response_model=list[ActivityLogResponse]
)
def get_project_activity(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check project exists
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check current user is a project member
    is_member = any(
        member.user_id == current_user.id
        for member in project.members
    )

    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project"
        )

    return (
        db.query(ActivityLog)
        .filter(
            ActivityLog.project_id == project_id
        )
        .order_by(
            ActivityLog.created_at.desc()
        )
        .all()
    )


# GET USER ACTIVITY
@router.get(
    "/users/{user_id}",
    response_model=list[ActivityLogResponse]
)
def get_user_activity(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Users can view their own activity.
    # Admins can view other users' activity.
    if (
        current_user.id != user_id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this activity"
        )

    return (
        db.query(ActivityLog)
        .filter(
            ActivityLog.user_id == user_id
        )
        .order_by(
            ActivityLog.created_at.desc()
        )
        .all()
    )
