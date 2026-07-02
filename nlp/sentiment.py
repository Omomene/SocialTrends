from textblob import TextBlob


def get_sentiment(text):

    polarity = TextBlob(str(text)).sentiment.polarity

    if polarity > 0.1:
        return "positive"

    if polarity < -0.1:
        return "negative"

    return "neutral"