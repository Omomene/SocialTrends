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

    occurrences INTEGER
);