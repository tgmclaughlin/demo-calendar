from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.database import Event, get_db, init_db
from app.models.schemas import EventCreate, EventResponse, SuccessResponse

# Initialize FastAPI app
app = FastAPI(title="AI Performance Manager Calendar")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize database
init_db()


@app.get("/", response_class=HTMLResponse)
async def get_calendar_ui(request: Request):
    """Render the calendar UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/events", response_model=EventResponse)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new calendar event."""
    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=400, detail="End time must be after start time"
        )

    db_event = Event(
        title=event.title,
        start_time=event.start_time,
        end_time=event.end_time,
        event_type=event.event_type,
        location=event.location,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.delete("/api/events/{event_id}", response_model=SuccessResponse)
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete an existing calendar event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()
    return {"success": True, "message": f"Event {event_id} deleted successfully"}


@app.delete("/api/calendar/clear", response_model=SuccessResponse)
async def clear_calendar(db: Session = Depends(get_db)):
    """Delete all events from the calendar."""
    events_count = db.query(Event).count()
    db.query(Event).delete()
    db.commit()
    return {"success": True, "message": f"Calendar cleared. {events_count} events deleted."}


@app.get("/api/calendar", response_model=List[EventResponse])
async def get_calendar(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Retrieve calendar events with optional date filtering."""
    query = db.query(Event)

    if start_date:
        query = query.filter(Event.start_time >= start_date)
    if end_date:
        query = query.filter(Event.end_time <= end_date)

    events = query.order_by(Event.start_time).all()
    return events


@app.get("/api/calendar/llm", response_model=str)
async def get_calendar_for_llm(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """
    Generate a structured text representation of the calendar for LLM processing.
    """
    # Set default range to one week if not provided
    if not start_date:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if not end_date:
        end_date = start_date + timedelta(days=7)

    events = (
        db.query(Event)
        .filter(Event.start_time >= start_date, Event.start_time <= end_date)
        .order_by(Event.start_time)
        .all()
    )

    # Format events for LLM consumption
    llm_calendar = f"Calendar from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}:\n\n"

    # Group by day
    current_day = None
    for event in events:
        event_day = event.start_time.date()
        
        if current_day != event_day:
            current_day = event_day
            day_str = event.start_time.strftime("%A, %B %d, %Y")
            llm_calendar += f"== {day_str} ==\n"
        
        # Format time
        start_time = event.start_time.strftime("%I:%M %p")
        end_time = event.end_time.strftime("%I:%M %p")
        
        # Add event details
        llm_calendar += f"- {start_time} - {end_time}: {event.title} ({event.event_type})"
        if event.location:
            llm_calendar += f" at {event.location}"
        llm_calendar += "\n"
    
    if not events:
        llm_calendar += "No events scheduled for this period.\n"
        
    return llm_calendar