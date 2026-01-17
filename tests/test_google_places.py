# coding=utf-8
"""
Unit tests for GooglePlaces API integration with mocks.
These tests mock the Google Places API to avoid making real API calls.
"""
from unittest.mock import MagicMock, patch

import pytest
from google.maps.places_v1.types import Place

from lib.api.google_places import GooglePlaces


@pytest.fixture
def google_places():
    """Create a GooglePlaces instance with mocked client."""
    with patch("lib.api.google_places.places_v1.PlacesClient") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        gp = GooglePlaces()
        gp._mock_client = mock_instance
        yield gp


class TestGetSuggestions:
    """Tests for the get_suggestions method."""

    def test_get_suggestions_returns_places(self, google_places):
        """Test that get_suggestions returns places from the API."""
        mock_places = [
            Place(
                name="places/place1",
                id="place1",
                display_name={"text": "Restaurant 1"},
                formatted_address="123 Test St",
                rating=4.5,
                types=["restaurant"],
            ),
            Place(
                name="places/place2",
                id="place2",
                display_name={"text": "Restaurant 2"},
                formatted_address="456 Test Ave",
                rating=4.0,
                types=["restaurant"],
            ),
        ]

        mock_response = MagicMock()
        mock_response.places = mock_places
        google_places.gMaps.search_text.return_value = mock_response

        result = google_places.get_suggestions("restaurants near me")

        assert len(result) == 2
        assert result[0].display_name.text == "Restaurant 1"
        assert result[1].display_name.text == "Restaurant 2"
        google_places.gMaps.search_text.assert_called_once()

    def test_get_suggestions_returns_empty_on_no_results(self, google_places):
        """Test that get_suggestions returns empty list when no places found."""
        google_places.gMaps.search_text.return_value = None

        result = google_places.get_suggestions("nonexistent location xyz123")

        assert result == []

    def test_get_suggestions_with_empty_response(self, google_places):
        """Test that get_suggestions handles empty response correctly."""
        mock_response = MagicMock()
        mock_response.places = []
        google_places.gMaps.search_text.return_value = mock_response

        result = google_places.get_suggestions("test area")

        assert result == []


class TestGetPlaceInformation:
    """Tests for the get_place_information method."""

    def test_get_place_information_success(self, google_places):
        """Test successful place information retrieval."""
        mock_place = Place(
            name="places/test_place_id",
            id="test_place_id",
            display_name={"text": "Test Restaurant"},
            formatted_address="123 Test St",
            rating=4.5,
            types=["restaurant"],
        )
        google_places.gMaps.get_place.return_value = mock_place

        result = google_places.get_place_information("test_place_id")

        assert result.display_name.text == "Test Restaurant"
        google_places.gMaps.get_place.assert_called_once()


class TestGetPlaceSuggestions:
    """Tests for the get_place_suggestions method."""

    def test_get_place_suggestions_formats_correctly(self, google_places):
        """Test that place suggestions are formatted correctly for Slack."""
        mock_places = [
            Place(
                name="places/place1",
                id="place1",
                display_name={"text": "Café One"},
                formatted_address="100 Main St",
            ),
            Place(
                name="places/place2",
                id="place2",
                display_name={"text": "Café Two"},
                formatted_address="200 Side St",
            ),
        ]

        mock_response = MagicMock()
        mock_response.places = mock_places
        google_places.gMaps.search_text.return_value = mock_response

        result = google_places.get_place_suggestions("café")

        assert len(result) == 2
        assert result[0]["text"]["text"] == "Café One"
        assert result[0]["text"]["type"] == "plain_text"
        assert result[0]["description"]["text"] == "100 Main St"
        assert result[0]["value"] == "place1"

    def test_get_place_suggestions_returns_empty_list(self, google_places):
        """Test that empty search returns empty list."""
        mock_response = MagicMock()
        mock_response.places = []
        google_places.gMaps.search_text.return_value = mock_response

        result = google_places.get_place_suggestions("xyz123nonexistent")

        assert result == []


class TestFormatPlace:
    """Tests for the format_place method."""

    def test_format_place_returns_dict(self, google_places):
        """Test that format_place returns properly formatted dictionary."""
        mock_place = Place(
            name="places/test_id",
            id="test_id",
            display_name={"text": "Test Place"},
            formatted_address="123 Test St",
            price_level=2,
            rating=4.5,
            types=["restaurant", "bar"],
            website_uri="https://test.com",
            business_status=1,
            google_maps_uri="https://maps.google.com/test",
        )

        result = google_places.format_place(mock_place)

        assert result["name"] == "Test Place"
        assert result["address"] == "123 Test St"
        assert result["price_level"] == 2
        assert result["rating"] == 4.5
        assert result["types"] == ["restaurant", "bar"]
        assert result["place_id"] == "test_id"
        assert result["website_uri"] == "https://test.com"
        assert result["business_status"] == 1
        assert result["google_maps_url"] == "https://maps.google.com/test"

    def test_format_place_handles_minimal_data(self, google_places):
        """Test that format_place handles places with minimal data."""
        mock_place = Place(
            name="places/minimal",
            id="minimal",
            display_name={"text": "Minimal Place"},
        )

        result = google_places.format_place(mock_place)

        assert result["name"] == "Minimal Place"
        assert result["place_id"] == "minimal"
