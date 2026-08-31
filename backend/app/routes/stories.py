from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Project, UserStory
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
    db: Session = Depends(get_db)
):
    # Check whether project exists
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

    update_data = story_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(story, key, value)

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

    db.delete(story)
    db.commit()

    return None
