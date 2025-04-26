<img width="1535" alt="image" src="https://github.com/user-attachments/assets/9285576c-2d4b-47c2-a54f-6907f6b6fb28" />

# Reusable Calendar Component

A minimalist and flexible calendar component that can be integrated into any web application. Built with FastAPI and vanilla JavaScript, it provides a clean, modern interface for event management.

## Features

- Clean, modern calendar interface with week and day views
- Easy event creation, editing, and deletion
- Visual differentiation between event types (customizable)
- Responsive design that works on mobile and desktop
- FastAPI backend with SQLite database
- Easily customizable for different use cases

## Getting Started

### Prerequisites

- Python 3.12 or higher
- uv (Python package installer)

### Installation

1. Clone the repository
2. Install dependencies using uv:

```bash
uv sync
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

## Customization

The calendar component is designed to be easily customizable:

- Update the event colors in the CSS to match your application's theme
- Modify the event types to suit your specific use cases
- Extend the API to add additional functionality

## Integration

To integrate this component into your existing application:

1. Copy the `app/templates/index.html` file and adapt it to your UI
2. Import the FastAPI routes from `app/main.py` into your application
3. Ensure your database models are compatible with the ones defined in `app/models/`

## Development

For development work:

```bash
# Install dev dependencies
uv sync -e dev

# Format code
black app/

# Type checking
mypy app/
```
