from fastapi import FastAPI

app = FastAPI(
    title="Agile Project Management API",
    description="Backend API for a small-team Agile Project Management Tool",
    version="1.0.0",
)


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
