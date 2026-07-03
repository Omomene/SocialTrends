CREATE TABLE IF NOT EXISTS sentiment_summary (
    sentiment_label TEXT,
    total_posts INT
);

CREATE TABLE IF NOT EXISTS team_summary (
    team TEXT,
    total_posts INT,
    avg_sentiment FLOAT
);

CREATE TABLE IF NOT EXISTS match_summary (
    match_name TEXT,
    total_posts INT,
    positive_posts INT,
    negative_posts INT
);