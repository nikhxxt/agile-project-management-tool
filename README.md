# AgileFlow Platform

AgileFlow is a full-stack Agile Project Management Tool for a small team. It uses React/Vite, FastAPI, SQLAlchemy, and SQLite to manage **Project → User Story → Task**.

## Table of Contents

- [AgileFlow Platform](#agileflow-platform)
- [Features](#features)
- [Tech Stack](#tech-stack)
  - [Frontend](#frontend)
  - [Backend](#backend)
  - [Database](#database)
  - [Testing](#testing)
- [Work-item States](#work-item-states)
- [Async Notification Workflow](#async-notification-workflow)
- [Architecture and API Documentation](#architecture-and-api-documentation)
- [Local Setup](#local-setup)
- [Testing](#testing-1)
- [Repository Structure](#repository-structure)
- [Security Considerations](#security-considerations)
- [Design Decisions and Tradeoffs](#design-decisions-and-tradeoffs)
- [AI Usage](#ai-usage)
- [With More Time](#with-more-time)
- [Demo](#demo)

## Features

- Registration, login, expiring JWT authentication, and protected frontend routes.
- Project CRUD, project search/status filtering, and membership-based authorization.
- Story and task CRUD, validated status/priority values, task assignees, and due dates.
- Project member add/remove controls; a project retains at least one member.
- Membership-scoped dashboard and project progress endpoint.
- Activity history for project, story, and task changes.
- Recipient-specific in-app assignment notifications processed with FastAPI background tasks.

 ## Tech Stack

### Frontend
- React
- Vite
- React Router
- Axios
- CSS

### Backend
- Python
- FastAPI
- SQLAlchemy
- JWT authentication
- bcrypt password hashing
- Uvicorn

### Database
- SQLite

### Testing
- Pytest

## Work-item states

| Item | Status values | Priority values |
| --- | --- | --- |
| Project | `ACTIVE`, `COMPLETED`, `ARCHIVED` | — |
| User Story | `BACKLOG`, `IN_PROGRESS`, `DONE` | `LOW`, `MEDIUM`, `HIGH` |
| Task | `TODO`, `IN_PROGRESS`, `DONE` | `LOW`, `MEDIUM`, `HIGH` |

Invalid values are rejected by the API.

## Async notification workflow

When a task is assigned, the server persists an in-app notification for the assigned project member and queues one FastAPI background attempt. Delivery validates the task, recipient, story, and project membership. `SENT` means the notification is available in that recipient's authenticated inbox; AgileFlow does not send email or push notifications.

Failure sets `FAILED`, increments `retry_count`, records `last_attempt_at`, and calculates exponential `next_retry_at`. The recipient can retry until the three-attempt limit. Notification APIs are recipient- and project-membership-scoped.

## Architecture and API documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for the architecture, schema, relationships, and security model. FastAPI interactive documentation is at `http://127.0.0.1:8000/docs`.

## Local setup

Prerequisites: Python 3.11+, Node.js/npm, and Git.

```powershell
Copy-Item .env.example .env
# Replace JWT_SECRET_KEY with a long random value.

cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "."
python -m uvicorn app.main:app
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend is at `http://localhost:5173`; the backend is at `http://127.0.0.1:8000`. Vite forwards `/api` to the backend in development. Existing local SQLite databases receive the additive notification columns at startup; new databases are created automatically.

## Testing

```powershell
cd backend
$env:PYTHONPATH = "."
$env:JWT_SECRET_KEY = "test-only-secret"
pytest -q

cd ..\frontend
npm run lint
npm run build
```

Tests cover authentication, hierarchy CRUD, membership/dashboard isolation, notification authorization and failure retries, due dates, validation, and project-progress 404 behavior.

## Repository structure

```text
backend/
  app/routes/        FastAPI routes
  app/auth.py        JWT/password helpers
  app/database.py    SQLAlchemy setup and additive migration
  app/models.py      SQLAlchemy models
  app/schemas.py     Pydantic schemas
  tests/test_api.py
frontend/
  src/pages/         Application pages
  src/services/api.js
  src/App.jsx
README.md
ARCHITECTURE.md
```

## Security considerations

- Passwords are bcrypt-hashed and API-created accounts require a password.
- JWTs use `JWT_SECRET_KEY`, expire after 60 minutes, and protect application APIs.
- Work-item, membership, activity, and progress requests require project membership.
- Dashboard metrics are limited to accessible projects; notifications are limited to their recipient and current project members.
- Task assignees must belong to the project.
- Deploy over HTTPS and use managed secret storage in production.

## Design decisions and tradeoffs

SQLite suits a small team and simple local setup. Background tasks keep in-app notification validation off the task request path, but are process-local; production should use a durable queue and scheduler. Membership is deliberately flat: any current member can manage a project's work and membership instead of using project roles.

## AI Usage

AI tooling was used as a development aid for implementation, review, documentation, and testing. The resulting behavior and changes were reviewed and verified by the developer.

## With more time

- Durable queue and scheduled notification retries.
- Project roles and invitation emails.
- Pagination, CI/CD, PostgreSQL, and broader frontend integration/accessibility tests.

## Demo

[There is currently no hosted demo or walkthrough video.](https://drive.google.com/file/d/1LvNN5ia85LWi54lFeEtEOxjGuH8BNfaQ/view)
