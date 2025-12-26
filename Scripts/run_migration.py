"""
Database Migration Runner
Idempotent schema migration with version tracking
"""
import sqlite3
from pathlib import Path
import sys

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
MIGRATE_SQL = Path(__file__).parent / 'migrate.sql'

def get_current_version(conn):
    """Get current schema version"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT MAX(version) FROM schema_version")
        result = cur.fetchone()
        return result[0] if result[0] else 0
    except sqlite3.OperationalError:
        # schema_version table doesn't exist yet
        return 0

def add_columns_to_knowledge_extracts(conn):
    """
    Pragmatic approach to adding columns to existing table
    SQLite doesn't have IF NOT EXISTS for ALTER COLUMN
    """
    cur = conn.cursor()
    
    # Get existing columns
    cur.execute("PRAGMA table_info(knowledge_extracts)")
    existing_columns = {row[1] for row in cur.fetchall()}
    
    # Add missing columns
    new_columns = {
        'file_path': 'TEXT',
        'line_number': 'INTEGER',
        'symbol_name': 'TEXT',
        'error_type': 'TEXT'
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in existing_columns:
            print(f"  Adding column: knowledge_extracts.{col_name}")
            cur.execute(f"ALTER TABLE knowledge_extracts ADD COLUMN {col_name} {col_type}")
    
    conn.commit()

def run_migration():
    """
    Run database migration
    - Idempotent: safe to run multiple times
    - Version tracking: only applies new migrations
    """
    # Create DB if doesn't exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📊 Migrating database: {DB_PATH}")
    
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    
    # Check current version
    current_version = get_current_version(conn)
    print(f"   Current schema version: {current_version}")
    
    if current_version >= 1:
        print("   ✅ Database already at latest version (v1)")
        conn.close()
        return True
    
    print(f"   🔄 Applying migration v1...")
    
    # Run main migration SQL
    if MIGRATE_SQL.exists():
        migration_sql = MIGRATE_SQL.read_text(encoding='utf-8')
        conn.executescript(migration_sql)
        print("   ✅ Executed migrate.sql")
    else:
        print(f"   ⚠️  migrate.sql not found at {MIGRATE_SQL}")
        print("   Creating tables manually...")
        
        # Fallback: create tables manually (same as migrate.sql)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_history (
                id INTEGER PRIMARY KEY,
                file_path TEXT NOT NULL UNIQUE,
                opened_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                last_opened TIMESTAMP,
                lessons TEXT
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS errors_log (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT,
                line_number INTEGER,
                error_type TEXT,
                error_message TEXT,
                lesson_created INTEGER,
                resolved INTEGER DEFAULT 0
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS injections (
                id INTEGER PRIMARY KEY,
                file_path TEXT,
                marker TEXT,
                start_line INTEGER,
                end_line INTEGER,
                backup_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_errors_log_file ON errors_log(file_path)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_file_history_path ON file_history(file_path)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_injections_file ON injections(file_path)")
        
        # Record version
        conn.execute("INSERT OR IGNORE INTO schema_version(version) VALUES (1)")
        
        conn.commit()
    
    # Add columns to knowledge_extracts (if table exists)
    try:
        add_columns_to_knowledge_extracts(conn)
        print("   ✅ Updated knowledge_extracts table")
    except sqlite3.OperationalError as e:
        print(f"   ⚠️  knowledge_extracts table doesn't exist yet: {e}")
        print("   (This is OK if running for first time)")
    
    # Enable WAL mode for concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    print("   ✅ Enabled WAL mode")
    
    # Verify final version
    final_version = get_current_version(conn)
    print(f"   ✅ Migration complete! Schema version: {final_version}")
    
    conn.close()
    return True

def verify_migration():
    """Verify migration was successful"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    required_tables = ['schema_version', 'file_history', 'errors_log', 'injections']
    
    print("\n🔍 Verifying migration:")
    for table in required_tables:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cur.fetchone():
            print(f"   ✅ Table exists: {table}")
        else:
            print(f"   ❌ Missing table: {table}")
            conn.close()
            return False
    
    conn.close()
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("AI Coach - Database Migration")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        verify_migration()
        print("\n✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
