from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from ..auth import get_current_user
from ..database import get_db
from ..models import Project, ProjectMember, UserStory, Task, User
from ..permissions import require_project_membership


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    accessible_project_ids = select(ProjectMember.project_id).where(
        ProjectMember.user_id == current_user.id
    )
    total_projects = db.query(Project).filter(Project.id.in_(accessible_project_ids)).count()
    total_stories = db.query(UserStory).filter(UserStory.project_id.in_(accessible_project_ids)).count()
    task_query = db.query(Task).join(UserStory).filter(
        UserStory.project_id.in_(accessible_project_ids)
    )
    total_tasks = task_query.count()

    completed_tasks = task_query.filter(Task.status == "DONE").count()

    completion_percentage = (
        round((completed_tasks / total_tasks) * 100, 2)
        if total_tasks > 0
        else 0
    )

    status_counts = dict(
        task_query.with_entities(
            Task.status,
            func.count(Task.id)
        )
        .group_by(Task.status)
        .all()
    )

    priority_counts = dict(
        task_query.with_entities(
            Task.priority,
            func.count(Task.id)
        )
        .group_by(Task.priority)
        .all()
    )

    return {
        "total_projects": total_projects,
        "total_stories": total_stories,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_percentage": completion_percentage,
        "tasks_by_status": status_counts,
        "tasks_by_priority": priority_counts
    }


@router.get("/projects/{project_id}/progress")
def get_project_progress(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    require_project_membership(db, project_id, current_user)

    total_stories = db.query(UserStory).filter(
        UserStory.project_id == project_id
    ).count()

    total_tasks = (
        db.query(Task)
        .join(UserStory)
        .filter(UserStory.project_id == project_id)
        .count()
    )

    completed_tasks = (
        db.query(Task)
        .join(UserStory)
        .filter(
            UserStory.project_id == project_id,
            Task.status == "DONE"
        )
        .count()
    )

    progress_percentage = (
        round((completed_tasks / total_tasks) * 100, 2)
        if total_tasks > 0
        else 0
    )

    return {
        "project_id": project_id,
        "project_name": project.name,
        "total_stories": total_stories,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "progress_percentage": progress_percentage
    }
