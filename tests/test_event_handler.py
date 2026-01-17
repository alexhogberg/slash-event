from unittest.mock import MagicMock, patch

import pytest
from google.maps.places_v1.types import Place

from lib.models.event import Event
from lib.models.event_place import EventPlace
from lib.models.slack_message import SlackMessage
from lib.utils.slack_helpers import print_possible_commands


@pytest.fixture
def event_handler():
    """Create an EventHandler with mocked dependencies."""
    # Patch GooglePlaces and Slack at the module level where they're imported
    with patch("lib.event_handler.GooglePlaces") as mock_google_places_class, patch(
        "lib.event_handler.Slack"
    ) as mock_slack_class:
        # Configure the mock GooglePlaces instance
        mock_google_places = MagicMock()
        mock_google_places_class.return_value = mock_google_places

        # Configure the mock Slack instance
        mock_slack = MagicMock()
        mock_slack.get_channel_id.return_value = "C12345"
        mock_slack_class.return_value = mock_slack

        # Mock the EventMongoDAL
        mock_event_dal = MagicMock()

        from lib.event_handler import EventHandler

        team_id = "test_team"
        bolt_client = MagicMock()
        say_func = MagicMock()
        respond_func = MagicMock()
        current_view = "test_view"

        handler = EventHandler(
            team_id=team_id,
            bolt_client=bolt_client,
            say_func=say_func,
            respond_func=respond_func,
            current_view=current_view,
            event_dal=mock_event_dal,
        )

        # Store the mocks on the handler for use in tests
        handler._mock_google_places = mock_google_places
        handler._mock_slack = mock_slack
        handler._mock_event_dal = mock_event_dal

        yield handler


@pytest.fixture
def get_mock_event():
    return Event(
        _id=1,
        date="2023-10-10",
        team_id="team_id",
        time="18:00",
        location=EventPlace(
            Place(
                name="Test Place",
                id="ChIJN1t_tDeuEmsRUsoyG83frY4",
                formatted_address="123 Test St",
                rating=4.5,
                types=["restaurant", "bar"],
            )
        ),
        participants=["U12345"],
        author="U67890",
    )


def test_parse_command_no_command(event_handler):
    event_handler.respond = MagicMock()
    event_handler.parse_command("", {})
    event_handler.respond.assert_called_once_with(
        f"No command given, {print_possible_commands()}"
    )


def test_parse_command_invalid_command(event_handler):
    event_handler.respond = MagicMock()
    event_handler.parse_command("invalid_command", {})
    event_handler.respond.assert_called_once_with(
        f"Invalid command given, {print_possible_commands()}"
    )


def test_list_event_with_results(event_handler, get_mock_event):
    event_handler.event_dal.list_events = MagicMock(return_value=[get_mock_event])
    event_handler.respond = MagicMock()
    event_handler.list_event("list", {"user_id": "test_user"})
    event_handler.respond.assert_called_once()


def test_list_event_no_results(event_handler):
    event_handler.event_dal.list_events = MagicMock(return_value=[])
    event_handler.respond = MagicMock()
    event_handler.list_event("list", {"user_id": "test_user"})
    called_args: SlackMessage = event_handler.respond.call_args[0][
        0
    ]  # Extract the first argument passed to respond
    assert called_args["text"] == "There is no upcoming event planned"


def test_create_event(event_handler):
    event_handler.bolt_client.views_open = MagicMock()
    event_handler.respond = MagicMock()
    event_handler.create_event("list", {"trigger_id": "test_trigger"})
    event_handler.bolt_client.views_open.assert_called_once()
    event_handler.respond.assert_called_once_with(
        "Please follow the instructions in the dialog!"
    )


def test_join_event_success(event_handler):
    event_handler.event_dal.join_event = MagicMock(return_value=True)
    event_handler.send_epemeral_message = MagicMock()
    result = event_handler.join_event("test_author", "test_id", "test_channel")
    assert result is True
    event_handler.send_epemeral_message.assert_called_once_with(
        "*Great!* You've joined the event!", "test_author", "test_channel"
    )


def test_join_event_failure(event_handler):
    event_handler.event_dal.join_event = MagicMock(return_value=False)
    event_handler.send_epemeral_message = MagicMock()
    result = event_handler.join_event("test_author", "test_id", "test_channel")
    assert result == (
        None,
        "*Oops!* I couldn't join you to that event. Maybe you are already participating?",
    )
    event_handler.send_epemeral_message.assert_called_once_with(
        "*Oops!* I couldn't join you to that event. Maybe you are already participating?",
        "test_author",
        "test_channel",
    )


def test_leave_event_success(event_handler):
    event_handler.event_dal.leave_event = MagicMock(return_value=True)
    event_handler.send_epemeral_message = MagicMock()
    result = event_handler.leave_event("test_id", "test_author", "test_channel")
    assert result is True
    event_handler.send_epemeral_message.assert_called_once_with(
        "*Done!* You are now removed from the event!",
        "test_author",
        "test_channel",
    )


