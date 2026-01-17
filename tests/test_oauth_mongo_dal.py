# coding=utf-8
"""
Unit tests for OauthMongoDAL class.
"""
from unittest.mock import MagicMock, patch

import pytest

from lib.api.mongodb import OauthMongoDAL


@pytest.fixture
def mock_oauth_dal():
    """Create an OauthMongoDAL instance with mocked MongoDB client."""
    with patch("lib.api.mongodb.MongoClient") as mock_client:
        mock_db = MagicMock()
        mock_client.return_value.events = mock_db

        dal = OauthMongoDAL()
        dal.mongodb = mock_client.return_value
        dal.database = mock_db
        yield dal


class TestGetWorkspace:
    """Tests for the get_workspace method."""

    def test_get_workspace_success(self, mock_oauth_dal):
        """Test successful workspace retrieval."""
        expected_workspace = {
            "team_id": "T123456",
            "bot_token": "xoxb-test-token",
            "app_id": "A123456",
        }
        mock_oauth_dal.database.slack_installations.find_one = MagicMock(
            return_value=expected_workspace
        )

        result = mock_oauth_dal.get_workspace("T123456")

        assert result == expected_workspace
        mock_oauth_dal.database.slack_installations.find_one.assert_called_once_with(
            {"team_id": "T123456"}
        )

    def test_get_workspace_not_found(self, mock_oauth_dal):
        """Test workspace retrieval when not found."""
        mock_oauth_dal.database.slack_installations.find_one = MagicMock(
            return_value=None
        )

        result = mock_oauth_dal.get_workspace("nonexistent_team")

        assert result is None

    def test_get_workspace_error(self, mock_oauth_dal):
        """Test workspace retrieval handles errors gracefully."""
        mock_oauth_dal.database.slack_installations.find_one = MagicMock(
            side_effect=Exception("Database error")
        )

        result = mock_oauth_dal.get_workspace("T123456")

        assert result is None
