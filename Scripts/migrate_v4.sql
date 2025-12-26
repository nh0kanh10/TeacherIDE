-- v4.0 Database Migration
-- Foundation: Skills table normalization + Event logging

-- 1. Add version 4 migration record
INSERT OR IGNORE INTO schema_version(version) VALUES (4);

-- 2. Skills table (normalize skill references)
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT,
    complexity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);

-- 3. Event log table
CREATE TABLE IF NOT EXISTS event_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_data TEXT,  -- JSON
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_log(event_type);
CREATE INDEX IF NOT EXISTS idx_event_log_timestamp ON event_log(timestamp);

-- 4. User preferences (v4 controls)
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY,
    user_id INTEGER DEFAULT 1,
    preference_key TEXT NOT NULL,
    preference_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

-- 5. Populate skills table from existing data
INSERT OR IGNORE INTO skills (name, category, complexity)
SELECT DISTINCT 
    skill_name as name,
    CASE 
        WHEN skill_name LIKE '%python%' THEN 'python'
        WHEN skill_name LIKE '%javascript%' THEN 'javascript'
        WHEN skill_name LIKE '%sql%' THEN 'sql'
        ELSE 'general'
    END as category,
    5 as complexity  -- Default medium
FROM skill_mastery
WHERE skill_name IS NOT NULL;

-- 6. Default user preferences (v4 features)
INSERT OR IGNORE INTO user_preferences (user_id, preference_key, preference_value) VALUES
(1, 'v4.spaced_repetition', 'true'),
(1, 'v4.emotion_detection', 'true'),
(1, 'v4.emotion_threshold', '0.7'),
(1, 'v4.proactive_suggestions', 'true'),
(1, 'v4.max_suggestions_per_session', '3'),
(1, 'v4.ide_hints', 'false');

-- 7. Spaced Repetition table (FSRS v5)
CREATE TABLE IF NOT EXISTS spaced_repetition (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    skill_id INTEGER NOT NULL,
    stability REAL DEFAULT 0.0,
    difficulty REAL DEFAULT 0.0,
    elapsed_days INTEGER DEFAULT 0,
    scheduled_days INTEGER DEFAULT 0,
    reps INTEGER DEFAULT 0,
    lapses INTEGER DEFAULT 0,
    state INTEGER DEFAULT 0,
    last_review TIMESTAMP,
    due TIMESTAMP
CREATE VIEW IF NOT EXISTS v_skills_with_mastery AS
SELECT 
    s.id as skill_id,
    s.name as skill_name,
    s.category,
    s.complexity,
    COALESCE(sm.mastery_prob, 0) as current_mastery,
    sm.attempts,
    sm.correct,
    sm.last_practiced
FROM skills s
LEFT JOIN skill_mastery sm ON s.name = sm.skill_name;
