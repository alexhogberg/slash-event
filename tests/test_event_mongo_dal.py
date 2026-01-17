# coding=utf-8
"""
Integration tests for EventMongoDAL.
These tests are marked for integration and require a MongoDB connection.
They are kept commented out but preserved for reference.

The mocked unit tests are in test_mongodb.py.
"""
import os

import pytest

# Skip all integration tests if MongoDB is not configured
requires_mongodb = pytest.mark.skipif(
    not os.getenv("MONGO_DB_CONNECTION_STRING")
    or os.getenv("MONGO_DB_CONNECTION_STRING") == "mongodb://localhost:27017",
    reason="Requires MONGO_DB_CONNECTION_STRING environment variable with a valid connection string",
)


# Integration tests for EventMongoDAL are available but disabled by default
# Run with: pytest tests/test_event_mongo_dal.py --run-integration
# when a real MongoDB connection is available

# @requires_mongodb
# @pytest.fixture
# def event_dal():
#     from lib.api.mongodb import EventMongoDAL
#     return EventMongoDAL(team_id="test_team_integration")
#
# @requires_mongodb
# @pytest.fixture
# def test_event():
#     from lib.models.event import Event
#     return Event(
#         _id=None,
#         team_id="test_team_integration",
#         date="2025-05-11",
#         time="12:00",
#         location={"name": "Test Location"},
#         description="Test Event Description",
#         participants=["test_user1"],
#         author="test_user1",
#     )
#
# @requires_mongodb
# def test_integration_insert_event(event_dal, test_event):
#     """Integration test for inserting events."""
#     event_id = event_dal.insert_event(test_event)
#     assert event_id is not None
#
#     inserted_event = event_dal.get_event(event_id)
#     assert inserted_event is not None
#     assert inserted_event.date == test_event.date
#
# @requires_mongodb
# @pytest.fixture(autouse=True)
# def cleanup(event_dal):
#     """Cleanup test data after each test."""
#     yield
#     event_dal.database.events.delete_many({"team_id": "test_team_integration"})