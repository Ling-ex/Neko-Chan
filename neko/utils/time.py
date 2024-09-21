import re
import time
from datetime import datetime
from datetime import timedelta
from typing import Optional


def usec() -> int:
    """Returns the current time in microseconds since the Unix epoch."""

    return int(time.time() * 1000000)


def msec() -> int:
    """Returns the current time in milliseconds since the Unix epoch."""

    return int(usec() / 1000)


def sec() -> int:
    """Returns the current time in seconds since the Unix epoch."""

    return int(time.time())


def format_duration_us(t_us: int | float) -> str:
    """Formats the given microsecond duration as a string."""

    t_us = int(t_us)

    t_ms = t_us / 1000
    t_s = t_ms / 1000
    t_m = t_s / 60
    t_h = t_m / 60
    t_d = t_h / 24

    if t_d >= 1:
        rem_h = t_h % 24
        return '%dd, %dh' % (t_d, rem_h)  # skipcq: PYL-C0209

    if t_h >= 1:
        rem_m = t_m % 60
        return '%dh, %dm' % (t_h, rem_m)  # skipcq: PYL-C0209

    if t_m >= 1:
        rem_s = t_s % 60
        return '%dm, %ds' % (t_m, rem_s)  # skipcq: PYL-C0209

    if t_s >= 1:
        return '%d sec' % t_s  # skipcq: PYL-C0209

    if t_ms >= 1:
        return '%d ms' % t_ms  # skipcq: PYL-C0209

    return '%d μs' % t_us  # skipcq: PYL-C0209


def format_datetime(text: str) -> Optional[datetime]:
    """
    Calculates a future datetime based on time deltas
    specified in the input text.

    Parameters:
        text (str): A string containing time deltas in the format '',
                    where  can be 'd' (days), 'h' (hours), 'm' (minutes),
                    or 's' (seconds).

    Returns:
        datetime: A datetime object representing the current time
                  plus the specified time deltas.
                  Returns None if no valid matches are found.
    """

    if matches := re.findall(r'([0-9]+)([dhms])', text.lower()):
        now = datetime.now()
        total_delta = timedelta()

        for number, unit in matches:
            number = int(number)
            if unit == 'd':
                total_delta += timedelta(days=number)
            elif unit == 'h':
                total_delta += timedelta(hours=number)
            elif unit == 'm':
                total_delta += timedelta(minutes=number)
            elif unit == 's':
                total_delta += timedelta(seconds=number)

        future_time = now + total_delta
        return future_time

    else:
        return None


def format_duration_td(value: timedelta, precision: int = 0) -> str:
    """
    Formats a timedelta object into a human-readable string with specified precision.

    Args:
        value (timedelta): The duration to format.
        precision (int): The number of time units to include.

    Returns:
        str: A string representation of the duration.
    """  # noqa: E501
    pieces = []

    if value.days:
        pieces.append(f'{value.days}d')

    seconds = value.seconds

    if seconds >= 3600:
        hours = int(seconds / 3600)
        pieces.append(f'{hours}h')
        seconds -= hours * 3600

    if seconds >= 60:
        minutes = int(seconds / 60)
        pieces.append(f'{minutes}m')
        seconds -= minutes * 60

    if seconds > 0 or not pieces:
        pieces.append(f'{seconds}s')

    if precision == 0:
        return ''.join(pieces)

    return ''.join(pieces[:precision])


def time_since_last_seen(last_seen_time) -> str:
    """
    Calculates the time since a given datetime and formats it as a human-readable string.

    Args:
        last_seen_time (datetime): The past datetime to calculate from.

    Returns:
        str: A string indicating the time elapsed since last_seen_time.
    """  # noqa: E501
    now = datetime.now()
    time = now - last_seen_time

    seconds = time.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} second{'s' if seconds != 1 else ''} ago"

    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"

    else:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"


start_time = usec()
