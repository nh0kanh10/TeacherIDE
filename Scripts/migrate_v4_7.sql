-- v4.7 Migration: Market Intelligence
-- Date: 2025-12-26

BEGIN TRANSACTION;

-- Market data table
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    date DATE NOT NULL,
    job_count INTEGER DEFAULT 0,
    salary_min INTEGER,  -- VND
    salary_max INTEGER,
    salary_avg INTEGER,
    source TEXT NOT NULL,  -- 'topcv' or 'vietnamworks'
    raw_data TEXT,  -- JSON backup
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(skill_name, date, source)
);

CREATE INDEX IF NOT EXISTS idx_market_skill_date ON market_data(skill_name, date);
CREATE INDEX IF NOT EXISTS idx_market_source ON market_data(source);

-- Add market fields to skills
ALTER TABLE skills ADD COLUMN market_value INTEGER DEFAULT 0;
ALTER TABLE skills ADD COLUMN demand_score INTEGER DEFAULT 0;
ALTER TABLE skills ADD COLUMN last_market_update DATE;

COMMIT;
