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

## 16. Primary Keys and Foreign Keys

Each main entity is identified by a primary key.

Foreign keys establish relationships between related records.

The key relationships are:

```text
Project
   ↓
UserStory
   ↓
Task
```

```text
User
   ↓
ProjectMember
   ↓
Project
```

```text
Task
   ↓
Notification
```

```text
Project
   ↓
ActivityLog
```

The exact database column definitions are maintained in the backend SQLAlchemy models.

---

## 17. Data Integrity

The relational structure maintains the association between parent and child work items.

For example:

* A user story belongs to a project.
* A task belongs to a user story.
* A project member connects a user with a project.
* A task assignment references a user.
* A notification references task-related activity.
* An activity log records project activity.

Backend validation is used to ensure that protected operations are performed only against valid and authorized project resources.

---

## 18. Asynchronous Notification Workflow

The notification system uses background processing.

```text
User creates task
       ↓
Task saved to database
       ↓
Notification created
       ↓
Background processing
       ↓
Notification status updated
       ↓
SENT / FAILED
```

This design keeps notification processing separate from the main task creation flow.

If notification processing encounters a failure, the notification record retains processing information such as its status and retry count.

---

## 19. API and Database Interaction

The backend acts as the main application layer between the frontend and database.

```text
React
  ↓
HTTP Request
  ↓
FastAPI Route
  ↓
Authentication / Authorization
  ↓
Business Logic
  ↓
SQLAlchemy
  ↓
SQLite
  ↓
Response
  ↓
React
```

This keeps database access inside the backend rather than exposing the database directly to the frontend.

---

## 20. Design Considerations

### SQLite

SQLite was selected because the assignment targets a small team and SQLite provides persistent relational storage without requiring a separate database server.

For a larger production deployment, PostgreSQL or another production-grade relational database would be more suitable.

### Relational Model

A relational database is appropriate because the application contains clear relationships between users, projects, stories, tasks, notifications, and activity records.

### Separation of Responsibilities

The frontend is responsible for presentation and user interaction.

The backend is responsible for:

* Authentication
* Authorization
* Business logic
* Database operations
* Activity logging
* Notification processing

This separation improves maintainability and makes the system easier to extend.

---

## 21. Summary

AgileFlow is structured around the following core model:

```text
User
 │
 ├── ProjectMember
 │        │
 │        ▼
 │      Project
 │        │
 │        ▼
 │     UserStory
 │        │
 │        ▼
 │       Task
 │        │
 │        ▼
 │   Notification
 │
 └────────────── Activity / Project Access
```

The architecture and database design support the application's primary requirements:

* Small-team project management
* Project → User Story → Task hierarchy
* User and project relationships
* Task assignment
* Persistent storage
* Activity tracking
* Asynchronous notifications
* Authentication and authorization

