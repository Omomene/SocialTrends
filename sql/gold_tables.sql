CREATE TABLE IF NOT EXISTS social_gold (
    id SERIAL PRIMARY KEY,

    post_id BIGINT,
    created_at TIMESTAMP,

    text_clean TEXT,
    language TEXT,

    sentiment_label TEXT,
    sentiment_score FLOAT,

    topic TEXT,

    likes INT,
    source TEXT,

    match_name TEXT,
    team TEXT,
    player TEXT,
    event_type TEXT,

    processed_at TIMESTAMP
);