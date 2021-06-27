import mongomock
from unittest.mock import patch

from otter_buddy.utils.db import db_interview_match, dbconn


mock_connection = mongomock.MongoClient('mongodb://localhost:27020')

def mock_client(self):
    self.connection = mock_connection
    return self


@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_set_interview_match():
    interview_match = {
        "emoji":            '👍',
        "day_of_the_week":  1,
        "channel_id":       1,
        "message_id":       1,
        "author_id":        1,
        "guild_id":         1,
    }
    result = db_interview_match.DbInterviewMatch.set_interview_match(interview_match)
    assert result.matched_count == 0
    assert result.modified_count == 0

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_update_interview_match():
    interview_match = {
        "emoji":            '🔥',
        "day_of_the_week":  1,
        "channel_id":       1,
        "message_id":       1,
        "author_id":        1,
        "guild_id":         1,
    }
    result = db_interview_match.DbInterviewMatch.set_interview_match(interview_match)
    assert result.matched_count == 1
    assert result.modified_count == 1

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_get_interview_match_valid():
    guild_id = 1
    result = db_interview_match.DbInterviewMatch.get_interview_match(guild_id)
    assert result['guild_id'] == guild_id

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_get_interview_match_invalid():
    guild_id = 0
    result = db_interview_match.DbInterviewMatch.get_interview_match(guild_id)
    assert result is None

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_populate_interview_match():
    interview_match = {
        "emoji":            '👍',
        "day_of_the_week":  0,
        "channel_id":       1,
        "message_id":       1,
        "author_id":        1,
        "guild_id":         2,
    }
    result = db_interview_match.DbInterviewMatch.set_interview_match(interview_match)
    assert result.matched_count == 0
    assert result.modified_count == 0

    interview_match = {
        "emoji":            '👍',
        "day_of_the_week":  0,
        "channel_id":       1,
        "message_id":       1,
        "author_id":        1,
        "guild_id":         3,
    }
    result = db_interview_match.DbInterviewMatch.set_interview_match(interview_match)
    assert result.matched_count == 0
    assert result.modified_count == 0

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_get_day_interview_match_single():
    weekday = 1
    results = db_interview_match.DbInterviewMatch.get_day_interview_match(weekday)
    matched = 0
    for result in results:
        assert result["day_of_the_week"] == weekday
        matched += 1
    assert matched == 1

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_get_day_interview_match_multiple():
    weekday = 0
    results = db_interview_match.DbInterviewMatch.get_day_interview_match(weekday)
    matched = 0
    for result in results:
        assert result["day_of_the_week"] == weekday
        matched += 1
    assert matched == 2

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_get_day_interview_match_empty():
    weekday = 2
    results = db_interview_match.DbInterviewMatch.get_day_interview_match(weekday)
    matched = 0
    for result in results:
        assert result["day_of_the_week"] == weekday
        matched += 1
    assert matched == 0

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_delete_interview_match_valid():
    guild_id = 1
    result = db_interview_match.DbInterviewMatch.delete_interview_match(guild_id)
    assert result.deleted_count == 1

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_get_interview_match_erased():
    guild_id = 1
    result = db_interview_match.DbInterviewMatch.get_interview_match(guild_id)
    assert result is None

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_delete_interview_match_invalid():
    guild_id = 0
    result = db_interview_match.DbInterviewMatch.delete_interview_match(guild_id)
    assert result.deleted_count == 0
