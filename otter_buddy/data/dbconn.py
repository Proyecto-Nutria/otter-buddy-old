import pymongo
import os
import time

from collections import namedtuple
from dotenv import load_dotenv


class DbConn:
    def __init__(self):
        load_dotenv('.env')
        self.conn = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    def get_mail(self, user):
        result = self.conn.InterviewBuddy.mails.find_one({ "id": user.id})
        self.conn.close()
        return result

    def set_mail(self, user):
        result = self.conn.InterviewBuddy.mails.update_one({"id": user.id}, {"$set": user}, upsert=True)
        self.conn.close()
        return result
