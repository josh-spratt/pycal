"""
PyCal – View and manage calendar from the command line.

Usage examples:
  pycal view                    # current month
  pycal view month --year 2024 --month 6
  pycal view day --date 2024-07-04
  pycal view week --date 2024-01-15
  pycal view quarter
  pycal view year
  pycal view --help
  pycal --help
"""
import argparse
from datetime import datetime, timedelta

from constants import DATE_FORMAT, DATETIME_FORMAT, DAYS_PER_WEEK, MONTHS_PER_QUARTER
from events import Event
from storage import add_event, events_in_range
from views import (
    render_day,
    render_month,
    render_quarter,
    render_week,
    render_year,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pycal",
        description="View and manage calendar from the command line.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="command")
    view_parser = subparsers.add_parser("view", help="View calendar by period")
    view_parser.add_argument(
        "period",
        nargs="?",
        default="month",
        choices=["day", "week", "month", "quarter", "year"],
        help="period to view (default: month)",
    )
    view_parser.add_argument("--year", type=int, default=None, help="year (default: current)")
    view_parser.add_argument("--month", type=int, default=None, help="month 1–12 (default: current)")
    view_parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="date for day/week (YYYY-MM-DD; default: today)",
    )
    add_parser = subparsers.add_parser("add", help="Add a calendar event")
    add_parser.add_argument(
        "description",
        type=str,
        help="event description",
    )
    add_parser.add_argument(
        "--start",
        type=str,
        required=True,
        help="start time (YYYY-MM-DDTHH:MM)",
    )
    add_parser.add_argument(
        "--end",
        type=str,
        required=True,
        help="end time (YYYY-MM-DDTHH:MM)",
    )
    add_parser.add_argument(
        "--category",
        type=str,
        default="",
        help="event category (default: none)",
    )
    return parser


def _parse_date(date_string: str | None, parser: argparse.ArgumentParser) -> datetime:
    """Parse --date from args; use today when omitted. Encapsulates boundary condition."""
    if date_string is None:
        return datetime.today()
    try:
        return datetime.strptime(date_string, DATE_FORMAT)
    except ValueError:
        parser.error(f"invalid --date '{date_string}'; use YYYY-MM-DD")


def _parse_datetime(s: str, parser: argparse.ArgumentParser, flag: str) -> datetime:
    """Parse a datetime string (YYYY-MM-DDTHH:MM)."""
    try:
        return datetime.strptime(s, DATETIME_FORMAT)
    except ValueError:
        parser.error(f"invalid {flag} '{s}'; use YYYY-MM-DDTHH:MM")


def _resolve_year_month(args: argparse.Namespace, today: datetime) -> tuple[int, int]:
    """Resolve view year and month from args or current date."""
    year = args.year if args.year is not None else today.year
    month = args.month if args.month is not None else today.month
    return year, month


def _week_start_sunday(reference_date: datetime) -> datetime:
    """Return the Sunday that starts the week containing reference_date."""
    days_since_sunday = (reference_date.weekday() + 1) % 7
    return reference_date - timedelta(days=days_since_sunday)


def _run_day_view(ref_date: datetime) -> None:
    day_start = ref_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    events = events_in_range(day_start, day_end)
    render_day(ref_date, events)


def _run_week_view(ref_date: datetime) -> None:
    week_start = _week_start_sunday(ref_date)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=DAYS_PER_WEEK)
    events = events_in_range(week_start, week_end)
    render_week(week_start.year, week_start.month, week_start, events)


def _run_month_view(year: int, month: int) -> None:
    render_month(year, month)


def _run_quarter_view(year: int, month: int) -> None:
    quarter = (month - 1) // MONTHS_PER_QUARTER + 1
    render_quarter(year, quarter)


def _run_year_view(year: int) -> None:
    render_year(year)


def _dispatch_view(
    period: str,
    year: int,
    month: int,
    ref_date: datetime,
) -> None:
    """Dispatch to the appropriate view renderer for the given period."""
    handlers = {
        "day": lambda: _run_day_view(ref_date),
        "week": lambda: _run_week_view(ref_date),
        "month": lambda: _run_month_view(year, month),
        "quarter": lambda: _run_quarter_view(year, month),
        "year": lambda: _run_year_view(year),
    }
    handlers[period]()


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "view":
        today = datetime.today()
        ref_date = _parse_date(args.date, parser)
        year, month = _resolve_year_month(args, today)
        _dispatch_view(args.period, year, month, ref_date)
    elif args.command == "add":
        start = _parse_datetime(args.start, parser, "--start")
        end = _parse_datetime(args.end, parser, "--end")
        if end <= start:
            parser.error("--end must be after --start")
        event = Event(
            description=args.description,
            category=args.category,
            start=start,
            end=end,
        )
        add_event(event)
        print(f"Added: {args.description}")


if __name__ == "__main__":
    main()
