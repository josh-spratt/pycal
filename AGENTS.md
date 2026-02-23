# PyCal – Agent Context

## Project overview

**PyCal** is a Python CLI for interacting with your calendar. It runs in the terminal and lets users view and manage calendar data from the command line.

## Tech stack

- **Language**: Python 3
- **Scope**: Prefer standard library where possible (e.g. `calendar`, `datetime`). Add external dependencies only when needed (e.g. for real calendar backends or richer CLI UX).
- **Interface**: Command-line; suitable for use with subcommands (e.g. `pycal view`, `pycal add`, `pycal list`).

## Current state

- **Entrypoint**: `main.py` — defines `main()` and calls `render_month(year, month)` for the current month.
- **Rendering**: `render_month()` is started but not finished: it uses `calendar.Calendar(firstweekday=6)` (week starts Sunday), gets weeks via `monthdayscalendar`, and has access to `month_name` / `month_abbr` and a `is_current_month` flag. No terminal output or formatting is implemented yet.
- **Dependencies**: None beyond the standard library.

## Conventions and constraints

- Keep the CLI fast and scriptable; avoid interactive prompts unless explicitly required.
- Prefer small, testable functions and clear separation between calendar logic and display/CLI.
- Use type hints for public functions and API boundaries.
- When adding features (e.g. event add/list, different views), consider subcommands and a single entrypoint in `main.py`.

## Suggested directions (for future work)

- Complete `render_month()` so it prints a readable month grid (e.g. 7-column week layout, optional day-of-week headers).
- Add argument parsing (e.g. `argparse` or `click`) for month/year and subcommands.
- Optionally integrate a real calendar (e.g. local `.ics`, Google Calendar, or system calendar) for viewing and editing events.
