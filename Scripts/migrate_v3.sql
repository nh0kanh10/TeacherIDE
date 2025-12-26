-- Migration v3: Cognitive Teaching System Schema
-- Adds user profiling, skill ROI, knowledge tracing (BKT), and analogy caching

BEGIN TRANSACTION;

-- 1. Add version 3 migration record
INSERT OR IGNORE INTO schema_version(version) VALUES (3);

-- 2. User profile table
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY,
    background TEXT,  -- JSON: ["chef", "musician"]
    career_goals TEXT,  -- JSON: ["backend_dev", "high_salary"]
    learning_style TEXT,  -- "visual", "hands_on", etc.
    current_skill_level TEXT,  -- "beginner", "intermediate", "advanced"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Skill ROI data (market intelligence)
CREATE TABLE IF NOT EXISTS skill_roi (
    skill_name TEXT PRIMARY KEY,
    market_salary REAL,  -- Median from Stack Overflow
    demand_trend REAL,  -- Growth rate from O*NET
    learning_cost REAL,  -- Calculated: Complexity × (1 - Current_Mastery)
    roi_score REAL,  -- Calculated: (Salary × Trend) / Learning_Cost
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Knowledge tracing (BKT) - skill mastery
CREATE TABLE IF NOT EXISTS skill_mastery (
    user_id INTEGER DEFAULT 1,
    skill_name TEXT,
    mastery_prob REAL,  -- 0.0 to 1.0 from BKT
    attempts INTEGER DEFAULT 0,  -- Number of practice attempts
    correct INTEGER DEFAULT 0,  -- Successful attempts
    last_practiced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, skill_name)
);

-- 5. Skill prerequisites (dependency graph)
CREATE TABLE IF NOT EXISTS skill_dependencies (
    skill_name TEXT,
    requires_skill TEXT,
    strength REAL DEFAULT 1.0,  -- How critical is prereq (0.0-1.0)
    PRIMARY KEY (skill_name, requires_skill)
);

-- 6. Analogy cache (SMT-based explanations)
CREATE TABLE IF NOT EXISTS analogies (
    target_concept TEXT,
    source_domain TEXT,  -- "cooking", "music", "general"
    analogy_text TEXT,
    quality_score REAL DEFAULT 0.0,  -- User feedback (1-5)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (target_concept, source_domain)
);

-- 7. Performance indexes for v3 tables
CREATE INDEX IF NOT EXISTS idx_skill_mastery_prob ON skill_mastery(mastery_prob);
CREATE INDEX IF NOT EXISTS idx_skill_mastery_user ON skill_mastery(user_id);
CREATE INDEX IF NOT EXISTS idx_skill_roi_score ON skill_roi(roi_score DESC);
CREATE INDEX IF NOT EXISTS idx_analogies_quality ON analogies(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_skill_deps_requires ON skill_dependencies(requires_skill);

-- 8. Add helpful views
CREATE VIEW IF NOT EXISTS v_top_roi_skills AS
SELECT 
    skill_name, 
    roi_score, 
    market_salary, 
    demand_trend,
    learning_cost
FROM skill_roi
ORDER BY roi_score DESC
LIMIT 20;

CREATE VIEW IF NOT EXISTS v_weak_skills AS
SELECT 
    sm.skill_name,
    sm.mastery_prob,
    sm.attempts,
    sm.last_practiced
FROM skill_mastery sm
WHERE sm.mastery_prob < 0.5
ORDER BY sm.last_practiced DESC;

COMMIT;

-- Verify migration
SELECT 'Migration v3 complete. Schema version: ' || MAX(version) FROM schema_version;
