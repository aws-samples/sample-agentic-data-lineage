"""
Time-related tools - Provide accurate time judgment capabilities for Agents
"""

from datetime import UTC, datetime, timedelta

import pytz
from strands import tool


@tool
def get_current_time(timezone_name: str = "UTC") -> str:
    """
    Get current time

    Args:
        timezone_name: Timezone name, such as 'UTC', 'Asia/Shanghai', 'America/New_York', etc.

    Returns:
        Formatted current time string
    """
    try:
        tz = pytz.timezone(timezone_name)
        current_time = datetime.now(tz)
        return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        # If timezone is invalid, return UTC time
        current_time = datetime.now(UTC)
        return f"{current_time.strftime('%Y-%m-%d %H:%M:%S UTC')} (Note: timezone '{timezone_name}' is invalid, returning UTC time)"


@tool
def get_current_timestamp() -> int:
    """
    Get current Unix timestamp

    Returns:
        Current Unix timestamp (seconds)
    """
    return int(datetime.now(UTC).timestamp())


@tool
def format_timestamp(
    timestamp: int, timezone_name: str = "UTC", format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format Unix timestamp to readable time

    Args:
        timestamp: Unix timestamp (seconds)
        timezone_name: Target timezone
        format_str: Time format string

    Returns:
        Formatted time string
    """
    try:
        tz = pytz.timezone(timezone_name)
        dt = datetime.fromtimestamp(timestamp, tz)
        return dt.strftime(f"{format_str} %Z")
    except Exception as e:
        return f"Timestamp formatting failed: {str(e)}"


@tool
def time_difference(time1: str, time2: str, unit: str = "hours") -> str:
    """
    Calculate the difference between two times

    Args:
        time1: First time (ISO format or common format)
        time2: Second time (ISO format or common format)
        unit: Return unit ('seconds', 'minutes', 'hours', 'days')

    Returns:
        Time difference description
    """
    try:
        # Try to parse time strings
        def parse_time(time_str):
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Unable to parse time format: {time_str}")

        dt1 = parse_time(time1)
        dt2 = parse_time(time2)
        diff = abs((dt2 - dt1).total_seconds())

        if unit == "seconds":
            return f"{diff:.0f} seconds"
        elif unit == "minutes":
            return f"{diff / 60:.1f} minutes"
        elif unit == "hours":
            return f"{diff / 3600:.1f} hours"
        elif unit == "days":
            return f"{diff / 86400:.1f} days"
        else:
            return f"{diff:.0f} seconds (unknown unit: {unit})"

    except Exception as e:
        return f"Time difference calculation failed: {str(e)}"


@tool
def is_time_before(time1: str, time2: str) -> str:
    """
    Determine if time1 is before time2

    Args:
        time1: First time
        time2: Second time

    Returns:
        Comparison result description
    """
    try:

        def parse_time(time_str):
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Unable to parse time format: {time_str}")

        dt1 = parse_time(time1)
        dt2 = parse_time(time2)

        if dt1 < dt2:
            return f"Yes, {time1} is before {time2}"
        elif dt1 > dt2:
            return f"No, {time1} is after {time2}"
        else:
            return f"{time1} and {time2} are the same time"

    except Exception as e:
        return f"Time comparison failed: {str(e)}"


@tool
def get_time_ago(hours: int = 0, days: int = 0, minutes: int = 0) -> str:
    """
    Get a time point specified time ago

    Args:
        hours: Number of hours
        days: Number of days
        minutes: Number of minutes

    Returns:
        Past time point string
    """
    try:
        now = datetime.now(UTC)
        past_time = now - timedelta(days=days, hours=hours, minutes=minutes)
        return past_time.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception as e:
        return f"Failed to calculate past time: {str(e)}"


@tool
def is_recent(timestamp_str: str, threshold_hours: int = 24) -> str:
    """
    Determine if the given time is within the recent specified hours

    Args:
        timestamp_str: Time string
        threshold_hours: Threshold hours

    Returns:
        Judgment result description
    """
    try:

        def parse_time(time_str):
            # Try to remove timezone identifiers before parsing
            time_str_clean = (
                time_str.replace(" UTC", "")
                .replace(" CST", "")
                .replace(" EST", "")
                .replace(" PST", "")
            )

            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(time_str_clean, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Unable to parse time format: {time_str}")

        target_time = parse_time(timestamp_str)
        now = datetime.now(UTC)

        # If target time has no timezone info, assume UTC
        if target_time.tzinfo is None:
            target_time = target_time.replace(tzinfo=UTC)

        time_diff = (now - target_time).total_seconds() / 3600  # Convert to hours

        if time_diff < 0:
            return f"Time {timestamp_str} is in the future, {abs(time_diff):.1f} hours from now"
        elif time_diff <= threshold_hours:
            return f"Yes, time {timestamp_str} is within the recent {threshold_hours} hours ({time_diff:.1f} hours ago)"
        else:
            return f"No, time {timestamp_str} is not within the recent {threshold_hours} hours ({time_diff:.1f} hours ago)"

    except Exception as e:
        return f"Time judgment failed: {str(e)}"


# Export all time tools
TIME_TOOLS = [
    get_current_time,
    get_current_timestamp,
    format_timestamp,
    time_difference,
    is_time_before,
    get_time_ago,
    is_recent,
]
