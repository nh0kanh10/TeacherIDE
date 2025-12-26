"""
Run v4.0 Database Migration
Foundation: Skills normalization + Event log + User preferences
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
MIGRATION_SQL = Path(__file__).parent / 'migrate_v4.sql'

def run_migration():
    print("🔧 Running v4.0 Migration...")
    print(f"Database: {DB_PATH}")
    
    if not DB_PATH.exists():
        print("❌ Database not found! Run v3 migration first.")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check current version
        cursor.execute("SELECT MAX(version) FROM schema_version")
        current_version = cursor.fetchone()[0] or 0
        
        if current_version >= 4:
            print(f"✅ Database already at v{current_version}")
            print("Migration not needed.")
            return True
        
        print(f"Upgrading from v{current_version} to v4...")
        
        # Read and execute migration
        with open(MIGRATION_SQL, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        cursor.executescript(migration_sql)
        conn.commit()
        
        # Verify
        cursor.execute("SELECT version FROM schema_version ORDER BY version")
        versions = [row[0] for row in cursor.fetchall()]
        print(f"\n✅ Migration complete!")
        print(f"Schema versions: {versions}")
        
        # Show new tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('skills', 'event_log', 'user_preferences')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n📊 New tables: {tables}")
        
        # Count skills
        cursor.execute("SELECT COUNT(*) FROM skills")
        skill_count = cursor.fetchone()[0]
        print(f"📚 Skills populated: {skill_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
   
    success = run_migration()
    sys.exit(0 if success else 1)
