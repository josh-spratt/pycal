"""
PyCal - View and manage calendar from the command line.

Usage examples:
  pycal view                    # current month
  pycal view month              # current month
  pycal view month --year 2024 --month 6
  pycal view day                # today
  pycal view day --date 2024-07-04
  pycal view week
  pycal view week --date 2024-01-15
  pycal view quarter
  pycal view year
  pycal view --help             # view subcommand options
  pycal --help                  # all commands
"""
import argparse
import calendar
from datetime import datetime, timedelta


def render_month(year: int, month: int):
    """Render the current month grid in a readable format."""
    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)

    today = datetime.today()
    is_current_month = today.year == year and today.month == month

    month_name = calendar.month_name[month]
    # Header: centered month and year
    header = f"{month_name} {year}"
    print(header.center(20))
    print("Su Mo Tu We Th Fr Sa")

    for week in weeks:
        print(_format_week_row(week, today, is_current_month))


def _format_week_row(week: list[int], today: datetime, is_current_month: bool) -> str:
    """Turn one week of day numbers into a single printable line (e.g. ' 1  2  3  4  5  6  7').

    Each week has 7 values: real days (1-31) or 0 for empty slots at the start/end
    of the month so the grid stays aligned. We format each as a 2-char cell and
    optionally highlight today with reverse video.
    """
    parts = []
    for day in week:
        if day == 0:
            # Empty slot (previous/next month); keep column width with spaces
            parts.append("  ")
        else:
            cell = f"{day:2}"
            if is_current_month and day == today.day:
                cell = f"\033[7m{day:2}\033[0m"  # reverse video so today stands out
            parts.append(cell)
    return " ".join(parts)


def render_day(date: datetime) -> None:
    """Render a single day (date header; minimal placeholder for events)."""
    weekday = calendar.day_name[date.weekday()]
    month_name = calendar.month_name[date.month]
    header = f"{weekday}, {month_name} {date.day}, {date.year}"
    print(header)
    print("-" * len(header))


def render_week(year: int, month: int, week_start: datetime) -> None:
    """Render one week: header plus a line of dates (Su–Sa)."""
    end = week_start + timedelta(days=6)
    print(f"Week of {calendar.month_abbr[week_start.month]} {week_start.day} – {calendar.month_abbr[end.month]} {end.day}, {year}")
    print("Su Mo Tu We Th Fr Sa")
    parts = []
    for i in range(7):
        d = week_start + timedelta(days=i)
        parts.append(f"{d.day:2}")
    print(" ".join(parts))


def render_quarter(year: int, quarter: int) -> None:
    """Render a quarter as three month names (Q1=Jan–Mar, etc.)."""
    start_month = (quarter - 1) * 3 + 1
    months = [calendar.month_name[start_month + i] for i in range(3)]
    print(f"Q{quarter} {year}: {', '.join(months)}")


def render_year(year: int) -> None:
    """Render a year as 12 month names."""
    print(str(year).center(24))
    print()
    months = [calendar.month_abbr[m] for m in range(1, 13)]
    print(" ".join(months))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pycal", description="View and manage calendar from the command line.")
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
    view_parser.add_argument("--date", type=str, default=None, help="date for day/week (YYYY-MM-DD; default: today)")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command != "view":
        return

    now = datetime.today()
    year = args.year if args.year is not None else now.year
    month = args.month if args.month is not None else now.month

    if args.date is not None:
        try:
            ref_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            parser.error(f"invalid --date '{args.date}'; use YYYY-MM-DD")
    else:
        ref_date = now

    if args.period == "day":
        render_day(ref_date)
    elif args.period == "week":
        # week containing ref_date, Sunday start (weekday 6)
        days_back = (ref_date.weekday() + 1) % 7
        start = ref_date - timedelta(days=days_back)
        render_week(start.year, start.month, start)
    elif args.period == "month":
        render_month(year, month)
    elif args.period == "quarter":
        quarter = (month - 1) // 3 + 1
        render_quarter(year, quarter)
    elif args.period == "year":
        render_year(year)


if __name__ == "__main__":
    main()
