-- v4.7 Enhancement: Prediction Tracking
-- Add tables for prediction feedback loop and response time tracking

-- Table: prediction_tracking
-- Stores predictions made before teaching sessions
CREATE TABLE IF NOT EXISTS prediction_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    prediction_timestamp TEXT NOT NULL,
    
    -- Prediction inputs
    prior_difficulty REAL,
    error_count INTEGER,
    avg_response_time REAL,
    learning_velocity REAL,
    
    -- Prediction outputs
    struggle_probability REAL NOT NULL,
    confidence REAL NOT NULL,
    predicted_action TEXT NOT NULL,  -- 'scaffold' or 'normal'
    
    -- Actual outcome (filled after session)
    actual_struggled INTEGER,  -- NULL until session completes, then 0/1
    mastery_before REAL,
    mastery_after REAL,
    session_duration_min REAL,
    
    -- Accuracy tracking
    prediction_correct INTEGER,  -- NULL until verified, then 0/1
    
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_prediction_skill ON prediction_tracking(skill_name);
CREATE INDEX IF NOT EXISTS idx_prediction_timestamp ON prediction_tracking(prediction_timestamp);

-- Table: response_times
-- Stores individual response times for better prediction accuracy
CREATE TABLE IF NOT EXISTS response_times (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    session_id INTEGER,  -- Optional: link to session_analytics
    response_time_sec REAL NOT NULL,
    correct INTEGER NOT NULL,  -- 0 or 1
    timestamp TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_response_skill ON response_times(skill_name);

-- View: prediction_accuracy
-- Quick view of prediction accuracy metrics
CREATE VIEW IF NOT EXISTS prediction_accuracy AS
SELECT 
    COUNT(*) as total_predictions,
    SUM(CASE WHEN prediction_correct = 1 THEN 1 ELSE 0 END) as correct_predictions,
    ROUND(100.0 * SUM(CASE WHEN prediction_correct = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
    AVG(confidence) as avg_confidence,
    COUNT(CASE WHEN predicted_action = 'scaffold' THEN 1 END) as scaffold_count,
    COUNT(CASE WHEN predicted_action = 'normal' THEN 1 END) as normal_count
FROM prediction_tracking
WHERE prediction_correct IS NOT NULL;

-- View: skill_prediction_performance
-- Per-skill prediction performance
CREATE VIEW IF NOT EXISTS skill_prediction_performance AS
SELECT 
    skill_name,
    COUNT(*) as predictions,
    SUM(CASE WHEN prediction_correct = 1 THEN 1 ELSE 0 END) as correct,
    ROUND(100.0 * SUM(CASE WHEN prediction_correct = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
    AVG(struggle_probability) as avg_struggle_prob
FROM prediction_tracking
WHERE prediction_correct IS NOT NULL
GROUP BY skill_name
HAVING COUNT(*) >= 3
ORDER BY accuracy_pct DESC;
