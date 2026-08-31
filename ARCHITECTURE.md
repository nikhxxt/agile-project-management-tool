# AgileFlow Platform — Architecture & Database Schema

## 1. System Architecture

AgileFlow uses a separated frontend and backend architecture.

```text
┌──────────────────────┐
│     React Frontend   │
│    Vite Application  │
└──────────┬───────────┘
           │
           │ HTTP / REST API
           ▼
┌──────────────────────┐
│    FastAPI Backend   │
│                      │
│  Authentication      │
│  Authorization       │
│  API Routes          │
│  Business Logic      │
│  Background Tasks    │
└──────────┬───────────┘
           │
           │ SQLAlchemy
           ▼
┌──────────────────────┐
│      SQLite DB       │
│   Persistent Storage  │
└──────────────────────┘
````

The frontend handles the user interface and communicates with the backend through REST APIs.

The backend handles authentication, authorization, business logic, database operations, activity logging, and asynchronous notification processing.

SQLite provides persistent storage for application data.

---

## 2. Application Flow

```text
User
  ↓
React Frontend
  ↓
REST API
  ↓
FastAPI Backend
  ↓
Authentication / Authorization
  ↓
Business Logic
  ↓
SQLAlchemy
  ↓
SQLite Database
```

The frontend and backend are maintained separately, allowing the API and business logic to operate independently from the presentation layer.

---

## 3. Work Item Hierarchy

AgileFlow follows the required hierarchical work-management model:

```text
Project
   │
   └── User Story
          │
          └── Task
```

### Project

A project represents a team's overall workspace for managing related work.

A project can contain multiple user stories and project members.

### User Story

A user story represents a feature, requirement, or piece of functionality within a project.

Each user story belongs to a project and can contain multiple tasks.

### Task

A task represents an individual unit of work belonging to a user story.

Tasks can contain information such as:

* Title
* Description
* Status
* Priority
* Assignee
* Due date

---

## 4. User and Project Membership

Users participate in projects through project membership.

```text
User
  │
  └── ProjectMember
          │
          └── Project
```

`ProjectMember` represents the relationship between users and projects.

This relationship is also used when validating access to project resources and task assignments.

---

## 5. Task Assignment

Tasks can be assigned to project members.

```text
Project
   │
   ├── ProjectMember
   │       │
   │       └── User
   │
   └── UserStory
          │
          └── Task
                 │
                 └── Assignee → User
```

The application supports both assigned and unassigned tasks.

Task assignment is validated against project membership to prevent assigning tasks to users outside the project.

---

## 6. Notifications

Notifications provide an asynchronous workflow for relevant task events.

```text
Task
 │
 └── Notification
```

When a task is created, a notification record can be generated and processed in the background.

Notification records contain processing information such as:

* Notification status
* Retry count
* Related task
* Related project
* Creation timestamp

---

## 7. Activity Logging

Project activity is recorded through the activity log.

```text
Project
   │
   └── ActivityLog
```

Activity records provide an audit trail of important actions performed within a project.

Examples include:

* Project creation
* Project updates
* Story creation
* Story updates
* Task creation
* Task updates
* Task assignment changes
* Task status changes

Activity records also identify the user associated with the action.

---

# Database Schema

## 8. Database Overview

AgileFlow uses SQLite as its persistent relational database.

The main entities are:

* User
* Project
* ProjectMember
* UserStory
* Task
* Notification
* ActivityLog

The database models the required work hierarchy while also supporting authentication, project membership, notifications, and activity tracking.

---

## 9. Core Entity Relationships

The primary work hierarchy is:

```text
Project
   │
   └── UserStory
          │
          └── Task
```

Project membership is represented through:

```text
User
   │
   └── ProjectMember
          │
          └── Project
```

Supporting workflow relationships include:

```text
Task
   │
   └── Notification
```

and:

```text
Project
   │
   └── ActivityLog
