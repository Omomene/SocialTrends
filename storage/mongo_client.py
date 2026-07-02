from pymongo import MongoClient


def get_mongo():

    client = MongoClient(
        "mongodb://app:app12345@mongo:27017/"
    )

    return client["socialtrends"]