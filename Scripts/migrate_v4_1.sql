-- v4.1 Migration: Meta-Learning Tracker
-- Adds session analytics and pre-aggregated learning stats

-- 1. Session analytics (raw data)
CREATE TABLE IF NOT EXISTS session_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    session_start TIMESTAMP NOT NULL,
    session_end TIMESTAMP,
    duration_minutes INTEGER,
    topics_covered TEXT,  -- JSON array of skill names
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    avg_response_time REAL,
    emotions_detected TEXT,  -- JSON array
    fatigue_detected BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);

CREATE INDEX idx_session_start ON session_analytics(session_start);
CREATE INDEX idx_session_user ON session_analytics(user_id);

-- 2. Meta-learning stats (pre-aggregated for fast queries)
CREATE TABLE IF NOT EXISTS meta_learning_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    stat_type TEXT NOT NULL,  -- 'velocity', 'time_perf', 'accuracy', 'session_length'
    time_bucket TEXT,  -- 'week', 'hour', 'day', 'month'
    bucket_value TEXT,  -- ISO week (2025-W01), hour (09), date (2025-12-26)
    metric_value REAL NOT NULL,
    sample_size INTEGER DEFAULT 1,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id),
    UNIQUE(user_id, stat_type, time_bucket, bucket_value)
);

CREATE INDEX idx_meta_stats_type ON meta_learning_stats(user_id, stat_type);
CREATE INDEX idx_meta_stats_bucket ON meta_learning_stats(time_bucket, bucket_value);

-- 3. Default stats
INSERT OR IGNORE INTO meta_learning_stats (user_id, stat_type, time_bucket, bucket_value, metric_value, sample_size)
VALUES 
    (1, 'velocity', 'week', 'default', 0.0, 0),
    (1, 'accuracy', 'overall', 'default', 0.0, 0),
    (1, 'session_length', 'preferred', 'default', 45.0, 1);
