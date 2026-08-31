from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


client = TestClient(app)


def authenticated_headers():
    email = f"test-{uuid4().hex}@example.com"
    password = "test-password"

    registration = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": password,
        },
    )
    assert registration.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200

    return {"Authorization": f"Bearer {login.json()['access_token']}"}


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
        json={"name": "Test Project", "description": "Testing authentication"}
    )
    assert response.status_code == 401


def test_create_story_requires_authentication():
    response = client.post(
        "/projects/8/stories",
        json={"title": "Test Story", "description": "Testing", "status": "BACKLOG", "priority": "HIGH"}
    )
    assert response.status_code == 401


def test_create_task_requires_authentication():
    response = client.post(
        "/stories/2/tasks",
        json={"title": "Test Task", "description": "Testing", "status": "TODO", "priority": "HIGH"}
    )
    assert response.status_code == 401


def test_project_search():
    response = client.get(
        "/projects",
        params={"search": "Activity", "status_filter": "ACTIVE"},
        headers=authenticated_headers(),
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dashboard_requires_authentication():
    response = client.get("/dashboard/summary")
    assert response.status_code == 401


def test_notifications_list():
    response = client.get("/notifications", headers=authenticated_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_notification_requires_authentication():
    response = client.delete("/notifications/999")
    assert response.status_code == 401


def test_process_notification_not_found():
    response = client.post(
        "/notifications/999999/process",
        headers=authenticated_headers(),
    )
    assert response.status_code == 404


def test_get_notification_not_found():
    response = client.get(
        "/notifications/999999",
        headers=authenticated_headers(),
    )
    assert response.status_code == 404
