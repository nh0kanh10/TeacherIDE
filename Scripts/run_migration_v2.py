"""
Migration v2 Runner - Apply schema improvements
"""
import sqlite3
from pathlib import Path
import sys
import json

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
MIGRATE_V2_SQL = Path(__file__).parent / 'migrate_v2.sql'

def get_current_version(conn):
    """Get current schema version"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT MAX(version) FROM schema_version")
        result = cur.fetchone()
        return result[0] if result[0] else 0
    except sqlite3.OperationalError:
        return 0

def migrate_json_to_junction_table(conn):
    """
    Migrate lessons from JSON TEXT column to junction table
    file_history.lessons (TEXT with JSON) → file_lessons_map table
    """
    cur = conn.cursor()
    
    # Get all file_history records with lessons
    cur.execute("SELECT id, file_path, lessons FROM file_history WHERE lessons IS NOT NULL")
    rows = cur.fetchall()
    
    migrated_count = 0
    for file_id, file_path, lessons_json in rows:
        if not lessons_json:
            continue
        
        try:
            lesson_ids = json.loads(lessons_json)
            if not isinstance(lesson_ids, list):
                continue
            
            # Insert into junction table
            for lesson_id in lesson_ids:
                try:
                    cur.execute("""
                        INSERT OR IGNORE INTO file_lessons_map (file_id, lesson_id)
                        VALUES (?, ?)
                    """, (file_id, lesson_id))
                    migrated_count += 1
                except sqlite3.IntegrityError:
                    # FK constraint failed - lesson might not exist
                    pass
        except json.JSONDecodeError:
            print(f"  ⚠️  Invalid JSON in file_history.id={file_id}")
            continue
    
    conn.commit()
    print(f"  ✅ Migrated {migrated_count} file-lesson mappings to junction table")

def add_sidecar_type_column(conn):
    """Add sidecar_type column to differentiate sidecar vs inline lessons"""
    cur = conn.cursor()
    
    # Check if column exists
    cur.execute("PRAGMA table_info(knowledge_extracts)")
    columns = {row[1] for row in cur.fetchall()}
    
    if 'sidecar_type' not in columns:
        cur.execute("ALTER TABLE knowledge_extracts ADD COLUMN sidecar_type TEXT DEFAULT 'vault'")
        conn.commit()
        print("  ✅ Added sidecar_type column")
    else:
        print("  ℹ️  sidecar_type column already exists")

def run_migration_v2():
    """Run migration v2"""
    print("=" * 60)
    print("Migration v2: Schema Improvements")
    print("=" * 60)
    print(f"📊 Database: {DB_PATH}\n")
    
    if not DB_PATH.exists():
        print("❌ Database not found. Run migration v1 first.")
        return False
    
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    
    # Check current version
    current_version = get_current_version(conn)
    print(f"   Current schema version: {current_version}")
    
    if current_version >= 2:
        print("   ✅ Database already at v2 or higher")
        conn.close()
        return True
    
    if current_version < 1:
        print("   ❌ Please run migration v1 first (run_migration.py)")
        conn.close()
        return False
    
    print(f"   🔄 Applying migration v2...")
    
    # Run SQL migration
    if MIGRATE_V2_SQL.exists():
        migration_sql = MIGRATE_V2_SQL.read_text(encoding='utf-8')
        conn.executescript(migration_sql)
        print("   ✅ Executed migrate_v2.sql")
    else:
        print(f"   ⚠️  migrate_v2.sql not found, applying manually...")
        
        # Fallback: create tables manually
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_lessons_map (
                id INTEGER PRIMARY KEY,
                file_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES file_history(id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES knowledge_extracts(id) ON DELETE CASCADE,
                UNIQUE(file_id, lesson_id)
            )
        """)
        
        conn.execute("CREATE INDEX IF NOT EXISTS idx_file_lessons_file ON file_lessons_map(file_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_file_lessons_lesson ON file_lessons_map(lesson_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_file_path ON knowledge_extracts(file_path)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_topic ON knowledge_extracts(topic)")
        
        conn.execute("INSERT OR IGNORE INTO schema_version(version) VALUES (2)")
        conn.commit()
    
    # Migrate existing JSON data to junction table
    print("\n   📦 Migrating JSON data to junction table...")
    migrate_json_to_junction_table(conn)
    
    # Add sidecar_type column
    print("\n   🔧 Adding sidecar_type column...")
    add_sidecar_type_column(conn)
    
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    print("\n   ✅ Enabled foreign key constraints")
    
    # Verify final version
    final_version = get_current_version(conn)
    print(f"\n   ✅ Migration complete! Schema version: {final_version}")
    
    conn.close()
    return True

def verify_migration_v2():
    """Verify v2 migration success"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    required_tables = ['file_lessons_map']
    required_indexes = ['idx_file_lessons_file', 'idx_file_lessons_lesson']
    
    print("\n🔍 Verifying migration v2:")
    
    all_good = True
    
    for table in required_tables:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cur.fetchone():
            print(f"   ✅ Table exists: {table}")
        else:
            print(f"   ❌ Missing table: {table}")
            all_good = False
    
    for index in required_indexes:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index,))
        if cur.fetchone():
            print(f"   ✅ Index exists: {index}")
        else:
            print(f"   ❌ Missing index: {index}")
            all_good = False
    
    # Check if junction table has data (if migrated from JSON)
    cur.execute("SELECT COUNT(*) FROM file_lessons_map")
    count = cur.fetchone()[0]
    print(f"   ℹ️  file_lessons_map entries: {count}")
    
    conn.close()
    return all_good

if __name__ == "__main__":
    success = run_migration_v2()
    
    if success:
        verify_migration_v2()
        print("\n✅ Migration v2 completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Migration v2 failed!")
        sys.exit(1)