def test_leave_event_failure(event_handler):
    event_handler.event_dal.leave_event = MagicMock(return_value=False)
    event_handler.send_epemeral_message = MagicMock()
    result = event_handler.leave_event("test_id", "test_author", "test_channel")
    assert result == (None, "*Oops!* Are you really joined to that event?")
    event_handler.send_epemeral_message.assert_called_once_with(
        "*Oops!* Are you really joined to that event?",
        "test_author",
        "test_channel",
    )


def test_suggest_event_no_area(event_handler):
    event_handler.bolt_client.chat_postEphemeral = MagicMock()
    event_handler.suggest_event(["suggest"], {})
    event_handler.bolt_client.chat_postEphemeral.assert_called_once_with(
        "Please specify a location to search for"
    )


def test_suggest_event_with_area(event_handler):
    event_handler.google_places.get_suggestions = MagicMock(
        return_value=[
            Place(
                name="Test Place",
                id="ChIJN1t_tDeuEmsRUsoyG83frY4",
                formatted_address="123 Test St",
                rating=4.5,
                types=["restaurant", "bar"],
            ),
            Place(
                name="Another Place",
                id="ChIJN1t_tDeuEmsRUsoyG83frY5",
                formatted_address="456 Another St",
                rating=4.0,
                types=["cafe", "restaurant"],
            ),
            Place(
                name="Third Place",
                id="ChIJN1t_tDeuEmsRUsoyG83frY6",
                formatted_address="789 Third St",
                rating=3.5,
                types=["bar", "night_club"],
            ),
        ]
    )
    event_handler.respond = MagicMock()
    event_handler.suggest_event(["suggest", "New York"], {})
    event_handler.respond.assert_called_once()


def test_create_event_from_input(event_handler):
    event_handler.google_places.get_place_information = MagicMock()
    event_handler.google_places.format_place = MagicMock()
    event_handler.event_dal.insert_event = MagicMock(return_value="test_id")
    event_handler.say = MagicMock()
    event_handler.create_event_from_input(
        date="2023-10-01",
        place_id="test_place",
        time="18:00",
        author="test_author",
        channel_id="test_channel",
        description="Test Event",
    )
    event_handler.say.assert_called_once()


def test_delete_event_success(event_handler):
    """Test successful event deletion by the event author."""
    mock_event = {
        "Author": "test_author",
        "Location": {"name": "Test Place"},
        "Date": "test_team|2023-10-01",
        "Time": "18:00",
    }
    event_handler.event_dal.get_event = MagicMock(return_value=mock_event)
    event_handler.event_dal.delete_event = MagicMock(return_value=True)
    event_handler.send_epemeral_message = MagicMock()
    event_handler.say = MagicMock()

    result = event_handler.delete_event("test_id", "test_author", "test_channel")

    assert result is True
    event_handler.event_dal.get_event.assert_called_once_with("test_id")
    event_handler.event_dal.delete_event.assert_called_once_with(
        "test_id", "test_author"
    )
    event_handler.say.assert_called_once()


def test_delete_event_not_found(event_handler):
    """Test event deletion when event not found."""
    event_handler.event_dal.get_event = MagicMock(return_value=None)
    event_handler.send_epemeral_message = MagicMock()

    result = event_handler.delete_event("test_id", "test_author", "test_channel")

    assert result == (None, "Event not found.")
    event_handler.send_epemeral_message.assert_called_once_with(
        "*Sorry!* I couldn't find the event to delete.",
        "test_author",
        "test_channel",
    )


def test_delete_event_unauthorized(event_handler):
    """Test event deletion by non-author."""
    mock_event = {"Author": "different_author"}
    event_handler.event_dal.get_event = MagicMock(return_value=mock_event)
    event_handler.send_epemeral_message = MagicMock()

    result = event_handler.delete_event("test_id", "test_author", "test_channel")

    assert result == (None, "Unauthorized to delete the event.")
    event_handler.send_epemeral_message.assert_called_once_with(
        "*Sorry!* You can only delete events you created.",
        "test_author",
        "test_channel",
    )


def test_delete_event_failure(event_handler):
    """Test event deletion failure at DAL level."""
    mock_event = {
        "Author": "test_author",
        "Location": {"name": "Test Place"},
        "Date": "test_team|2023-10-01",
        "Time": "18:00",
    }
    event_handler.event_dal.get_event = MagicMock(return_value=mock_event)
    event_handler.event_dal.delete_event = MagicMock(return_value=False)
    event_handler.send_epemeral_message = MagicMock()

    result = event_handler.delete_event("test_id", "test_author", "test_channel")

    assert result == (None, "Failed to delete the event.")
    event_handler.send_epemeral_message.assert_called_once_with(
        "*Sorry!* I was unable to delete the event.",
        "test_author",
        "test_channel",
    )


def test_delete_event_none_id(event_handler):
    """Test delete_event with None id returns error message."""
    result = event_handler.delete_event(None, "test_author", "test_channel")

    assert result == "Couldn't find any event on that day."


def test_leave_event_none_id(event_handler):
    """Test leave_event with None id returns error message."""
    result = event_handler.leave_event(None, "test_author", "test_channel")

    assert result == "Couldn't find any event on that day."


