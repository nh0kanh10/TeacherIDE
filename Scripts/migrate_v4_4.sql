-- v4.4 Migration: Silent Assistant
-- File activity tracking for passive observation

CREATE TABLE IF NOT EXISTS file_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    activity_type TEXT, -- 'modified', 'created', 'deleted'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER DEFAULT 1
);

CREATE INDEX idx_file_activity_time ON file_activity(timestamp DESC);
CREATE INDEX idx_file_activity_file ON file_activity(file_path);
