# coding=utf-8
"""
Unit tests for the Event model.
"""
import pytest
from unittest.mock import MagicMock

from lib.models.event import Event


class TestEventInitialization:
    """Tests for Event object initialization."""

    def test_event_init_with_all_params(self):
        """Test Event initialization with all parameters."""
        event = Event(
            _id="test_id",
            team_id="team123",
            date="2025-12-15",
            time="18:00",
            location={"name": "Test Place"},
            description="Test Description",
            participants=["U123", "U456"],
            author="U123",
        )

        assert event._id == "test_id"
        assert event.team_id == "team123"
        assert event.date == "2025-12-15"
        assert event.time == "18:00"
        assert event.location == {"name": "Test Place"}
        assert event.description == "Test Description"
        assert event.participants == ["U123", "U456"]
        assert event.author == "U123"

    def test_event_init_with_minimal_params(self):
        """Test Event initialization with minimal required parameters."""
        event = Event(
            _id=None,
            team_id="team123",
            date="2025-12-15",
            time="18:00",
            location={"name": "Minimal Place"},
        )

        assert event._id is None
        assert event.team_id == "team123"
        assert event.date == "2025-12-15"
        assert event.time == "18:00"
        assert event.location == {"name": "Minimal Place"}
        assert event.description is None
        assert event.participants == []
        assert event.author is None

    def test_event_init_with_none_participants(self):
        """Test that None participants gets converted to empty list."""
        event = Event(
            _id="test_id",
            team_id="team123",
            date="2025-12-15",
            time="18:00",
            location={"name": "Test Place"},
            participants=None,
        )

        assert event.participants == []


class TestEventStr:
    """Tests for Event string representation."""

    def test_str_representation(self):
        """Test __str__ method returns expected format."""
        event = Event(
            _id="test_id",
            team_id="team123",
            date="2025-12-15",
            time="18:00",
            location={"name": "Test Place"},
            description="Test Description",
            participants=["U123"],
            author="U123",
        )

        result = str(event)

        assert "test_id" in result
        assert "2025-12-15" in result
        assert "18:00" in result
        assert "Test Place" in result
        assert "Test Description" in result


class TestEventToDict:
    """Tests for Event to_dict method."""

    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all expected fields."""
        event = Event(
            _id="test_id",
            team_id="team123",
            date="2025-12-15",
            time="18:00",
            location={"name": "Test Place"},
            description="Test Description",
            participants=["U123", "U456"],
            author="U123",
        )

        result = event.to_dict()

        assert result["date"] == "2025-12-15"
        assert result["time"] == "18:00"
        assert result["team_id"] == "team123"
        assert result["location"] == {"name": "Test Place"}
        assert result["description"] == "Test Description"
        assert result["participants"] == ["U123", "U456"]
        assert result["author"] == "U123"
        # Note: _id is not included in to_dict
        assert "_id" not in result

    def test_to_dict_with_empty_participants(self):
        """Test to_dict with empty participants list."""
        event = Event(
            _id=None,
            team_id="team123",
            date="2025-12-15",
            time="18:00",
            location={"name": "Test Place"},
        )

        result = event.to_dict()

        assert result["participants"] == []


class TestEventFromDict:
    """Tests for Event from_dict class method."""

    def test_from_dict_creates_event(self):
        """Test that from_dict creates an Event object correctly."""
        data = {
            "id": "test_id",
            "team_id": "team123",
            "date": "2025-12-15",
            "time": "18:00",
            "location": {"name": "Test Place"},
            "description": "Test Description",
            "participants": ["U123", "U456"],
            "author": "U123",
        }

        event = Event.from_dict(data)

        assert event._id == "test_id"
        assert event.team_id == "team123"
        assert event.date == "2025-12-15"
        assert event.time == "18:00"
        assert event.location == {"name": "Test Place"}
        assert event.description == "Test Description"
        assert event.participants == ["U123", "U456"]
        assert event.author == "U123"

    def test_from_dict_with_missing_fields(self):
        """Test from_dict handles missing optional fields."""
        data = {
            "team_id": "team123",
            "date": "2025-12-15",
            "time": "18:00",
            "location": {"name": "Test Place"},
        }

        event = Event.from_dict(data)

        assert event._id is None
        assert event.description is None
        # Note: from_dict returns None for missing participants, but __init__ converts it to []
        assert event.participants == []
        assert event.author is None


class TestEventWithEventPlace:
    """Tests for Event with EventPlace location."""

    def test_event_with_event_place_location(self, sample_event_place):
        """Test Event with EventPlace as location."""
        event = Event(
            _id="test_id",
            team_id="team123",
            date="2025-12-15",
            time="18:00",
            location=sample_event_place,
            author="U123",
        )

        assert event.location == sample_event_place
        # Access EventPlace methods through location
        assert event.location.name() == "Test Restaurant"
