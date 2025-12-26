-- v4.2 Migration: Long-Term Memory
-- Tracks deep conceptual understanding and error patterns

-- 1. Deep memory (conceptual understanding)
CREATE TABLE IF NOT EXISTS deep_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    concept TEXT NOT NULL,
    user_misconception TEXT,
    correct_understanding TEXT,
    aha_moment TEXT,
    confidence_score REAL DEFAULT 0.5,  -- ✅ Validation threshold
    validation_count INTEGER DEFAULT 1,
    related_errors TEXT,  -- JSON array of error IDs
    first_encountered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_recalled TIMESTAMP,
    recall_count INTEGER DEFAULT 0,
    retention_score REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);

CREATE INDEX idx_deep_memory_concept ON deep_memory(user_id, concept);
CREATE INDEX idx_deep_memory_confidence ON deep_memory(confidence_score DESC);

-- 2. Error patterns (recurring mistakes)
CREATE TABLE IF NOT EXISTS error_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    error_type TEXT NOT NULL,  -- 'syntax', 'logic', 'concept', 'typo'
    pattern_description TEXT,
    example_code TEXT,
    occurrence_count INTEGER DEFAULT 1,
    first_occurred TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_occurred TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    related_concept TEXT,
    fix_learned BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_profile(id)
);

CREATE INDEX idx_error_patterns_type ON error_patterns(user_id, error_type);
CREATE INDEX idx_error_patterns_count ON error_patterns(occurrence_count DESC);

-- 3. Concept links (relationships between concepts)
CREATE TABLE IF NOT EXISTS concept_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    concept_a TEXT NOT NULL,
    concept_b TEXT NOT  NULL,
    link_type TEXT,  -- 'prerequisite', 'related', 'opposite', 'example'
    strength REAL DEFAULT 0.5,  -- How strong the connection
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profile(id),
    UNIQUE(user_id, concept_a, concept_b)
);

CREATE INDEX idx_concept_links ON concept_links(user_id, concept_a);
