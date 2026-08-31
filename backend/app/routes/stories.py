from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..activity_logger import log_activity
from ..auth import get_current_user
from ..database import get_db
from ..models import Project, UserStory, User
from ..schemas import StoryCreate, StoryUpdate, StoryResponse

router = APIRouter(
    tags=["User Stories"]
)


# CREATE USER STORY
@router.post(
    "/projects/{project_id}/stories",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_story(
    project_id: int,
    story: StoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    new_story = UserStory(
        project_id=project_id,
        title=story.title,
        description=story.description,
        status=story.status,
        priority=story.priority
    )

    db.add(new_story)
    db.flush()

    log_activity(
        db,
        user_id=current_user.id,
        project_id=project_id,
        action="CREATE",
        entity_type="STORY",
        entity_id=new_story.id,
        details=f"Created story '{new_story.title}'"
    )

    db.commit()
    db.refresh(new_story)

    return new_story


# GET ALL STORIES FOR A PROJECT
@router.get(
    "/projects/{project_id}/stories",
    response_model=list[StoryResponse]
)
def get_project_stories(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return db.query(UserStory).filter(
        UserStory.project_id == project_id
    ).order_by(UserStory.created_at.desc()).all()


# GET SINGLE STORY
@router.get(
    "/stories/{story_id}",
    response_model=StoryResponse
)
def get_story(
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

    return story


# UPDATE STORY
@router.put(
    "/stories/{story_id}",
    response_model=StoryResponse
)
def update_story(
    story_id: int,
    story_data: StoryUpdate,
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

    update_data = story_data.model_dump(
        exclude_unset=True
    )

    changes = []

    for key, value in update_data.items():
        old_value = getattr(story, key)

        if old_value != value:
            changes.append(
                f"{key}: '{old_value}' -> '{value}'"
            )

        setattr(story, key, value)

    if changes:
        log_activity(
            db,
            user_id=current_user.id,
            project_id=story.project_id,
            action="UPDATE",
            entity_type="STORY",
            entity_id=story.id,
            details=(
                f"Updated story '{story.title}': "
                + ", ".join(changes)
            )
        )

    db.commit()
    db.refresh(story)

    return story


# DELETE STORY
@router.delete(
    "/stories/{story_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_story(
    story_id: int,
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

    project_id = story.project_id
    story_id_value = story.id
    story_title = story.title

    log_activity(
        db,
        user_id=current_user.id,
        project_id=project_id,
        action="DELETE",
        entity_type="STORY",
        entity_id=story_id_value,
        details=f"Deleted story '{story_title}'"
    )

    db.delete(story)
    db.commit()

    return None
