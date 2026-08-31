from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# -------------------------
# User
# -------------------------

class UserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )
    email: str = Field(
        min_length=5,
        max_length=150
    )
    password: str = Field(
        min_length=6,
        max_length=100
    )
    role: str = "member"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# -------------------------
# Project
# -------------------------

class ProjectCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )
    description: Optional[str] = None
    status: Literal["ACTIVE", "COMPLETED", "ARCHIVED"] = "ACTIVE"


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=150
    )
    description: Optional[str] = None
    status: Optional[Literal["ACTIVE", "COMPLETED", "ARCHIVED"]] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# -------------------------
# User Story
# -------------------------

class StoryCreate(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=200
    )
    description: Optional[str] = None
    status: Literal["BACKLOG", "IN_PROGRESS", "DONE"] = "BACKLOG"
    priority: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"


class StoryUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200
    )
    description: Optional[str] = None
    status: Optional[Literal["BACKLOG", "IN_PROGRESS", "DONE"]] = None
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = None


class StoryResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# -------------------------
# Task
# -------------------------

class TaskCreate(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=200
    )
    description: Optional[str] = None
    status: Literal["TODO", "IN_PROGRESS", "DONE"] = "TODO"
    priority: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200
    )
    description: Optional[str] = None
    status: Optional[Literal["TODO", "IN_PROGRESS", "DONE"]] = None
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = None
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None


class TaskResponse(BaseModel):
    id: int
    user_story_id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    assigned_to: Optional[int]
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# -------------------------
# Notification
# -------------------------

class NotificationResponse(BaseModel):
    id: int
    task_id: int
    recipient_id: int
    message: str
    status: str
    retry_count: int
    last_attempt_at: Optional[datetime]
    next_retry_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# -------------------------
# Activity Log
# -------------------------

class ActivityLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    project_id: Optional[int]
    action: str
    entity_type: str
    entity_id: Optional[int]
    details: Optional[str]
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
