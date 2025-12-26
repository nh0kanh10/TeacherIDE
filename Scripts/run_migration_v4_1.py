"""
Run v4.1 Migration - Meta-Learning Tracker
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
SQL_PATH = Path(__file__).parent / 'migrate_v4_1.sql'

def run_migration():
    """Run v4.1 migration"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 Running v4.1 Migration (Meta-Learning Tracker)...")
    print(f"Database: {DB_PATH}")
    
    # Read SQL file
    with open(SQL_PATH, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Execute
    cursor.executescript(sql_script)
    conn.commit()
    
    # Verify
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name IN ('session_analytics', 'meta_learning_stats')
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    
    if len(tables) == 2:
        print(f"✅ Migration complete!")
        print(f"   New tables: {tables}")
        
        # Check stats
        cursor.execute("SELECT COUNT(*) FROM meta_learning_stats")
        stats_count = cursor.fetchone()[0]
        print(f"   Default stats: {stats_count}")
    else:
        print(f"❌ Migration failed - missing tables")
    
    conn.close()

if __name__ == "__main__":
    run_migration()
