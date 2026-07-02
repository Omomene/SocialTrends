from database.mongo import MongoManager

mongo = MongoManager()


def save_post(post: dict):

    document = {

        "post_id": post["post_id"],

        "match_id": post["match_id"],

        "match_name": post["match_name"],

        "source": post["source"],

        "created_at": post["created_at"],

        "text_raw": post.get("text_raw"),

        "text_clean": post.get("text_clean"),

        "language": post["language"],

        "sentiment": {

            "label": post["sentiment_label"],

            "score": float(post["sentiment_score"])
        },

        "topic": {

            "id": int(post["topic_id"]),

            "label": post["topic_label"]
        },

        "processed_at": post["processed_at"]
    }

    mongo.insert_post(document)