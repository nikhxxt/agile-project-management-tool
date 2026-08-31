from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..activity_logger import log_activity
from ..auth import get_current_user
from ..database import get_db
from ..models import Project, ProjectMember, User
from ..permissions import require_project_membership
from ..schemas import ProjectCreate, ProjectUpdate, ProjectResponse


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# CREATE PROJECT
@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_project = Project(
        name=project.name,
        description=project.description
    )

    db.add(new_project)
    db.flush()

    membership = ProjectMember(
        user_id=current_user.id,
        project_id=new_project.id
    )
    db.add(membership)

    log_activity(
        db,
        user_id=current_user.id,
        project_id=new_project.id,
        action="CREATE",
        entity_type="PROJECT",
        entity_id=new_project.id,
        details=f"Created project '{new_project.name}'"
    )

    db.commit()
    db.refresh(new_project)

    return new_project


# GET ALL PROJECTS
@router.get(
    "",
    response_model=list[ProjectResponse]
)
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).order_by(
        Project.created_at.desc()
    ).all()


# GET SINGLE PROJECT
@router.get(
    "/{project_id}",
    response_model=ProjectResponse
)
def get_project(
    project_id: int,
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

    require_project_membership(db, project_id, current_user)

    return project


# UPDATE PROJECT
@router.put(
    "/{project_id}",
    response_model=ProjectResponse
)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
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

    require_project_membership(db, project_id, current_user)

    update_data = project_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    log_activity(
        db=db,
        user_id=current_user.id,
        project_id=project.id,
        action="UPDATE",
        entity_type="PROJECT",
        entity_id=project.id,
        details=f"Updated project '{project.name}'"
    )
    db.commit()

    return project


# DELETE PROJECT
@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_project(
    project_id: int,
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

    require_project_membership(db, project_id, current_user)

    project_name = project.name
    project_id_value = project.id

    log_activity(
        db=db,
        user_id=current_user.id,
        project_id=project_id_value,
        action="DELETE",
        entity_type="PROJECT",
        entity_id=project_id_value,
        details=f"Deleted project '{project_name}'"
    )

    db.delete(project)
    db.commit()

    return None
