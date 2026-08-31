from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..activity_logger import log_activity
from ..auth import get_current_user
from ..database import get_db
from ..models import UserStory, Task, User, ProjectMember
from ..schemas import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(
    tags=["Tasks"]
)


# CREATE TASK
@router.post(
    "/stories/{story_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    story_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    story = db.query(UserStory).filter(
        UserStory.id == story_id
    ).first()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User story not found"
        )

    if task.assigned_to is not None:
        user = db.query(User).filter(
            User.id == task.assigned_to
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

        membership = db.query(ProjectMember).filter(
            ProjectMember.user_id == task.assigned_to,
            ProjectMember.project_id == story.project_id
        ).first()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a member of this project"
            )

    new_task = Task(
        user_story_id=story_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        assigned_to=task.assigned_to,
        due_date=task.due_date
    )

    db.add(new_task)
    db.flush()

    log_activity(
        db,
        user_id=current_user.id,
        project_id=story.project_id,
        action="CREATE",
        entity_type="TASK",
        entity_id=new_task.id,
        details=f"Created task '{new_task.title}'"
    )

    if new_task.assigned_to is not None:
        log_activity(
            db,
            user_id=current_user.id,
            project_id=story.project_id,
            action="ASSIGN",
            entity_type="TASK",
            entity_id=new_task.id,
            details=(
                f"Assigned task '{new_task.title}' "
                f"to user {new_task.assigned_to}"
            )
        )

    db.commit()
    db.refresh(new_task)

    return new_task


# GET ALL TASKS FOR A USER STORY
@router.get(
    "/stories/{story_id}/tasks",
    response_model=list[TaskResponse]
)
def get_story_tasks(
    story_id: int,
    db: Session = Depends(get_db)
):
    story = db.query(UserStory).filter(
        UserStory.id == story_id
    ).first()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User story not found"
        )

    return db.query(Task).filter(
        Task.user_story_id == story_id
    ).order_by(Task.created_at.desc()).all()


# GET SINGLE TASK
@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


# UPDATE TASK
@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    story = db.query(UserStory).filter(
        UserStory.id == task.user_story_id
    ).first()

    old_status = task.status
    old_assignee = task.assigned_to

    update_data = task_data.model_dump(
        exclude_unset=True
    )

    # Validate new assignee only when assigned_to is supplied
    if "assigned_to" in update_data:
        new_assignee = update_data["assigned_to"]

        if new_assignee is not None:
            user = db.query(User).filter(
                User.id == new_assignee
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assigned user not found"
                )

            membership = db.query(ProjectMember).filter(
                ProjectMember.user_id == new_assignee,
                ProjectMember.project_id == story.project_id
            ).first()

            if not membership:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is not a member of this project"
                )

    changes = []

    for key, value in update_data.items():
        old_value = getattr(task, key)

        if old_value != value:
            changes.append(
                f"{key}: '{old_value}' -> '{value}'"
            )

        setattr(task, key, value)

    # General UPDATE activity
    if changes:
        log_activity(
            db,
            user_id=current_user.id,
            project_id=story.project_id,
            action="UPDATE",
            entity_type="TASK",
            entity_id=task.id,
            details=(
                f"Updated task '{task.title}': "
                + ", ".join(changes)
            )
        )

    # Assignment activity
    if (
        "assigned_to" in update_data
        and old_assignee != task.assigned_to
    ):
        if task.assigned_to is None:
            assignment_details = (
                f"Unassigned task '{task.title}'"
            )
        else:
            assignment_details = (
                f"Assigned task '{task.title}' "
                f"to user {task.assigned_to}"
            )

        log_activity(
            db,
            user_id=current_user.id,
            project_id=story.project_id,
            action="ASSIGN",
            entity_type="TASK",
            entity_id=task.id,
            details=assignment_details
        )

    # Status change activity
    if (
        "status" in update_data
        and old_status != task.status
    ):
        log_activity(
            db,
            user_id=current_user.id,
            project_id=story.project_id,
            action="STATUS_CHANGE",
            entity_type="TASK",
            entity_id=task.id,
            details=(
                f"Task '{task.title}' status changed "
                f"from '{old_status}' to '{task.status}'"
            )
        )

    db.commit()
    db.refresh(task)

    return task


# DELETE TASK
@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    story = db.query(UserStory).filter(
        UserStory.id == task.user_story_id
    ).first()

    project_id = story.project_id
    task_id_value = task.id
    task_title = task.title

    log_activity(
        db,
        user_id=current_user.id,
        project_id=project_id,
        action="DELETE",
        entity_type="TASK",
        entity_id=task_id_value,
        details=f"Deleted task '{task_title}'"
    )

    db.delete(task)
    db.commit()

    return None
