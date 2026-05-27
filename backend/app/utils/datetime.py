"""UTC datetime utilities."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def utc_from_timestamp(ts: float) -> datetime:
    """Convert a UNIX timestamp to a timezone-aware UTC datetime.

    Args:
        ts: Unix timestamp (seconds since epoch).

    Returns:
        Timezone-aware datetime in UTC.
    """
    return datetime.fromtimestamp(ts, tz=timezone.utc)
