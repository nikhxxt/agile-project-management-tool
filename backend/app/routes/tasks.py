from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
    db: Session = Depends(get_db)
):
    # Check whether the user story exists
    story = db.query(UserStory).filter(
        UserStory.id == story_id
    ).first()

    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User story not found"
        )

    # Validate assignee if provided
    if task.assigned_to is not None:
        user = db.query(User).filter(
            User.id == task.assigned_to
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

        # Get the project through the story
        project_id = story.project_id

        membership = db.query(ProjectMember).filter(
            ProjectMember.user_id == task.assigned_to,
            ProjectMember.project_id == project_id
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

    # If changing the assignee, validate the new user
    if task_data.assigned_to is not None:

        user = db.query(User).filter(
            User.id == task_data.assigned_to
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

        # Find the project through:
        # Task → User Story → Project
        story = db.query(UserStory).filter(
            UserStory.id == task.user_story_id
        ).first()

        membership = db.query(ProjectMember).filter(
            ProjectMember.user_id == task_data.assigned_to,
            ProjectMember.project_id == story.project_id
        ).first()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a member of this project"
            )

    update_data = task_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(task, key, value)

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

    db.delete(task)
    db.commit()

    return None
