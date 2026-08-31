from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, apply_schema_migrations, engine
from . import models
from .routes import (
    projects,
    stories,
    tasks,
    users,
    auth,
    activity,
    dashboard,
    notifications
)


Base.metadata.create_all(bind=engine)
apply_schema_migrations()


app = FastAPI(
    title="Agile Project Management API",
    description="Backend API for a small-team Agile Project Management Tool",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(projects.router)
app.include_router(stories.router)
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(activity.router)
app.include_router(dashboard.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    return {
        "message": "Agile Project Management API is running",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
