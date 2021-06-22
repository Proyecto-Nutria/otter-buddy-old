import pymongo
import mongomock
from unittest.mock import patch

from otter_buddy.data import db_email, dbconn


mock_connection = mongomock.MongoClient('mongodb://localhost:27017')

def mock_client(self):
    self.connection = mock_connection
    return self


@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_set_email():
    user = {
        "user_id": 1,
        "guild_id": 1,
        "email": 'test@test.com'
    }
    result = db_email.DbEmail.set_mail(user)
    assert result.matched_count == 0
    assert result.modified_count == 0

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_update_email():
    user = {
        "user_id": 1,
        "guild_id": 1,
        "email": 'new_test@test.com'
    }
    result = db_email.DbEmail.set_mail(user)
    assert result.matched_count == 1
    assert result.modified_count == 1

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_get_email_valid():
    user_id = 1
    guild_id = 1
    result = db_email.DbEmail.get_mail(user_id, guild_id)
    assert result['user_id'] == user_id
    assert result['guild_id'] == guild_id

@patch.object(dbconn.DbConn, '__enter__', mock_client)
def test_get_email_invalid():
    user_id = 0
    guild_id = 1
    result = db_email.DbEmail.get_mail(user_id, guild_id)
    assert result is None