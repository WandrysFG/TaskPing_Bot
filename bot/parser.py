"""
Parser module
-------------
Interprets the day and time typed by the user, based on the system's
real calendar.
"""

from datetime import datetime, timedelta, date

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_day(text: str):
    """Converts 'today', 'tomorrow', a weekday name, or a dd/mm/yy date into a date object."""
    text = text.lower().strip()
    today = date.today()  # <- system's real calendar

    if text == "today":
        return today

    if text == "tomorrow":
        return today + timedelta(days=1)

    if text in WEEKDAYS:
        target = WEEKDAYS[text]
        diff = (target - today.weekday()) % 7
        if diff == 0:
            diff = 7  # same weekday as today -> schedule for the NEXT one
        return today + timedelta(days=diff)

    for fmt in ("%d/%m/%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None


def parse_time(text: str):
    """Converts 'HH:MM' into (hour, minute). Returns None if the format is invalid."""
    try:
        h_str, m_str = text.split(":")
        h, m = int(h_str), int(m_str)
        if 0 <= h <= 23 and 0 <= m <= 59:
            return h, m
    except (ValueError, AttributeError):
        pass
    return None
