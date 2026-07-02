from database.mongo import MongoManager
from tests.fake_posts import FAKE_POSTS

mongo = MongoManager()

mongo.delete_all()

mongo.insert_many_posts(FAKE_POSTS)

count = mongo.count_posts()

print("Posts inserted :", count)

assert count == 2

print("TEST INSERT OK")