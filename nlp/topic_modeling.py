def get_topic(text):

    text = str(text).lower()

    if any(word in text for word in [
        "goal",
        "score",
        "scored",
        "penalty",
        "striker"
    ]):
        return "match_action"

    if any(word in text for word in [
        "referee",
        "var",
        "offside"
    ]):
        return "officiating"

    if any(word in text for word in [
        "coach",
        "manager",
        "tactics"
    ]):
        return "tactics"

    return "general"