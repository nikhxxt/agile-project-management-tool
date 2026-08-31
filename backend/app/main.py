from fastapi import FastAPI

from .database import Base, engine
from . import models
from .routes import projects, stories

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agile Project Management API",
    description="Backend API for a small-team Agile Project Management Tool",
    version="1.0.0",
)

app.include_router(projects.router)
app.include_router(stories.router)


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