```

---

## 10. Entity Relationship Overview

```text
                    ┌──────────────┐
                    │     User     │
                    └──────┬───────┘
                           │
                           │
                    ┌──────▼───────┐
                    │ProjectMember │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Project   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌───────────┐ ┌───────────┐ ┌─────────────┐
        │ UserStory │ │ActivityLog│ │ProjectMember│
        └─────┬─────┘ └───────────┘ └─────────────┘
              │
              ▼
        ┌───────────┐
        │   Task    │
        └─────┬─────┘
              │
              ▼
        ┌──────────────┐
        │ Notification │
        └──────────────┘
```

---

## 11. Entity Responsibilities

| Entity        | Purpose                                                         |
| ------------- | --------------------------------------------------------------- |
| User          | Stores application users and authentication-related information |
| Project       | Represents a project workspace                                  |
| ProjectMember | Associates users with projects                                  |
| UserStory     | Represents a story or requirement within a project              |
| Task          | Represents an individual unit of work within a story            |
| Notification  | Stores task-related notification events and processing state    |
| ActivityLog   | Stores project activity and audit events                        |

---

## 12. Project → User Story → Task Relationship

The central relationship of the application is:

```text
Project
   │
   ├── User Story 1
   │      ├── Task 1
   │      └── Task 2
   │
   ├── User Story 2
   │      ├── Task 3
   │      └── Task 4
   │
   └── User Story 3
          └── Task 5
```

This structure allows teams to organize high-level project work into stories and then break stories into actionable tasks.

---

## 13. Project Membership Relationship

A user can participate in projects through the `ProjectMember` relationship.

```text
User
  │
  ├── ProjectMember → Project A
  │
  ├── ProjectMember → Project B
  │
  └── ProjectMember → Project C
```

This supports project-level access control and allows tasks to be assigned to valid project members.

---

## 14. Notification Relationship

Task events can produce notification records.

```text
Create Task
     ↓
Notification Created
     ↓
Background Processing
     ↓
SENT / FAILED
     ↓
Retry / Failure Tracking
```

Notifications are stored persistently so their processing status and retry information can be tracked.

---

## 15. Activity Log Relationship

Important project actions are recorded as activity events.

```text
User
  │
  │ performs action
  ▼
Project / Story / Task
  │
  ▼
