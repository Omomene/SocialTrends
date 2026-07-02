CREATE TABLE IF NOT EXISTS football_events (

    id SERIAL PRIMARY KEY,

    event_time TIMESTAMP,

    match_name VARCHAR(255),

    event_type VARCHAR(50),

    team VARCHAR(100),

    player VARCHAR(100)
);