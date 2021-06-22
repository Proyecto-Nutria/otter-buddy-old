import pymongo

from otter_buddy.data.dbconn import DbConn


class DbEmail:

    @staticmethod
    def get_mail(user_id: int, guild_id: int):
        with DbConn() as conn:
            result = conn.connection.InterviewBuddy.mails.find_one({ "user_id": user_id, "guild_id": guild_id })
            return result

    @staticmethod
    def set_mail(user):
        with DbConn() as conn:
            result = conn.connection.InterviewBuddy.mails.update_one({ "user_id" : { "$eq": user['user_id'] }, "guild_id" : { "$eq": user['guild_id'] } }, { "$set" : user }, upsert=True)
            return result