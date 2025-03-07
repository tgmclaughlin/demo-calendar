# AI Performance Manager Calendar

A minimalist web application for managing training schedules, serving as the foundation for an AI coaching system targeted at busy professionals who participate in group training activities.

## Features

- Clean, modern calendar interface with week and day views
- Easy event creation, editing, and deletion
- Visual differentiation between event types (work, training, etc.)
- Responsive design that works on mobile and desktop
- FastAPI backend with SQLite database

## Getting Started

### Prerequisites

- Python 3.12 or higher

### Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -e .
```

### Running the Application

```bash
python run.py
```

The application will be available at http://localhost:8000

## API Endpoints

- `POST /api/events` - Create a new calendar event
- `DELETE /api/events/{event_id}` - Delete an existing event
- `GET /api/calendar` - Get all calendar events with optional date filtering
- `GET /api/calendar/llm` - Get calendar events in a format suitable for LLM processing

## Project Structure

- `app/` - Main application directory
  - `main.py` - FastAPI application and endpoints
  - `models/` - Database models and Pydantic schemas
  - `templates/` - HTML templates (single-file UI)
  - `static/` - Static assets (if any)
- `run.py` - Application entry point