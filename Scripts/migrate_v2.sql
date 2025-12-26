-- Migration v2: Schema Improvements
-- Fixes: Add Foreign Keys, create junction table for file-lesson mapping

BEGIN TRANSACTION;

-- 1. Add version 2 migration record
INSERT OR IGNORE INTO schema_version(version) VALUES (2);

-- 2. Create junction table for file-lesson mapping (replaces JSON in TEXT)
CREATE TABLE IF NOT EXISTS file_lessons_map (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES file_history(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES knowledge_extracts(id) ON DELETE CASCADE,
    UNIQUE(file_id, lesson_id)  -- Prevent duplicates
);

CREATE INDEX IF NOT EXISTS idx_file_lessons_file ON file_lessons_map(file_id);
CREATE INDEX IF NOT EXISTS idx_file_lessons_lesson ON file_lessons_map(lesson_id);

-- 3. Add file_id to errors_log for proper relationship
-- Note: SQLite doesn't support ADD FOREIGN KEY, so we check if column exists
-- If column doesn't exist, we'll handle in Python migration script

-- 4. Create index on knowledge_extracts.file_path for faster spatial queries
CREATE INDEX IF NOT EXISTS idx_knowledge_file_path ON knowledge_extracts(file_path);
CREATE INDEX IF NOT EXISTS idx_knowledge_topic ON knowledge_extracts(topic);

-- 5. Add sidecar_type column to track lesson storage type
-- Will be added via Python migration script due to SQLite limitations

COMMIT;

-- Enable foreign keys enforcement
PRAGMA foreign_keys = ON;