ActivityLog
```

Examples:

```text
CREATEPROJECT
CREATESTORY
CREATETASK
UPDATETASK
ASSIGNTASK
STATUS_CHANGETASK
```

This provides visibility into changes made within a project.

---

## 16. Database Tables, Fields, Primary Keys and Foreign Keys

The following schema reflects the SQLAlchemy models used by the application.

### Users

| Field | Type | Key | Nullable | Description |
|---|---|---|---|---|
| id | Integer | PK | No | Unique user identifier |
| name | String(100) | — | No | User name |
| email | String(150) | Unique | No | User email address |
| password_hash | String(255) | — | Yes | Hashed password |
| role | String(20) | — | Yes | User role, default `member` |
| created_at | DateTime | — | Yes | Account creation timestamp |

### Projects

| Field | Type | Key | Nullable | Description |
|---|---|---|---|---|
| id | Integer | PK | No | Unique project identifier |
| name | String(150) | — | No | Project name |
| description | Text | — | Yes | Project description |
| status | String(30) | — | Yes | Project status, default `ACTIVE` |
| created_at | DateTime | — | Yes | Project creation timestamp |
| updated_at | DateTime | — | Yes | Last update timestamp |

### Project Members

| Field | Type | Key | Nullable | Description |
|---|---|---|---|---|
| id | Integer | PK | No | Unique membership identifier |
| project_id | Integer | FK → projects.id | No | Associated project |
| user_id | Integer | FK → users.id | No | Associated user |

`project_id` and `user_id` use cascading deletion with their parent records.

### User Stories

| Field | Type | Key | Nullable | Description |
|---|---|---|---|---|
| id | Integer | PK | No | Unique story identifier |
| project_id | Integer | FK → projects.id | No | Parent project |
| title | String(200) | — | No | Story title |
| description | Text | — | Yes | Story description |
| status | String(30) | — | Yes | Story status, default `BACKLOG` |
| priority | String(20) | — | Yes | Story priority, default `MEDIUM` |
| created_at | DateTime | — | Yes | Story creation timestamp |
| updated_at | DateTime | — | Yes | Last update timestamp |

### Tasks

| Field | Type | Key | Nullable | Description |
|---|---|---|---|---|
| id | Integer | PK | No | Unique task identifier |
| user_story_id | Integer | FK → user_stories.id | No | Parent user story |
| title | String(200) | — | No | Task title |
| description | Text | — | Yes | Task description |
| status | String(30) | — | Yes | Task status, default `TODO` |
| priority | String(20) | — | Yes | Task priority, default `MEDIUM` |
| assigned_to | Integer | FK → users.id | Yes | Assigned user |
| due_date | Date | — | Yes | Task due date |
| created_at | DateTime | — | Yes | Task creation timestamp |
| updated_at | DateTime | — | Yes | Last update timestamp |

A task may remain unassigned because `assigned_to` is nullable.

### Notifications

| Field | Type | Key | Nullable | Description |
|---|---|---|---|---|
| id | Integer | PK | No | Unique notification identifier |
| task_id | Integer | FK → tasks.id | No | Related task |
| message | Text | — | No | Notification message |
| status | String(30) | — | Yes | Processing status, default `PENDING` |
| retry_count | Integer | — | Yes | Number of processing retries, default `0` |
| created_at | DateTime | — | Yes | Notification creation timestamp |

`task_id` uses cascading deletion when its associated task is deleted.

### Activity Logs

| Field | Type | Key | Nullable | Description |
|---|---|---|---|---|
| id | Integer | PK | No | Unique activity identifier |
| user_id | Integer | FK → users.id | Yes | User who performed the action |
| project_id | Integer | FK → projects.id | Yes | Related project |
| action | String(100) | — | No | Action performed |
| entity_type | String(50) | — | No | Type of entity affected |
| entity_id | Integer | — | Yes | Identifier of affected entity |
| details | Text | — | Yes | Additional activity information |
| created_at | DateTime | — | Yes | Activity timestamp |

`user_id` and `project_id` are nullable because an activity record may not always require a directly associated user or project.

---

## 17. Foreign Key Relationships

The database relationships are:

| Child Table | Foreign Key | Parent Table | Relationship |
|---|---|---|---|
| project_members | project_id | projects.id | Project membership belongs to a project |
| project_members | user_id | users.id | Project membership belongs to a user |
| user_stories | project_id | projects.id | Story belongs to a project |
| tasks | user_story_id | user_stories.id | Task belongs to a story |
| tasks | assigned_to | users.id | Task can be assigned to a user |
| notifications | task_id | tasks.id | Notification belongs to a task |
| activity_logs | user_id | users.id | Activity can reference the acting user |
| activity_logs | project_id | projects.id | Activity can reference a project |

---

## 18. Relationship Cardinality

The main relationships can be summarized as:

```text
User 1 ──────── * ProjectMember * ──────── 1 Project

Project 1 ───── * UserStory

UserStory 1 ─── * Task

User 1 ──────── * Task
                 (assignment)

Task 1 ──────── * Notification

User 1 ──────── * ActivityLog
                 (optional)

Project 1 ───── * ActivityLog
                 (optional)
````

This results in the core hierarchy:

```text
Project
   │
   └── UserStory
          │
          └── Task
                 │
                 └── Notification
```

while users connect to projects through `ProjectMember` and can also be assigned tasks and associated with activity records.

---

## 19. Cascade and Optional Relationships

The database uses cascading deletion for several parent-child relationships.

When a project is deleted, its project memberships and user stories are configured to be removed with the project.

When a user story is deleted, its associated tasks are configured to be removed with the story.

When a task is deleted, its associated notifications are configured to be removed with the task.

Some relationships are intentionally optional:

* `Task.assigned_to` may be null for unassigned tasks.
* `ActivityLog.user_id` may be null.
* `ActivityLog.project_id` may be null.
* `ActivityLog.entity_id` may be null.
* `User.password_hash` may be null.

---

## 20. Database Design Summary

The relational database is centered around the project management hierarchy:

```text
Project
   ↓
UserStory
   ↓
Task
```

Additional tables support:

```text
User
  ↓
ProjectMember
  ↓
Project
```

and:

```text
Task
  ↓
Notification
```

and:

```text
Project
  ↓
ActivityLog
```

