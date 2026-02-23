"""
Calendar view rendering. Each function renders one kind of period (day, week, month, quarter, year).
"""
import calendar
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from constants import (
    ANSI_REVERSE_END,
    ANSI_REVERSE_START,
    DAY_CELL_WIDTH,
    DAYS_PER_WEEK,
    FIRST_WEEKDAY_SUNDAY,
    MONTH_HEADER_WIDTH,
    MONTHS_PER_QUARTER,
    WEEKDAY_HEADER,
    YEAR_HEADER_WIDTH,
)

if TYPE_CHECKING:
    from events import Event


def render_month(year: int, month: int) -> None:
    """Render a single month as a 7-column grid (Sunday–Saturday)."""
    month_calendar = calendar.Calendar(firstweekday=FIRST_WEEKDAY_SUNDAY)
    weeks = month_calendar.monthdayscalendar(year, month)
    today = datetime.today()
    is_current_month = _is_same_month(today, year, month)
    header = _month_header(year, month)

    print(header.center(MONTH_HEADER_WIDTH))
    print(WEEKDAY_HEADER)
    for week in weeks:
        print(_format_week_row(week, today, is_current_month))


def _is_same_month(date: datetime, year: int, month: int) -> bool:
    return date.year == year and date.month == month


def _month_header(year: int, month: int) -> str:
    return f"{calendar.month_name[month]} {year}"


def _format_week_row(
    week: list[int], today: datetime, is_current_month: bool
) -> str:
    """Format one week of day numbers into a single line. Empty slots (0) become spaces; today is highlighted."""
    cells = []
    for day in week:
        cell = _format_day_cell(day, today, is_current_month)
        cells.append(cell)
    return " ".join(cells)


def _format_day_cell(day: int, today: datetime, is_current_month: bool) -> str:
    if day == 0:
        return " " * DAY_CELL_WIDTH
    cell = f"{day:{DAY_CELL_WIDTH}}"
    if is_current_month and day == today.day:
        cell = f"{ANSI_REVERSE_START}{day:{DAY_CELL_WIDTH}}{ANSI_REVERSE_END}"
    return cell


def _format_event_time_range(start: datetime, end: datetime) -> str:
    """Format event time range as HH:MM–HH:MM."""
    return f"{start.strftime('%H:%M')}–{end.strftime('%H:%M')}"


def render_day(date: datetime, events: list["Event"] | None = None) -> None:
    """Render a single day: weekday, month day, year, separator, then events (time range + description)."""
    weekday_name = calendar.day_name[date.weekday()]
    month_name = calendar.month_name[date.month]
    header = f"{weekday_name}, {month_name} {date.day}, {date.year}"
    print(header)
    print("-" * len(header))
    for ev in sorted(events or [], key=lambda e: e.start):
        time_range = _format_event_time_range(ev.start, ev.end)
        label = f"[{ev.category}] {ev.description}" if ev.category else ev.description
        print(f"  {time_range}  {label}")


def _hours_by_category(events: list["Event"]) -> dict[str, float]:
    """Sum meeting hours per category. Returns category -> total hours."""
    by_cat: dict[str, float] = {}
    for ev in events:
        hours = (ev.end - ev.start).total_seconds() / 3600.0
        key = ev.category if ev.category else "Uncategorized"
        by_cat[key] = by_cat.get(key, 0.0) + hours
    return by_cat


def _format_hours(hours: float) -> str:
    """Format hours as '1 hr' or '2 hrs' or '1.5 hrs'."""
    if hours == 1.0:
        return "1 hr"
    if hours == int(hours):
        return f"{int(hours)} hrs"
    return f"{hours:.1f} hrs"


def render_week(
    year: int,
    month: int,
    week_start: datetime,
    events: list["Event"] | None = None,
) -> None:
    """Render one week: range header, day numbers, aggregate hours by category, then events grouped by day."""
    week_end = week_start + timedelta(days=DAYS_PER_WEEK - 1)
    range_label = _week_range_label(week_start, week_end, year)
    print(range_label)
    print(WEEKDAY_HEADER)
    day_numbers = [
        f"{(week_start + timedelta(days=i)).day:{DAY_CELL_WIDTH}}"
        for i in range(DAYS_PER_WEEK)
    ]
    print(" ".join(day_numbers))
    events = events or []
    # Aggregate meeting hours by category
    by_category = _hours_by_category(events)
    if by_category:
        print()
        for cat in sorted(by_category.keys()):
            print(f"{cat}: {_format_hours(by_category[cat])}")
        print()
    by_day: dict[datetime, list["Event"]] = {}
    for ev in events:
        day = ev.start.replace(hour=0, minute=0, second=0, microsecond=0)
        by_day.setdefault(day, []).append(ev)
    for i in range(DAYS_PER_WEEK):
        day_date = week_start + timedelta(days=i)
        day_date = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_events = sorted(by_day.get(day_date, []), key=lambda e: e.start)
        if day_events:
            weekday_abbr = calendar.day_abbr[day_date.weekday()]
            print(f"\n{weekday_abbr} {day_date.month}/{day_date.day}")
            for ev in day_events:
                time_range = _format_event_time_range(ev.start, ev.end)
                label = f"[{ev.category}] {ev.description}" if ev.category else ev.description
                print(f"  {time_range}  {label}")


def _week_range_label(week_start: datetime, week_end: datetime, year: int) -> str:
    start_abbr = calendar.month_abbr[week_start.month]
    end_abbr = calendar.month_abbr[week_end.month]
    return f"Week of {start_abbr} {week_start.day} – {end_abbr} {week_end.day}, {year}"


def render_quarter(year: int, quarter: int) -> None:
    """Render a quarter as three month names (Q1=Jan–Mar, etc.)."""
    start_month = (quarter - 1) * MONTHS_PER_QUARTER + 1
    month_names = [
        calendar.month_name[start_month + i]
        for i in range(MONTHS_PER_QUARTER)
    ]
    print(f"Q{quarter} {year}: {', '.join(month_names)}")


def render_year(year: int) -> None:
    """Render a year as a centered title and 12 abbreviated month names."""
    print(str(year).center(YEAR_HEADER_WIDTH))
    print()
    month_abbreviations = [calendar.month_abbr[m] for m in range(1, 13)]
    print(" ".join(month_abbreviations))
