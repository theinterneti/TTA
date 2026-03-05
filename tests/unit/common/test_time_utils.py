"""
Unit tests for src/common/time_utils.py.

Tests cover:
- consecutive_streak_ending_today: empty, single, consecutive, gap, duplicates
- pick_reference_today: both in set, only utc, only local, neither, empty
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from src.common.time_utils import consecutive_streak_ending_today, pick_reference_today


# ---------------------------------------------------------------------------
# consecutive_streak_ending_today
# ---------------------------------------------------------------------------


class TestConsecutiveStreakEndingToday:
    def test_empty_returns_zero(self):
        assert consecutive_streak_ending_today([]) == 0

    def test_single_date_matching_today(self):
        today = date.today()
        assert consecutive_streak_ending_today([today], ref_today=today) == 1

    def test_single_date_not_today(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        # ref_today=today but only yesterday in list → streak is 0
        assert consecutive_streak_ending_today([yesterday], ref_today=today) == 0

    def test_consecutive_three_days(self):
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(3)]
        assert consecutive_streak_ending_today(dates, ref_today=today) == 3

    def test_gap_breaks_streak(self):
        today = date.today()
        # today and 2 days ago — missing yesterday
        dates = [today, today - timedelta(days=2)]
        assert consecutive_streak_ending_today(dates, ref_today=today) == 1

    def test_duplicates_are_ignored(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        dates = [today, today, yesterday, yesterday]
        assert consecutive_streak_ending_today(dates, ref_today=today) == 2

    def test_longer_streak_with_gap_at_end(self):
        today = date.today()
        # 5-day run ending yesterday; today is missing
        dates = [today - timedelta(days=i) for i in range(1, 6)]
        # streak ending AT today is 0 because today not present
        assert consecutive_streak_ending_today(dates, ref_today=today) == 0

    def test_five_consecutive_days(self):
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(5)]
        assert consecutive_streak_ending_today(dates, ref_today=today) == 5


# ---------------------------------------------------------------------------
# pick_reference_today
# ---------------------------------------------------------------------------


class TestPickReferenceToday:
    def test_returns_utc_when_only_utc_in_candidates(self):
        from datetime import datetime

        utc = datetime.utcnow().date()
        result = pick_reference_today([utc])
        assert result == utc

    def test_fallback_to_most_recent_when_neither_today_in_set(self):
        past1 = date(2023, 1, 10)
        past2 = date(2023, 1, 5)
        result = pick_reference_today([past1, past2])
        assert result == past1  # most recent

    def test_empty_candidates_returns_utc_today(self):
        from datetime import datetime

        utc = datetime.utcnow().date()
        result = pick_reference_today([])
        assert result == utc

    def test_returns_max_when_both_local_and_utc_present(self):
        from datetime import datetime

        utc = datetime.utcnow().date()
        local = datetime.now().date()
        # Both present → should return max(local, utc)
        result = pick_reference_today([utc, local])
        assert result == max(utc, local)
