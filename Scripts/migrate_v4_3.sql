-- v4.3 Migration: Adaptive Teaching Style
-- Tracks teaching effectiveness by style

-- 1. Teaching effectiveness tracking
CREATE TABLE IF NOT EXISTS teaching_effectiveness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    teaching_style TEXT NOT NULL,  -- 'visual', 'hands_on', 'theoretical', 'example_based', 'analogy'
    skill_name TEXT NOT NULL,
    mastery_before REAL,
    mastery_after REAL,
    improvement REAL,  -- mastery_after - mastery_before
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retention_checked BOOLEAN DEFAULT 0,
    retention_1week REAL,
    effectiveness_score REAL,  -- Composite score
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);

CREATE INDEX idx_teaching_style ON teaching_effectiveness(user_id, teaching_style);
CREATE INDEX idx_teaching_skill ON teaching_effectiveness(skill_name);

-- 2. Style preferences (pre-aggregated)
CREATE TABLE IF NOT EXISTS style_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    teaching_style TEXT NOT NULL,
    avg_effectiveness REAL DEFAULT 0.5,
    sample_size INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id),
    UNIQUE(user_id, teaching_style)
);

-- 3. Default preferences (Epsilon-Greedy initialization)
INSERT OR IGNORE INTO style_preferences (user_id, teaching_style, avg_effectiveness, sample_size)
VALUES 
    (1, 'visual', 0.5, 0),
    (1, 'hands_on', 0.5, 0),
    (1, 'theoretical', 0.5, 0),
    (1, 'example_based', 0.5, 0),
    (1, 'analogy', 0.5, 0);
