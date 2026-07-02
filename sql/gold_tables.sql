CREATE TABLE IF NOT EXISTS sentiment_hourly (

    id SERIAL PRIMARY KEY,

    hour_bucket TIMESTAMP,

    match_name VARCHAR(255),

    positive_count INTEGER,

    neutral_count INTEGER,

    negative_count INTEGER,

    total_posts INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);