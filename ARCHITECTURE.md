# AgileFlow Platform — Architecture & Database Schema

## 1. System Architecture

AgileFlow uses a separated frontend/backend architecture.

```text
┌──────────────────────┐
│   React Frontend     │
│   Vite Application   │
└──────────┬───────────┘
           │ HTTP / REST API
           ▼
┌──────────────────────┐
│    FastAPI Backend   │
│ Authentication       │
│ Business Logic       │
│ API Routes           │
│ Background Tasks     │
└──────────┬───────────┘
           │ SQLAlchemy
           ▼
┌──────────────────────┐
│      SQLite DB       │
│ Persistent Storage   │
└──────────────────────┘
