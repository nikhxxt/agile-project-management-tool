# AgileFlow Architecture and Database Schema

## System architecture

```text
React + Vite SPA
       │ HTTPS/REST (Axios)
       ▼
FastAPI
  ├─ JWT authentication and membership authorization
  ├─ Resource routes and Pydantic validation
  └─ FastAPI background notification processing
       ▼
SQLAlchemy
       ▼
SQLite
````

The frontend uses a Vite `/api` development proxy. The backend owns business rules, persistence, activity logging, and authorization. `Base.metadata.create_all()` initializes a new SQLite database; a small additive startup migration supplies current notification columns to older local databases.

## Work hierarchy

```text
Project 1 ─── * UserStory 1 ─── * Task
```

Projects have members through `ProjectMember`. A task can optionally be assigned to one user, but the API verifies that the assignee belongs to the task's project.

```text
User 1 ─── * ProjectMember * ─── 1 Project
User 1 ─── * Task                 (optional assignment)
Task 1 ─── * Notification
User 1 ─── * Notification         (recipient)
Project 1 ─── * ActivityLog
```

## Authentication and authorization

`/auth/register` creates a `member` account and `/auth/login` returns a 60-minute HS256 JWT. All application-data routes use the bearer token. Project, story, task, activity, project-member, eligible-user, and project-progress routes require a matching `ProjectMember` row. Dashboard queries are constrained to that user's project IDs. Notifications are constrained to their `recipient_id`; a user cannot retrieve, process, or delete someone else's notification by guessing an ID.

The user-management routes are `POST /users` and `GET /users`. Project-specific user selection is handled through `GET /projects/{project_id}/eligible-users`.

## Notification workflow

```text
Task assignment
  → persisted Notification(task_id, recipient_id, PENDING)
  → FastAPI BackgroundTask
  → validate task, recipient, story, and membership
  → SENT (available in recipient's in-app inbox)
    or FAILED (retry_count++, last_attempt_at, next_retry_at)
```

This is an in-app notification workflow, not an email or push integration. Each invocation performs one attempt. A failed notification can be manually processed again by its recipient until `MAX_NOTIFICATION_ATTEMPTS` (3) is reached. `next_retry_at` uses exponential seconds (`2^retry_count`) as retry tracking; no scheduler is currently included, so retry initiation is user-driven.

## Entity-Relationship Diagram

The database relationships are:

```text
User
 │
 ├── * ProjectMember * ── 1 Project
 │                         │
 │                         └── * UserStory
 │                                │
 │                                └── * Task
 │                                      │
 │                                      └── * Notification
 │
 ├── * Task (optional assignee)
 │
 └── * Notification (recipient)

Project
 └── * ActivityLog
```

## Database tables

### `users`

| Field         | Type        | Notes                                         |
| ------------- | ----------- | --------------------------------------------- |
| id            | Integer PK  | User identifier                               |
| name          | String(100) | Required                                      |
| email         | String(150) | Required, unique, indexed                     |
| password_hash | String(255) | Required bcrypt hash for API-created accounts |
| role          | String(20)  | Defaults to `member`                          |
| created_at    | DateTime    | UTC creation time                             |

### `projects`

| Field                   | Type        | Notes                                           |
| ----------------------- | ----------- | ----------------------------------------------- |
| id                      | Integer PK  | Project identifier                              |
| name                    | String(150) | Required                                        |
| description             | Text        | Nullable                                        |
| status                  | String(30)  | API-enforced: `ACTIVE`, `COMPLETED`, `ARCHIVED` |
| created_at / updated_at | DateTime    | Lifecycle timestamps                            |

### `project_members`

| Field      | Type                     | Notes                       |
| ---------- | ------------------------ | --------------------------- |
| id         | Integer PK               | Membership identifier       |
| project_id | Integer FK → projects.id | Required; cascade on delete |
| user_id    | Integer FK → users.id    | Required; cascade on delete |

### `user_stories`

| Field                   | Type                     | Notes                                          |
| ----------------------- | ------------------------ | ---------------------------------------------- |
| id                      | Integer PK               | Story identifier                               |
| project_id              | Integer FK → projects.id | Required; cascade on delete                    |
| title                   | String(200)              | Required                                       |
| description             | Text                     | Nullable                                       |
| status                  | String(30)               | API-enforced: `BACKLOG`, `IN_PROGRESS`, `DONE` |
| priority                | String(20)               | API-enforced: `LOW`, `MEDIUM`, `HIGH`          |
| created_at / updated_at | DateTime                 | Lifecycle timestamps                           |

### `tasks`

| Field                   | Type                         | Notes                                       |
| ----------------------- | ---------------------------- | ------------------------------------------- |
| id                      | Integer PK                   | Task identifier                             |
| user_story_id           | Integer FK → user_stories.id | Required; cascade on delete                 |
| title                   | String(200)                  | Required                                    |
| description             | Text                         | Nullable                                    |
| status                  | String(30)                   | API-enforced: `TODO`, `IN_PROGRESS`, `DONE` |
| priority                | String(20)                   | API-enforced: `LOW`, `MEDIUM`, `HIGH`       |
| assigned_to             | Integer FK → users.id        | Nullable assignee; must be a project member |
| due_date                | Date                         | Nullable                                    |
| created_at / updated_at | DateTime                     | Lifecycle timestamps                        |

### `notifications`

| Field           | Type                  | Notes                                                 |
| --------------- | --------------------- | ----------------------------------------------------- |
| id              | Integer PK            | Notification identifier                               |
| task_id         | Integer FK → tasks.id | Required; cascade on delete                           |
| recipient_id    | Integer FK → users.id | Required for newly created records; indexed recipient |
| message         | Text                  | Required                                              |
| status          | String(30)            | `PENDING`, `PROCESSING`, `SENT`, or `FAILED`          |
| retry_count     | Integer               | Number of failed attempts                             |
| last_attempt_at | DateTime              | Nullable                                              |
| next_retry_at   | DateTime              | Nullable retry-tracking time                          |
| created_at      | DateTime              | Creation time                                         |

### `activity_logs`

| Field       | Type                     | Notes                        |
| ----------- | ------------------------ | ---------------------------- |
| id          | Integer PK               | Activity identifier          |
| user_id     | Integer FK → users.id    | Nullable actor               |
| project_id  | Integer FK → projects.id | Nullable project             |
| action      | String(100)              | Required action label        |
| entity_type | String(50)               | Required entity label        |
| entity_id   | Integer                  | Nullable affected identifier |
| details     | Text                     | Nullable description         |
| created_at  | DateTime                 | Activity time                |

## API groups

* Authentication: registration, login, and current user.
* Projects: CRUD, project search/status filter, eligible-user list, and members.
* Stories and tasks: nested creation, resource CRUD, task assignment, due dates, and validation.
* Dashboard: membership-scoped summary and project progress.
* Notifications: recipient-scoped list/read/retry/delete.
* Activity: project and own/admin user history.

FastAPI documents request/response formats at `/docs`.

## Design tradeoffs

SQLite and process-local background tasks suit a small-team assignment and simple local setup. The notification model persists state and retry metadata, but a production system should replace the background task with a durable queue plus a scheduler. Authorization uses flat project membership instead of per-project roles to keep the scope focused.

