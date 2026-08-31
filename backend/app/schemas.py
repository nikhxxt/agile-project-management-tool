from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# -------------------------
# User
# -------------------------

class UserCreate(BaseModel):
    name: str
    email: str
    password: Optional[str] = None
    role: str = "member"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Project
# -------------------------

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# User Story
# -------------------------

class StoryCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "BACKLOG"
    priority: str = "MEDIUM"


class StoryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class StoryResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Task
# -------------------------

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "TODO"
    priority: str = "MEDIUM"
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
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

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Notification
# -------------------------

class NotificationResponse(BaseModel):
    id: int
    task_id: int
    message: str
    status: str
    retry_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)
