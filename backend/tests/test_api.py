from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.database import SessionLocal
from app.models import Notification
from app.routes.notifications import MAX_NOTIFICATION_ATTEMPTS, process_notification


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


def create_project_hierarchy(headers, assigned_to=None, due_date=None):
    project = client.post("/projects", json={"name": f"Project {uuid4().hex}"}, headers=headers)
    assert project.status_code == 201
    story = client.post(
        f"/projects/{project.json()['id']}/stories",
        json={"title": "A story", "status": "BACKLOG", "priority": "MEDIUM"},
        headers=headers,
    )
    assert story.status_code == 201
    task_data = {"title": "A task", "status": "TODO", "priority": "HIGH", "assigned_to": assigned_to, "due_date": due_date}
    task = client.post(f"/stories/{story.json()['id']}/tasks", json=task_data, headers=headers)
    assert task.status_code == 201
    return project.json(), story.json(), task.json()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_registration_requires_a_valid_password():
    response = client.post(
        "/auth/register",
        json={"name": "No Password", "email": f"missing-{uuid4().hex}@example.com"},
    )
    assert response.status_code == 422


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


def test_project_story_task_crud_and_due_date():
    headers = authenticated_headers()
    project, story, task = create_project_hierarchy(headers, due_date="2030-01-15")
    assert task["due_date"] == "2030-01-15"
    update = client.put(f"/tasks/{task['id']}", json={"status": "DONE", "due_date": "2030-02-01"}, headers=headers)
    assert update.status_code == 200
    assert update.json()["status"] == "DONE"
    assert update.json()["due_date"] == "2030-02-01"
    assert client.put(f"/stories/{story['id']}", json={"priority": "LOW"}, headers=headers).status_code == 200
    assert client.delete(f"/tasks/{task['id']}", headers=headers).status_code == 204
    assert client.delete(f"/stories/{story['id']}", headers=headers).status_code == 204
    assert client.delete(f"/projects/{project['id']}", headers=headers).status_code == 204


def test_membership_and_dashboard_are_isolated():
    owner_headers = authenticated_headers()
    outsider_headers = authenticated_headers()
    project, _, _ = create_project_hierarchy(owner_headers)
    assert client.get(f"/projects/{project['id']}", headers=outsider_headers).status_code == 403
    assert client.get(f"/projects/{project['id']}/stories", headers=outsider_headers).status_code == 403
    summary = client.get("/dashboard/summary", headers=outsider_headers)
    assert summary.status_code == 200
    assert summary.json()["total_projects"] == 0


def test_notification_is_only_visible_to_assignee():
    owner_headers = authenticated_headers()
    assignee_headers = authenticated_headers()
    assignee = client.get("/auth/me", headers=assignee_headers).json()
    project, _, task = create_project_hierarchy(owner_headers)
    assert client.post(
        f"/users/{assignee['id']}/projects/{project['id']}", headers=owner_headers
    ).status_code == 201
    assert client.put(
        f"/tasks/{task['id']}", json={"assigned_to": assignee["id"]}, headers=owner_headers
    ).status_code == 200
    notifications = client.get("/notifications", headers=assignee_headers)
    assert notifications.status_code == 200
    notification = next(item for item in notifications.json() if item["task_id"] == task["id"])
    assert notification["recipient_id"] == assignee["id"]
    assert client.get(f"/notifications/{notification['id']}", headers=owner_headers).status_code == 404
    assert client.delete(f"/notifications/{notification['id']}", headers=owner_headers).status_code == 404
    assert client.get(f"/projects/{project['id']}", headers=assignee_headers).status_code == 200


def test_status_and_priority_validation_and_progress_not_found():
    headers = authenticated_headers()
    invalid_project = client.post("/projects", json={"name": "Invalid", "status": "INVALID"}, headers=headers)
    assert invalid_project.status_code == 422
    project = client.post("/projects", json={"name": "Valid"}, headers=headers).json()
    invalid_story = client.post(
        f"/projects/{project['id']}/stories",
        json={"title": "Invalid", "priority": "URGENT"}, headers=headers,
    )
    assert invalid_story.status_code == 422
    assert client.get("/dashboard/projects/99999999/progress", headers=headers).status_code == 404


def test_notification_failure_retries_to_limit():
    owner_headers = authenticated_headers()
    project, _, task = create_project_hierarchy(owner_headers)
    recipient_headers = authenticated_headers()
    recipient_id = client.get("/auth/me", headers=recipient_headers).json()["id"]
    db = SessionLocal()
    try:
        notification = Notification(task_id=task["id"], recipient_id=recipient_id, message="Invalid recipient membership")
        db.add(notification)
        db.commit()
        db.refresh(notification)
        for _ in range(MAX_NOTIFICATION_ATTEMPTS):
            process_notification(notification.id)
        db.refresh(notification)
        assert notification.status == "FAILED"
        assert notification.retry_count == MAX_NOTIFICATION_ATTEMPTS
    finally:
        db.close()
