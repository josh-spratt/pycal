"""
Calendar and display configuration. Configurable data at a high level.
"""

# Week layout: 0=Monday .. 6=Sunday (calendar module convention)
FIRST_WEEKDAY_SUNDAY = 6
DAYS_PER_WEEK = 7
MONTHS_PER_QUARTER = 3

# Display
MONTH_HEADER_WIDTH = 20
YEAR_HEADER_WIDTH = 24
DAY_CELL_WIDTH = 2
WEEKDAY_HEADER = "Su Mo Tu We Th Fr Sa"

# Date parsing
DATE_FORMAT = "%Y-%m-%d"
# Event timestamps: ISO-like for scriptability (e.g. 2025-02-24T09:00)
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

# ANSI: reverse video for highlighting today
ANSI_REVERSE_START = "\033[7m"
ANSI_REVERSE_END = "\033[0m"
