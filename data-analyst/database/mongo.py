from pymongo import MongoClient
from config import *

class MongoManager:

    def __init__(self):

        self.uri = (
            f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}"
            f"@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}"
            f"?authSource={MONGO_DATABASE}"
        )

        self.client = MongoClient(self.uri)

        self.db = self.client[MONGO_DATABASE]

        self.collection = self.db[MONGO_COLLECTION]

    def insert_post(self, post: dict):

        return self.collection.insert_one(post)

    def insert_many_posts(self, posts: list):

        return self.collection.insert_many(posts)

    def get_posts(self):

        return list(self.collection.find())

    def get_posts_by_event(self,  match_id):

        return list(
            self.collection.find(
                {"match_id": match_id}
            )
        )

    def delete_all(self):

        self.collection.delete_many({})

    def count_posts(self):

        return self.collection.count_documents({})

    def close(self):

        self.client.close()