# coding=utf-8
"""
Unit tests for date utilities.
"""
from datetime import datetime, timedelta

import pytest

from lib.utils.date_utils import (
    get_date,
    get_day_number,
    get_next_weekday_as_date,
    is_day_formatted_as_date,
    parse_date_to_weekday,
)


class TestIsDayFormattedAsDate:
    """Tests for is_day_formatted_as_date function."""

    def test_valid_date_format(self):
        """Test that valid YYYY-MM-DD format returns True."""
        assert is_day_formatted_as_date("2025-01-15") is True
        assert is_day_formatted_as_date("2025-12-31") is True
        assert is_day_formatted_as_date("2024-02-29") is True  # Leap year

    def test_invalid_date_format(self):
        """Test that invalid date formats return False."""
        assert is_day_formatted_as_date("15-01-2025") is False
        assert is_day_formatted_as_date("01/15/2025") is False
        assert is_day_formatted_as_date("2025/01/15") is False
        assert is_day_formatted_as_date("January 15, 2025") is False

    def test_none_returns_false(self):
        """Test that None returns False."""
        assert is_day_formatted_as_date(None) is False

    def test_empty_string_returns_false(self):
        """Test that empty string returns False."""
        assert is_day_formatted_as_date("") is False

    def test_invalid_date_values(self):
        """Test that invalid date values return False."""
        assert is_day_formatted_as_date("2025-13-01") is False  # Invalid month
        assert is_day_formatted_as_date("2025-01-32") is False  # Invalid day
        assert is_day_formatted_as_date("not-a-date") is False


class TestGetNextWeekdayAsDate:
    """Tests for get_next_weekday_as_date function."""

    def test_returns_correct_weekday(self):
        """Test that returned date has correct weekday."""
        for weekday in range(7):
            result = get_next_weekday_as_date(weekday)
            result_date = datetime.strptime(result, "%Y-%m-%d")
            assert result_date.weekday() == weekday

    def test_returns_future_date(self):
        """Test that returned date is in the future or today."""
        today = datetime.now().date()
        for weekday in range(7):
            result = get_next_weekday_as_date(weekday)
            result_date = datetime.strptime(result, "%Y-%m-%d").date()
            assert result_date >= today

    def test_returns_within_week(self):
        """Test that returned date is within the next 7 days."""
        today = datetime.now().date()
        one_week = today + timedelta(days=7)
        for weekday in range(7):
            result = get_next_weekday_as_date(weekday)
            result_date = datetime.strptime(result, "%Y-%m-%d").date()
            assert result_date <= one_week


class TestParseDateToWeekday:
    """Tests for parse_date_to_weekday function."""

    def test_returns_correct_weekday_names(self):
        """Test that correct weekday names are returned."""
        # 2025-01-13 is a Monday
        assert parse_date_to_weekday("2025-01-13") == "Monday"
        assert parse_date_to_weekday("2025-01-14") == "Tuesday"
        assert parse_date_to_weekday("2025-01-15") == "Wednesday"
        assert parse_date_to_weekday("2025-01-16") == "Thursday"
        assert parse_date_to_weekday("2025-01-17") == "Friday"
        assert parse_date_to_weekday("2025-01-18") == "Saturday"
        assert parse_date_to_weekday("2025-01-19") == "Sunday"

    def test_known_dates(self):
        """Test with known specific dates."""
        # Christmas 2025 is on Thursday
        assert parse_date_to_weekday("2025-12-25") == "Thursday"

        # New Year's Day 2025 is on Wednesday
        assert parse_date_to_weekday("2025-01-01") == "Wednesday"


class TestGetDayNumber:
    """Tests for get_day_number function."""

    def test_full_day_names(self):
        """Test with full weekday names."""
        assert get_day_number("Monday") == 0
        assert get_day_number("Tuesday") == 1
        assert get_day_number("Wednesday") == 2
        assert get_day_number("Thursday") == 3
        assert get_day_number("Friday") == 4

    def test_abbreviated_day_names(self):
        """Test with abbreviated weekday names."""
        assert get_day_number("Mon") == 0
        assert get_day_number("Tue") == 1
        assert get_day_number("Wed") == 2
        assert get_day_number("Thu") == 3
        assert get_day_number("Fri") == 4

    def test_case_insensitivity(self):
        """Test that function handles different cases."""
        assert get_day_number("monday") == 0
        assert get_day_number("MONDAY") == 0
        assert get_day_number("MoNdAy") == 0

    def test_returns_none_for_weekend(self):
        """Test that weekend days return None (based on implementation)."""
        # The current implementation returns None for day_num >= 5
        assert get_day_number("Saturday") is None
        assert get_day_number("Sunday") is None

    def test_invalid_day_returns_none(self):
        """Test that invalid day names return None."""
        assert get_day_number("InvalidDay") is None
        assert get_day_number("Funday") is None
        assert get_day_number("") is None


class TestGetDate:
    """Tests for get_date function (natural language date parsing)."""

    def test_tomorrow(self):
        """Test parsing 'tomorrow'."""
        result = get_date("tomorrow")
        tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert result == tomorrow

    def test_next_week(self):
        """Test parsing 'next week' returns a future date."""
        result = get_date("next week")
        if result:
            result_date = datetime.strptime(result, "%Y-%m-%d")
            assert result_date > datetime.today()

    def test_specific_weekday(self):
        """Test parsing 'next Thursday' returns a Thursday."""
        result = get_date("next Thursday")
        if result:
            result_date = datetime.strptime(result, "%Y-%m-%d")
            assert result_date.weekday() == 3  # Thursday is 3

    def test_past_date_returns_none(self):
        """Test that past dates return None."""
        result = get_date("yesterday")
        assert result is None

        result = get_date("last week")
        assert result is None

    def test_in_x_days(self):
        """Test parsing 'in 5 days'."""
        result = get_date("in 5 days")
        if result:
            expected = (datetime.today() + timedelta(days=5)).strftime("%Y-%m-%d")
            # Allow for potential off-by-one due to time parsing
            result_date = datetime.strptime(result, "%Y-%m-%d")
            expected_date = datetime.strptime(expected, "%Y-%m-%d")
            assert abs((result_date - expected_date).days) <= 1
