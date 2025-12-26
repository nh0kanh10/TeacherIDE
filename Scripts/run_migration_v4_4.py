"""
Run v4.4 Migration - Silent Assistant
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
SQL_PATH = Path(__file__).parent / 'migrate_v4_4.sql'

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 Running v4.4 Migration (Silent Assistant)...")
    
    with open(SQL_PATH, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    cursor.executescript(sql_script)
    conn.commit()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name = 'file_activity'
    """)
    
    if cursor.fetchone():
        print("✅ Migration complete!")
        print("   Table: file_activity")
    else:
        print("❌ Migration failed")
    
    conn.close()

if __name__ == "__main__":
    run_migration()
