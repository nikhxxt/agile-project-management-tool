# AgileFlow Platform

A full-stack Agile Project Management Tool designed for small teams to manage projects, user stories, tasks, team members, activity history, and notifications through a simple Agile workflow.

## Project Overview

AgileFlow follows a hierarchical work-management model:

Project → User Story → Task

Users can create and manage projects, organize work into user stories, create and assign tasks, update task status and priority, track project activity, and receive notifications for relevant task events.

The application is designed with a separate React frontend and FastAPI backend, with SQLite used for persistent storage.

## Key Features

### Authentication & Authorization
- User registration and login
- JWT-based authentication
- Password hashing
- Protected frontend routes
- Protected backend APIs
- Project membership and task-assignment validation

### Project Management
- Create, view, update, and delete projects
- Project status management
- Project team members
- Project progress overview

### User Stories
- Create, view, update, and delete stories
- Story status
- Story priority
- Stories organized under projects

### Task Management
- Create, view, update, and delete tasks
- Tasks organized under user stories
- Task status:
  - TODO
  - IN_PROGRESS
  - DONE
- Task priority:
  - LOW
  - MEDIUM
  - HIGH
- Assign and unassign tasks to project members
- Task descriptions and due-date support

### Dashboard
- Project statistics
- Story and task counts
- Completion progress
- Task status breakdown
- Task priority breakdown
- Workspace-level progress information

### Search & Filtering
- Project search
- Task status filtering
- Task priority filtering
- Task assignee filtering
- Clear filters

### Activity Log
The application records important project events such as:
- Project creation and updates
- Story creation and updates
- Task creation
- Task updates
- Task assignment changes
- Task status changes

Activity history is displayed within the project workspace.

### Notifications
Users receive notifications for relevant task events.

Notifications include:
- Related task information
- Related project navigation
- Processing status
- Retry information
- Notification deletion

## Asynchronous Workflow

AgileFlow includes an asynchronous notification workflow.

When a task is created:

Task Creation
↓
Notification Created
↓
Background Processing
↓
SENT / FAILED
↓
Retry Handling

The backend uses background processing so notification handling does not block the main task-creation request.

Notification records maintain processing information such as status and retry count. Failures can be tracked and retried according to the implemented notification workflow.

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
- Password hashing
- Uvicorn

### Database
- SQLite

### Testing
- Pytest

## Architecture

The application follows a separated frontend/backend architecture.

```text
React Frontend
      ↓
REST API
      ↓
FastAPI Backend
      ↓
SQLAlchemy
      ↓
SQLite Database
````

The main work hierarchy is:

```text
Project
   ↓
User Story
   ↓
Task
```

Supporting relationships include:

```text
User
  ↓
ProjectMember
  ↓
Project

Task
  ↓
Notification

Project
  ↓
ActivityLog
```

## Project Structure

```text
agile-project-management-tool/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── components/
│   │   └── App.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## API Documentation

The backend provides interactive API documentation through FastAPI.

When running locally:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI can be used to explore and test the available REST API endpoints.

## Local Setup

### Prerequisites

* Python 3.11+
* Node.js and npm
* Git

### 1. Clone the Repository

```bash
git clone <[GITHUB_REPOSITORY_URL](https://github.com/nikhxxt/agile-project-management-tool>
cd agile-project-management-tool
```

### 2. Backend Setup

```powershell
cd backend

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

$env:PYTHONPATH = "."
python -m uvicorn app.main:app
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 3. Frontend Setup

Open another terminal:

```powershell
cd frontend

npm install
npm run dev
```

Frontend:

```text
http://localhost:5174
```

## Testing

Run backend tests:

```powershell
cd backend

$env:PYTHONPATH = "."
pytest -q
```

Expected result:

```text
8 passed
```

Build the frontend:

```powershell
cd frontend
npm run build
```

## Database Schema

The application uses SQLite for persistent storage.

The main entities include:

* User
* Project
* ProjectMember
* UserStory
* Task
* Notification
* ActivityLog

The primary hierarchy is:

```text
Project
   │
   └── UserStory
          │
          └── Task
```

Project membership connects users with projects, while notifications and activity logs provide supporting workflow and audit information.

A detailed ER/database diagram is documented separately in the project documentation.

## Security Considerations

The application includes several security measures:

* JWT-based authentication
* Password hashing rather than storing plaintext passwords
* Protected frontend routes
* Authentication checks on backend endpoints
* Project membership validation
* Task assignment validation
* Environment variables for sensitive configuration
* `.gitignore` used to prevent local/generated files and secrets from being committed

Production deployment should use HTTPS, secure secret management, stronger production configuration, and a production-grade database where appropriate.

## Design Decisions & Tradeoffs

### SQLite

SQLite was selected because the assignment targets a small team and SQLite provides simple persistent storage without requiring a separate database server.

For a larger production deployment, PostgreSQL or another production-grade relational database would be more appropriate.

### REST API

REST was selected because the application's operations map naturally to resources such as projects, stories, tasks, users, activities, and notifications.

### React + FastAPI

React provides a component-based frontend suitable for an interactive project-management interface, while FastAPI provides a lightweight Python framework for building documented REST APIs.

### Frontend / Backend Separation

Separating the frontend and backend keeps presentation logic independent from business and persistence logic and allows the API to be tested independently.

### Background Processing

Notification processing is handled asynchronously so notification work does not block the primary task operation.

### Notification Retry Handling

Notification records track processing state and retry information so failures can be identified and handled without silently losing notification events.

## AI Usage

AI tools were used during development as a development assistant for:

* Debugging errors
* Reviewing implementation approaches
* Improving UI structure and styling
* Generating development suggestions
* Assisting with documentation
* Reviewing API and frontend integration issues

All generated suggestions were reviewed, tested, and integrated based on the application's actual requirements and behavior.

## Future Improvements

With additional development time, the application could be extended with:

* Role-based permissions with more granular project roles
* Advanced reporting and analytics
* Kanban-style task visualization
* Email or push notifications
* Improved notification retry infrastructure
* PostgreSQL for larger deployments
* Automated CI/CD
* More comprehensive automated frontend testing
* Enhanced audit and monitoring capabilities

## Demo

### Demo Application

Add the deployed application URL here if available:

```text
<DEMO_URL>
```

### Walkthrough Video

Add the walkthrough video link here if available:

```text
<VIDEO_URL>
```

## Demo Account

If a dedicated demo account is provided:

```text
Email: demo4@example.com
Password: demo123
```

Do not commit real production credentials to the repository.

## Project Status

The application implements the core requirements of the Agile Project Management Tool assignment, including:

* Full-stack frontend and backend
* Persistent SQLite storage
* Project → User Story → Task hierarchy
* CRUD operations
* Task assignment and organization
* Authentication and authorization
* Activity logging
* Asynchronous notifications
* API documentation
* Automated backend tests

````

### ⚠️ Before you paste it

There are **3 placeholders you must replace**:

```text
<GITHUB_REPOSITORY_URL>
<DEMO_URL>
<VIDEO_URL>
````

And only add demo credentials if you're actually providing a dedicated demo account.

**Next after README:** we do the **Architecture + Database Schema/ER diagram** documentation.
