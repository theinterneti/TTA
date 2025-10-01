"""
Time/date utility helpers to centralize timezone-agnostic date calculations.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime, timedelta


def utc_today() -> date:
    """Return today's date in UTC."""
    return datetime.utcnow().date()


def pick_reference_today(candidates: Iterable[date]) -> date:
    """Choose the most appropriate "today" reference aligned with available activity.
    Preference order:
      1) The newer of local today vs UTC today, if either appears in candidates
      2) UTC today if present
      3) Local today if present
      4) The most recent date in candidates
    Fallback: UTC today.
    """
    cset = set(candidates)
    local = datetime.now().date()
    utc = datetime.utcnow().date()
    if local in cset and utc in cset:
        return max(local, utc)
    if utc in cset:
        return utc
    if local in cset:
        return local
    return max(cset) if cset else utc


def consecutive_streak_ending_today(
    dates: Iterable[date], ref_today: date | None = None
) -> int:
    """Compute a consecutive-day streak ending at ref_today.
    Dates are treated as calendar dates (no times). Duplicates are ignored.
    """
    if not dates:
        return 0
    unique = sorted(set(dates), reverse=True)
    today = ref_today or pick_reference_today(unique)
    streak = 0
    for i, d in enumerate(unique):
        if d == today - timedelta(days=i):
            streak += 1
        else:
            break
    return streak
