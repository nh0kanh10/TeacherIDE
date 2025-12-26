"""
Run v4.2 Migration - Long-Term Memory
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
SQL_PATH = Path(__file__).parent / 'migrate_v4_2.sql'

def run_migration():
    """Run v4.2 migration"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 Running v4.2 Migration (Long-Term Memory)...")
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
        WHERE type='table' AND name IN ('deep_memory', 'error_patterns', 'concept_links')
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    
    if len(tables) == 3:
        print(f"✅ Migration complete!")
        print(f"   New tables: {tables}")
    else:
        print(f"❌ Migration failed - missing tables")
        print(f"   Found: {tables}")
    
    conn.close()

if __name__ == "__main__":
    run_migration()
