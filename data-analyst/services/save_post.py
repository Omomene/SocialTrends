from database.mongo import MongoManager

mongo = MongoManager()

def save_post(post: dict):

    mongo.insert_post(post)