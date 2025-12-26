-- IDE-Native Teaching System - Database Migration (Idempotent)
-- Run with: sqlite3 .ai_coach/progress.db < Scripts/migrate.sql

BEGIN TRANSACTION;

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Check if migration v1 already applied
-- SQLite user_version approach (alternative to checking schema_version table)
PRAGMA user_version;
-- After migration, we'll set user_version=1

-- File lifecycle tracking (with UNIQUE constraint)
CREATE TABLE IF NOT EXISTS file_history (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    opened_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    last_opened TIMESTAMP,
    lessons TEXT  -- JSON array of lesson IDs
);

-- Error tracking
CREATE TABLE IF NOT EXISTS errors_log (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT,
    line_number INTEGER,
    error_type TEXT,
    error_message TEXT,
    lesson_created INTEGER,  -- FK to knowledge_extracts
    resolved INTEGER DEFAULT 0
);

-- Injection tracking (for safe undo)
CREATE TABLE IF NOT EXISTS injections (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    marker TEXT,
    start_line INTEGER,
    end_line INTEGER,
    backup_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_errors_log_file ON errors_log(file_path);
CREATE INDEX IF NOT EXISTS idx_file_history_path ON file_history(file_path);
CREATE INDEX IF NOT EXISTS idx_injections_file ON injections(file_path);

-- Record migration version
INSERT OR IGNORE INTO schema_version(version) VALUES (1);

COMMIT;

-- Enable WAL mode for concurrency
PRAGMA journal_mode=WAL;
