CREATE TABLE IF NOT EXISTS social_posts (
    id SERIAL PRIMARY KEY,

    tweet_id TEXT,

    created_at TIMESTAMP,

    text TEXT,

    language VARCHAR(20),

    sentiment VARCHAR(20),

    topic VARCHAR(100),

    match_name VARCHAR(255),

    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);