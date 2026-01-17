# coding=utf-8
"""
Unit tests for Slack API integration with mocks.
"""
from unittest.mock import MagicMock, patch

import pytest
from slack_sdk.errors import SlackApiError

from lib.api.slack import Slack


@pytest.fixture
def mock_slack():
    """Create a Slack instance with mocked dependencies."""
    with patch("lib.api.slack.WebClient") as mock_client, patch(
        "lib.api.slack.OauthMongoDAL"
    ) as mock_oauth:
        mock_web_client = MagicMock()
        mock_client.return_value = mock_web_client

        mock_oauth_instance = MagicMock()
        mock_oauth.return_value = mock_oauth_instance

        slack = Slack(team_id="test_team")
        slack._mock_client = mock_web_client
        yield slack


class TestPrivateSlackText:
    """Tests for the private_slack_text static method."""

    def test_private_slack_text_returns_dict(self):
        """Test that private_slack_text returns correct format."""
        result = Slack.private_slack_text("Hello, World!")

        assert result == {"text": "Hello, World!"}

    def test_private_slack_text_empty_string(self):
        """Test that private_slack_text handles empty string."""
        result = Slack.private_slack_text("")

        assert result == {"text": ""}


class TestGetChannelId:
    """Tests for the get_channel_id method."""

    def test_get_channel_id_success(self, mock_slack, monkeypatch):
        """Test successful channel ID retrieval."""
        monkeypatch.setenv("SLACK_CHANNEL_NAME", "test-channel")

        mock_response = {
            "channels": [
                {"name": "general", "id": "C111111"},
                {"name": "test-channel", "id": "C222222"},
                {"name": "random", "id": "C333333"},
            ]
        }
        mock_slack.client.conversations_list.return_value = mock_response

        result = mock_slack.get_channel_id()

        assert result == "C222222"
        mock_slack.client.conversations_list.assert_called_once()

    def test_get_channel_id_not_found(self, mock_slack, monkeypatch):
        """Test channel ID retrieval when channel not found."""
        monkeypatch.setenv("SLACK_CHANNEL_NAME", "nonexistent-channel")

        mock_response = {
            "channels": [
                {"name": "general", "id": "C111111"},
                {"name": "random", "id": "C333333"},
            ]
        }
        mock_slack.client.conversations_list.return_value = mock_response

        result = mock_slack.get_channel_id()

        assert result is None

    def test_get_channel_id_api_error(self, mock_slack, monkeypatch):
        """Test channel ID retrieval handles API errors."""
        monkeypatch.setenv("SLACK_CHANNEL_NAME", "test-channel")

        mock_slack.client.conversations_list.side_effect = SlackApiError(
            message="API Error", response={"error": "invalid_auth"}
        )

        with pytest.raises(SlackApiError):
            mock_slack.get_channel_id()


class TestSendPublicMessage:
    """Tests for the send_public_message method."""

    def test_send_public_message_success(self, mock_slack, monkeypatch):
        """Test successful public message sending."""
        monkeypatch.setenv("SLACK_CHANNEL_NAME", "test-channel")

        mock_slack.client.conversations_list.return_value = {
            "channels": [{"name": "test-channel", "id": "C123456"}]
        }

        mock_slack.send_public_message(
            text="Hello, World!",
            username="TestBot",
            attachments=[{"text": "Attachment"}],
        )

        mock_slack.client.chat_postMessage.assert_called_once_with(
            channel="C123456",
            text="Hello, World!",
            username="TestBot",
            attachments=[{"text": "Attachment"}],
        )

    def test_send_public_message_no_channel(self, mock_slack, monkeypatch):
        """Test that message is not sent when channel not found."""
        monkeypatch.setenv("SLACK_CHANNEL_NAME", "nonexistent")

        mock_slack.client.conversations_list.return_value = {"channels": []}

        # Should not raise, but also should not send message
        mock_slack.send_public_message(text="Hello", username="Bot")

        mock_slack.client.chat_postMessage.assert_not_called()

    def test_send_public_message_api_error(self, mock_slack, monkeypatch):
        """Test that API errors are raised properly."""
        monkeypatch.setenv("SLACK_CHANNEL_NAME", "test-channel")

        mock_slack.client.conversations_list.return_value = {
            "channels": [{"name": "test-channel", "id": "C123456"}]
        }
        mock_slack.client.chat_postMessage.side_effect = SlackApiError(
            message="API Error", response={"error": "channel_not_found"}
        )

        with pytest.raises(SlackApiError):
            mock_slack.send_public_message(text="Hello", username="Bot")


class TestUpdateChatMessage:
    """Tests for the update_chat_message method."""

    def test_update_chat_message_success(self, mock_slack):
        """Test successful message update."""
        mock_slack.update_chat_message(
            channel="C123456", ts="1234567890.123456", text="Updated message"
        )

        mock_slack.client.chat_update.assert_called_once_with(
            channel="C123456", ts="1234567890.123456", text="Updated message"
        )

    def test_update_chat_message_api_error(self, mock_slack):
        """Test that API errors are raised properly."""
        mock_slack.client.chat_update.side_effect = SlackApiError(
            message="API Error", response={"error": "message_not_found"}
        )

        with pytest.raises(SlackApiError):
            mock_slack.update_chat_message(
                channel="C123456", ts="1234567890.123456", text="Updated"
            )


class TestOpenDialog:
    """Tests for the open_dialog method."""

    def test_open_dialog_success(self, mock_slack):
        """Test successful dialog opening."""
        mock_response = {"ok": True}
        mock_slack.client.dialog_open.return_value = mock_response

        dialog = {"title": "Test Dialog", "elements": []}
        result = mock_slack.open_dialog(trigger_id="T123456", dialog=dialog)

        assert result == mock_response
        mock_slack.client.dialog_open.assert_called_once_with(
            trigger_id="T123456", dialog=dialog
        )

    def test_open_dialog_api_error(self, mock_slack):
        """Test that API errors are raised properly."""
        mock_slack.client.dialog_open.side_effect = SlackApiError(
            message="API Error", response={"error": "invalid_trigger"}
        )

        with pytest.raises(SlackApiError):
            mock_slack.open_dialog(trigger_id="T123456", dialog={})


class TestSlackInitialization:
    """Tests for Slack class initialization."""

    def test_slack_init_with_team_id(self, monkeypatch):
        """Test Slack initialization with team_id."""
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-token")

        with patch("lib.api.slack.WebClient") as mock_client, patch(
            "lib.api.slack.OauthMongoDAL"
        ):
            Slack(team_id="test_team")
            mock_client.assert_called_once_with(token="xoxb-test-token")

    def test_slack_init_without_team_id(self, monkeypatch):
        """Test Slack initialization without team_id."""
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-default-token")

        with patch("lib.api.slack.WebClient") as mock_client, patch(
            "lib.api.slack.OauthMongoDAL"
        ):
            Slack(team_id=None)
            mock_client.assert_called_once_with(token="xoxb-default-token")
