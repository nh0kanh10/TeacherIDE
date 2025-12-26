"""
Run v4.3 Migration - Adaptive Teaching
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
SQL_PATH = Path(__file__).parent / 'migrate_v4_3.sql'

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 Running v4.3 Migration (Adaptive Teaching)...")
    
    with open(SQL_PATH, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    cursor.executescript(sql_script)
    conn.commit()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name IN ('teaching_effectiveness', 'style_preferences')
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    
    if len(tables) == 2:
        cursor.execute("SELECT COUNT(*) FROM style_preferences")
        styles_count = cursor.fetchone()[0]
        
        print(f"✅ Migration complete!")
        print(f"   Tables: {tables}")
        print(f"   Default styles: {styles_count}")
    else:
        print(f"❌ Migration failed")
    
    conn.close()

if __name__ == "__main__":
    run_migration()
