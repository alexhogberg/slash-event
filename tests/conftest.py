# coding=utf-8
"""
Shared pytest fixtures and mocks for all tests.
"""
import os
from unittest.mock import MagicMock, patch

import pytest
from google.maps.places_v1.types import Place

from lib.models.event import Event
from lib.models.event_place import EventPlace


# Set up required environment variables for tests
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up required environment variables for all tests."""
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "test_api_key")
    monkeypatch.setenv("SLACK_AUTH_KEY", "test_auth_key")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-token")
    monkeypatch.setenv("SLACK_CHANNEL_NAME", "test-channel")
    monkeypatch.setenv("MONGO_DB_CONNECTION_STRING", "mongodb://localhost:27017")


@pytest.fixture
def mock_google_places():
    """Create a mock GooglePlaces instance."""
    with patch("lib.api.google_places.places_v1.PlacesClient") as mock_client:
        mock_client.return_value = MagicMock()
        from lib.api.google_places import GooglePlaces

        google_places = GooglePlaces()
        yield google_places


@pytest.fixture
def mock_google_places_class():
    """Patch the GooglePlaces class constructor to return a mock."""
    with patch("lib.api.google_places.GooglePlaces") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_slack_client():
    """Create a mock Slack WebClient."""
    with patch("lib.api.slack.WebClient") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_mongo_client():
    """Patch the MongoDB client."""
    with patch("lib.api.mongodb.MongoClient") as mock_client:
        mock_db = MagicMock()
        mock_client.return_value.events = mock_db
        yield mock_client


@pytest.fixture
def sample_place():
    """Create a sample Google Places Place object."""
    return Place(
        name="places/test_place_id",
        id="test_place_id",
        display_name={"text": "Test Restaurant", "language_code": "en"},
        formatted_address="123 Test St, Test City, TC 12345",
        rating=4.5,
        price_level=2,
        types=["restaurant", "bar"],
        website_uri="https://test-restaurant.com",
        google_maps_uri="https://maps.google.com/test",
        business_status=1,
        icon_mask_base_uri="https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png",
        current_opening_hours={
            "open_now": True,
            "weekday_descriptions": [
                "Monday: 9:00 AM – 10:00 PM",
                "Tuesday: 9:00 AM – 10:00 PM",
            ],
        },
    )


@pytest.fixture
def sample_event_place(sample_place):
    """Create a sample EventPlace object."""
    return EventPlace(sample_place)


@pytest.fixture
def sample_event(sample_event_place):
    """Create a sample Event object."""
    return Event(
        _id="test_event_id",
        team_id="test_team",
        date="2025-12-15",
        time="18:00",
        location=sample_event_place,
        description="Test event description",
        participants=["U12345", "U67890"],
        author="U12345",
    )


@pytest.fixture
def sample_event_dict():
    """Create a sample event as a dictionary."""
    return {
        "_id": "0123456789ab0123456789ab",
        "team_id": "test_team",
        "date": "2025-12-15",
        "time": "18:00",
        "location": {
            "name": "Test Restaurant",
            "address": "123 Test St",
            "rating": 4.5,
            "price_level": 2,
            "types": ["restaurant", "bar"],
            "place_id": "test_place_id",
            "website_uri": "https://test-restaurant.com",
            "business_status": 1,
            "google_maps_url": "https://maps.google.com/test",
        },
        "description": "Test event description",
        "participants": ["U12345", "U67890"],
        "author": "U12345",
    }


@pytest.fixture
def sample_places_list():
    """Create a list of sample places for testing."""
    return [
        Place(
            name="places/place_1",
            id="place_1",
            display_name={"text": "First Restaurant", "language_code": "en"},
            formatted_address="111 First St",
            rating=4.5,
            types=["restaurant"],
            current_opening_hours={
                "open_now": True,
                "weekday_descriptions": ["Monday: 9:00 AM – 10:00 PM"],
            },
        ),
        Place(
            name="places/place_2",
            id="place_2",
            display_name={"text": "Second Bar", "language_code": "en"},
            formatted_address="222 Second St",
            rating=4.0,
            types=["bar"],
            current_opening_hours={
                "open_now": True,
                "weekday_descriptions": ["Monday: 5:00 PM – 2:00 AM"],
            },
        ),
        Place(
            name="places/place_3",
            id="place_3",
            display_name={"text": "Third Cafe", "language_code": "en"},
            formatted_address="333 Third St",
            rating=3.5,
            types=["cafe"],
            current_opening_hours={
                "open_now": False,
                "weekday_descriptions": ["Monday: 7:00 AM – 5:00 PM"],
            },
        ),
    ]


@pytest.fixture
def mock_slack_payload():
    """Create a sample Slack interactive payload."""
    return {
        "type": "block_actions",
        "user": {"id": "U12345", "team_id": "T12345"},
        "container": {"channel_id": "C12345", "view_id": "V12345"},
        "actions": [{"action_id": "join_event", "value": "test_event_id"}],
        "view": {
            "state": {
                "values": {
                    "event_day": {
                        "event_day": {"type": "datepicker", "selected_date": "2025-12-15"}
                    },
                    "event_time": {
                        "event_time": {"type": "timepicker", "selected_time": "18:00"}
                    },
                    "suggest_place": {
                        "suggest_place": {
                            "type": "external_select",
                            "selected_option": {"value": "test_place_id"},
                        }
                    },
                }
            },
            "blocks": [{"block_id": "suggest_place|test_place_id"}],
            "callback_id": "create_event_dialog|",
        },
    }


@pytest.fixture
def mock_bolt_client():
    """Create a mock Slack Bolt client."""
    return MagicMock()


@pytest.fixture
def mock_say_func():
    """Create a mock say function."""
    return MagicMock()


@pytest.fixture
def mock_respond_func():
    """Create a mock respond function."""
    return MagicMock()
