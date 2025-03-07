from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class EventBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    event_type: str
    location: Optional[str] = None


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CalendarQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SuccessResponse(BaseModel):
    success: bool
    message: str