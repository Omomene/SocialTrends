from langdetect import detect


def detect_language(text):

    try:
        return detect(str(text))

    except Exception:
        return "unknown"