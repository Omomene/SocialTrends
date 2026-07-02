from nlp.topic_modeling import get_topic


def run_topic(post):

    post["topic"] = get_topic(
        post.get("text", "")
    )

    return post