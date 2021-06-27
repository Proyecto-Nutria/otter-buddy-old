import pymongo

from otter_buddy.utils.db.dbconn import DbConn


class DbInterviewMatch:

    @staticmethod
    def get_interview_match(guild_id: int):
        with DbConn() as conn:
            result = conn.connection.OtterBuddy.interview_matchs.find_one({ "guild_id": guild_id })
            return result

    @staticmethod
    def get_day_interview_match(weekday: int):
        with DbConn() as conn:
            result = conn.connection.OtterBuddy.interview_matchs.find({ "day_of_the_week": weekday })
            return result

    @staticmethod
    def set_interview_match(interview_match):
        with DbConn() as conn:
            result = conn.connection.OtterBuddy.interview_matchs.update_one({ "guild_id" : { "$eq": interview_match['guild_id'] } }, { "$set" : interview_match }, upsert=True)
            return result

    @staticmethod
    def delete_interview_match(guild_id: int):
        with DbConn() as conn:
            result = conn.connection.OtterBuddy.interview_matchs.delete_one({ "guild_id" : { "$eq": guild_id } })
            return result
