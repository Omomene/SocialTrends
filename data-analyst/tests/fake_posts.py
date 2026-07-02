from datetime import datetime

FAKE_POSTS = [
    {
        "post_id": "p1",
        "event_id": "MATCH001",
        "source": "reddit",
        "created_at": datetime.now().isoformat(),

        "text": "Amazing goal",

        "language": "en",

        "sentiment": {
            "label": "positive",
            "score": 0.95
        },

        "topics": [
            "goal",
            "mbappe"
        ]
    },

    {
        "post_id": "p2",
        "event_id": "MATCH001",
        "source": "reddit",
        "created_at": datetime.now().isoformat(),

        "text": "Bad referee",

        "language": "en",

        "sentiment": {
            "label": "negative",
            "score": -0.8
        },

        "topics": [
            "referee"
        ]
    }
]