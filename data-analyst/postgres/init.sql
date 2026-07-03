CREATE TABLE IF NOT EXISTS matches (

    match_id VARCHAR(100) PRIMARY KEY,

    home_team VARCHAR(100),

    away_team VARCHAR(100),

    competition VARCHAR(100),

    kickoff_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS match_events (

    id SERIAL PRIMARY KEY,

    match_id VARCHAR(100)
        REFERENCES matches(match_id),

    minute INTEGER,

    event_type VARCHAR(50),

    team VARCHAR(100),

    player VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS sentiment_hourly (

    hour_ts TIMESTAMP,

    match_id VARCHAR(100),

    post_count INTEGER,

    positive_count INTEGER,

    neutral_count INTEGER,

    negative_count INTEGER,

    avg_sentiment NUMERIC(6,3),

    PRIMARY KEY(hour_ts, match_id)
);

CREATE TABLE IF NOT EXISTS topic_hourly (

    hour_ts TIMESTAMP,

    match_id VARCHAR(100),

    topic VARCHAR(100),

    occurrences INTEGER,

    PRIMARY KEY(hour_ts, match_id, topic)
);

CREATE TABLE IF NOT EXISTS trend_summary (

    match_id VARCHAR(255) PRIMARY KEY,

    match_name VARCHAR(255),

    summary_text TEXT,

    generated_at TIMESTAMP
);


CREATE TABLE IF NOT EXISTS sentiment_timeline (

    hour_ts TIMESTAMP,

    match_id VARCHAR(255),

    sentiment_index NUMERIC(8,3),

    dominant_sentiment VARCHAR(50),

    total_posts INTEGER,

    PRIMARY KEY(hour_ts, match_id)
);

CREATE TABLE IF NOT EXISTS event_correlations (

    event_id VARCHAR(255) PRIMARY KEY,

    match_id VARCHAR(255),

    event_time TIMESTAMP,

    event_type VARCHAR(100),

    volume_delta NUMERIC(8,3),

    sentiment_delta NUMERIC(8,3),

    dominant_topic_after TEXT,

    correlation_strength VARCHAR(50),

    explanation TEXT
);