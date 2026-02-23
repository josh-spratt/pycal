"""
Event model for PyCal scheduling. Minimal dataclass for description and start/end timestamps.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    """A single calendar event with description and time range."""

    description: str
    category: str
    start: datetime
    end: datetime
