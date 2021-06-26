import pymongo

from otter_buddy.utils.db.dbconn import DbConn


class DbEmail:

    @staticmethod
    def get_mail(user_id: int, guild_id: int):
        with DbConn() as conn:
            result = conn.connection.OtterBuddy.mails.find_one({ "user_id": user_id, "guild_id": guild_id })
            return result

    @staticmethod
    def set_mail(user):
        with DbConn() as conn:
            result = conn.connection.OtterBuddy.mails.update_one({ "user_id" : { "$eq": user['user_id'] }, "guild_id" : { "$eq": user['guild_id'] } }, { "$set" : user }, upsert=True)
            return result

    @staticmethod
    def delete_mail(user_id: int, guild_id: int):
        with DbConn() as conn:
            result = conn.connection.OtterBuddy.mails.delete_one({ "user_id" : { "$eq": user_id }, "guild_id" : { "$eq": guild_id } })
            return result
