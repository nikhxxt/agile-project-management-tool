from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Agile Project Management API is running"


def test_create_project_requires_authentication():
    response = client.post(
        "/projects",
        json={
            "name": "Test Project",
            "description": "Testing authentication"
        }
    )

    assert response.status_code == 401


def test_create_story_requires_authentication():
    response = client.post(
        "/projects/8/stories",
        json={
            "title": "Test Story",
            "description": "Testing authentication",
            "status": "BACKLOG",
            "priority": "HIGH"
        }
    )

    assert response.status_code == 401


def test_create_task_requires_authentication():
    response = client.post(
        "/stories/2/tasks",
        json={
            "title": "Test Task",
            "description": "Testing authentication",
            "status": "TODO",
            "priority": "HIGH"
        }
    )

    assert response.status_code == 401


def test_project_search():
    response = client.get(
        "/projects",
        params={
            "search": "Activity",
            "status_filter": "ACTIVE"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dashboard_requires_authentication():
    response = client.get("/dashboard/summary")

    assert response.status_code == 401


def test_notifications_endpoint():
    response = client.get("/notifications")

    assert response.status_code in [200, 401]