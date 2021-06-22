import pymongo
import os
import time

from collections import namedtuple
from dotenv import load_dotenv


class DbConn:
    def __init__(self):
        load_dotenv()
        self.uri = os.environ.get("MONGO_URI")
        self.connection = None

    def __enter__(self):
        self.connection = pymongo.MongoClient(self.uri)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
