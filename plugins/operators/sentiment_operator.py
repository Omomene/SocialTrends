from nlp.sentiment import get_sentiment


def run_sentiment(post):

    post["sentiment"] = get_sentiment(
        post.get("text", "")
    )

    return post