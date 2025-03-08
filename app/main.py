from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import random

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


@app.post("/api/populate-mock-calendar", response_model=SuccessResponse)
async def populate_mock_calendar(db: Session = Depends(get_db)):
    """Populate the calendar with realistic events for an Applied AI Solutions architect."""
    
    # Clear existing events first
    db.query(Event).delete()
    
    # Use March 8, 2025 (Saturday) as the start date to match the calendar UI
    start_date = datetime(2025, 3, 8).date()
    
    # Client companies (big names)
    clients = [
        "Goldman Sachs", "JP Morgan", "Google", "Microsoft", "Meta", 
        "Netflix", "Amazon", "Tesla"
    ]
    
    # Types of meetings
    meeting_types = [
        "Project Kickoff", "Technical Review", "Architecture Workshop",
        "Solution Design", "Progress Review"
    ]
    
    # Locations
    locations = [
        "Client HQ", "Virtual", "Conference Room A", "Innovation Lab", 
        "Teams Meeting"
    ]
    
    # Event count tracker
    events_created = 0
    
    # Create Tuesday/Thursday standups only
    standup_dates = [
        datetime(2025, 3, 11).date(),  # Tuesday
        datetime(2025, 3, 13).date()   # Thursday
    ]
    
    for standup_date in standup_dates:
        standup = Event(
            title="Team Standup",
            start_time=datetime.combine(standup_date, datetime.min.time().replace(hour=9, minute=0)),
            end_time=datetime.combine(standup_date, datetime.min.time().replace(hour=9, minute=30)),
            event_type="work",
            location="Teams Meeting"
        )
        db.add(standup)
        events_created += 1
    
    # Add only 3 client meetings for the entire week
    client_meetings = [
        {
            "title": f"{random.choice(clients)} Project Kickoff",
            "date": datetime(2025, 3, 10).date(),  # Monday
            "start_hour": 11,
            "start_minute": 0,
            "duration": 60,
            "location": "Client HQ"
        },
        {
            "title": f"{random.choice(clients)} Technical Review",
            "date": datetime(2025, 3, 12).date(),  # Wednesday
            "start_hour": 14,
            "start_minute": 0,
            "duration": 90,
            "location": "Conference Room A"
        },
        {
            "title": f"{random.choice(clients)} Architecture Workshop",
            "date": datetime(2025, 3, 14).date(),  # Friday
            "start_hour": 10,
            "start_minute": 30,
            "duration": 60,
            "location": "Virtual"
        }
    ]
    
    for meeting in client_meetings:
        event = Event(
            title=meeting["title"],
            start_time=datetime.combine(meeting["date"], datetime.min.time().replace(hour=meeting["start_hour"], minute=meeting["start_minute"])),
            end_time=datetime.combine(meeting["date"], datetime.min.time().replace(hour=meeting["start_hour"], minute=meeting["start_minute"])) + timedelta(minutes=meeting["duration"]),
            event_type="work",
            location=meeting["location"]
        )
        db.add(event)
        events_created += 1
    
    # Add one client dinner (Thursday evening - March 13)
    thursday = datetime(2025, 3, 13).date()
    dinner = Event(
        title=f"Client Dinner with {random.choice(clients)} Executive Team",
        start_time=datetime.combine(thursday, datetime.min.time().replace(hour=19, minute=0)),
        end_time=datetime.combine(thursday, datetime.min.time().replace(hour=21, minute=0)),
        event_type="work",
        location="The Capital Grille"
    )
    db.add(dinner)
    events_created += 1

    
    # Commit all events
    db.commit()
    
    return {"success": True, "message": f"Calendar populated with {events_created} realistic events for an Applied AI Solutions architect."}