def test_send_ephemeral_message_success(event_handler):
    """Test sending ephemeral message."""
    event_handler.bolt_client.chat_postEphemeral = MagicMock()

    event_handler.send_epemeral_message("Test message", "U12345", "C12345")

    event_handler.bolt_client.chat_postEphemeral.assert_called_once_with(
        channel="C12345", text="Test message", user="U12345"
    )


def test_send_ephemeral_message_with_none_values(event_handler):
    """Test that ephemeral message is not sent with None values."""
    event_handler.bolt_client.chat_postEphemeral = MagicMock()

    event_handler.send_epemeral_message(None, "U12345", "C12345")
    event_handler.send_epemeral_message("Test", None, "C12345")
    event_handler.send_epemeral_message("Test", "U12345", None)

    # Should not be called because of None values
    event_handler.bolt_client.chat_postEphemeral.assert_not_called()


def test_update_events_view(event_handler, get_mock_event):
    """Test updating events view."""
    event_handler.event_dal.list_events = MagicMock(return_value=[get_mock_event])
    event_handler.bolt_client.views_publish = MagicMock()

    event_handler.update_events_view("U12345")

    event_handler.bolt_client.views_publish.assert_called_once()


def test_update_events_view_none_user(event_handler):
    """Test that update_events_view does nothing with None user_id."""
    event_handler.bolt_client.views_publish = MagicMock()

    event_handler.update_events_view(None)

    event_handler.bolt_client.views_publish.assert_not_called()


def test_parse_command_list(event_handler, get_mock_event):
    """Test parsing 'list' command."""
    event_handler.event_dal.list_events = MagicMock(return_value=[get_mock_event])
    event_handler.respond = MagicMock()

    event_handler.parse_command("list", {"user_id": "test_user"})

    event_handler.respond.assert_called_once()


def test_parse_command_create(event_handler):
    """Test parsing 'create' command."""
    event_handler.bolt_client.views_open = MagicMock()
    event_handler.respond = MagicMock()

    event_handler.parse_command("create", {"trigger_id": "test_trigger"})

    event_handler.bolt_client.views_open.assert_called_once()


def test_handle_interactive_event_join(event_handler):
    """Test handling interactive join event."""
    payload = {
        "type": "block_actions",
        "actions": [{"action_id": "join_event", "value": "test_event_id"}],
        "user": {"id": "U12345", "team_id": "T12345"},
        "container": {"channel_id": "C12345"},
    }

    event_handler.event_dal.join_event = MagicMock(return_value=True)
    event_handler.event_dal.list_events = MagicMock(return_value=[])
    event_handler.send_epemeral_message = MagicMock()

    event_handler.handle_interactive_event(payload)

    event_handler.event_dal.join_event.assert_called_once_with(
        "test_event_id", "U12345"
    )


def test_handle_interactive_event_leave(event_handler):
    """Test handling interactive leave event."""
    payload = {
        "type": "block_actions",
        "actions": [{"action_id": "leave_event", "value": "test_event_id"}],
        "user": {"id": "U12345", "team_id": "T12345"},
        "container": {"channel_id": "C12345"},
    }

    event_handler.event_dal.leave_event = MagicMock(return_value=True)
    event_handler.event_dal.list_events = MagicMock(return_value=[])
    event_handler.send_epemeral_message = MagicMock()

    event_handler.handle_interactive_event(payload)

    event_handler.event_dal.leave_event.assert_called_once_with(
        "test_event_id", "U12345"
    )


def test_handle_interactive_event_delete(event_handler):
    """Test handling interactive delete event."""
    payload = {
        "type": "block_actions",
        "actions": [{"action_id": "delete_event", "value": "test_event_id"}],
        "user": {"id": "U12345", "team_id": "T12345"},
        "container": {"channel_id": "C12345"},
    }

    mock_event = {
        "Author": "U12345",
        "Location": {"name": "Test Place"},
        "Date": "test_team|2023-10-01",
        "Time": "18:00",
    }
    event_handler.event_dal.get_event = MagicMock(return_value=mock_event)
    event_handler.event_dal.delete_event = MagicMock(return_value=True)
    event_handler.event_dal.list_events = MagicMock(return_value=[])
    event_handler.send_epemeral_message = MagicMock()
    event_handler.say = MagicMock()

    event_handler.handle_interactive_event(payload)

    event_handler.event_dal.delete_event.assert_called_once_with(
        "test_event_id", "U12345"
    )


def test_show_events_view(event_handler, get_mock_event):
    """Test showing events view."""
    event_handler.event_dal.list_events = MagicMock(return_value=[get_mock_event])

    result = event_handler.show_events_view("U12345")

    assert result["type"] == "home"
    assert "blocks" in result
    event_handler.event_dal.list_events.assert_called_once()


def test_show_events_view_empty(event_handler):
    """Test showing events view with no events."""
    event_handler.event_dal.list_events = MagicMock(return_value=[])

    result = event_handler.show_events_view("U12345")

    assert result["type"] == "home"
    assert "blocks" in result
