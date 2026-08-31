from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user, hash_password
from ..database import get_db
from ..models import User, Project, ProjectMember
from ..permissions import require_project_membership
from ..schemas import UserCreate, UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# CREATE USER
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users"
        )

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# GET ALL USERS
@router.get(
    "",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all users"
        )

    return db.query(User).order_by(
        User.name
    ).all()


# GET PROJECT MEMBERS
@router.get(
    "/projects/{project_id}/members",
    response_model=list[UserResponse]
)
def get_project_members(
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

    return (
        db.query(User)
        .join(ProjectMember)
        .filter(ProjectMember.project_id == project_id)
        .all()
    )


# GET SINGLE USER
@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
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

    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this user"
        )

    return user


# ADD USER TO PROJECT
@router.post(
    "/{user_id}/projects/{project_id}",
    status_code=status.HTTP_201_CREATED
)
def add_user_to_project(
    user_id: int,
    project_id: int,
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

    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    require_project_membership(db, project_id, current_user)

    existing_membership = db.query(ProjectMember).filter(
        ProjectMember.user_id == user_id,
        ProjectMember.project_id == project_id
    ).first()

    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this project"
        )

    membership = ProjectMember(
        user_id=user_id,
        project_id=project_id
    )

    db.add(membership)
    db.commit()

    return {
        "message": "User added to project successfully",
        "user_id": user_id,
        "project_id": project_id
    }


@router.delete(
    "/{user_id}/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_user_from_project(
    user_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    require_project_membership(db, project_id, current_user)

    membership = db.query(ProjectMember).filter(
        ProjectMember.user_id == user_id,
        ProjectMember.project_id == project_id,
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project membership not found")

    if db.query(ProjectMember).filter(ProjectMember.project_id == project_id).count() <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A project must retain at least one member",
        )
    db.delete(membership)
    db.commit()
    return None

