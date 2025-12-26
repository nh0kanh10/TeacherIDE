"""
Migration v3 Runner - Cognitive Teaching System
Apply schema v3: user profile, skill ROI, BKT, analogies
"""
import sqlite3
from pathlib import Path
import sys

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
MIGRATE_V3_SQL = Path(__file__).parent / 'migrate_v3.sql'

def get_current_version(conn):
    """Get current schema version"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT MAX(version) FROM schema_version")
        result = cur.fetchone()
        return result[0] if result[0] else 0
    except sqlite3.OperationalError:
        return 0

def run_migration_v3():
    """Run migration v3"""
    print("=" * 60)
    print("Migration v3: Cognitive Teaching System")
    print("=" * 60)
    print(f"📊 Database: {DB_PATH}\n")
    
    if not DB_PATH.exists():
        print("❌ Database not found. Run migration v1 first.")
        return False
    
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    
    # Check current version
    current_version = get_current_version(conn)
    print(f"   Current schema version: {current_version}")
    
    if current_version >= 3:
        print("   ✅ Database already at v3 or higher")
        conn.close()
        return True
    
    if current_version < 2:
        print("   ⚠️  Recommended: Run migration v2 first")
        print("   Continuing anyway...")
    
    print(f"   🔄 Applying migration v3...")
    
    # Run SQL migration
    if MIGRATE_V3_SQL.exists():
        migration_sql = MIGRATE_V3_SQL.read_text(encoding='utf-8')
        conn.executescript(migration_sql)
        print("   ✅ Executed migrate_v3.sql")
    else:
        print(f"   ❌ migrate_v3.sql not found at {MIGRATE_V3_SQL}")
        conn.close()
        return False
    
    # Verify final version
    final_version = get_current_version(conn)
    print(f"\n   ✅ Migration complete! Schema version: {final_version}")
    
    conn.close()
    return True

def verify_migration_v3():
    """Verify v3 migration success"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    required_tables = [
        'user_profile',
        'skill_roi', 
        'skill_mastery',
        'skill_dependencies',
        'analogies'
    ]
    
    required_views = ['v_top_roi_skills', 'v_weak_skills']
    
    print("\n🔍 Verifying migration v3:")
    
    all_good = True
    
    # Check tables
    for table in required_tables:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cur.fetchone():
            print(f"   ✅ Table exists: {table}")
        else:
            print(f"   ❌ Missing table: {table}")
            all_good = False
    
    # Check views
    for view in required_views:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='view' AND name=?", (view,))
        if cur.fetchone():
            print(f"   ✅ View exists: {view}")
        else:
            print(f"   ⚠️  Missing view: {view}")
    
    # Check indexes
    indexes = ['idx_skill_mastery_prob', 'idx_skill_roi_score', 'idx_analogies_quality']
    for index in indexes:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index,))
        if cur.fetchone():
            print(f"   ✅ Index exists: {index}")
    
    conn.close()
    return all_good

def populate_initial_data():
    """Populate initial skill dependencies (Python basics)"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    # Basic Python skill graph
    dependencies = [
        ('list_comprehension', 'for_loops', 1.0),
        ('list_comprehension', 'lists', 0.8),
        ('recursion', 'functions', 1.0),
        ('recursion', 'conditionals', 0.8),
        ('classes', 'functions', 0.9),
        ('classes', 'dictionaries', 0.6),
        ('decorators', 'functions', 1.0),
        ('generators', 'functions', 0.9),
        ('async_await', 'functions', 1.0),
    ]
    
    for skill, req, strength in dependencies:
        cur.execute("""
            INSERT OR IGNORE INTO skill_dependencies (skill_name, requires_skill, strength)
            VALUES (?, ?, ?)
        """, (skill, req, strength))
    
    conn.commit()
    conn.close()
    
    print(f"\n   ✅ Populated {len(dependencies)} skill dependencies")

if __name__ == "__main__":
    success = run_migration_v3()
    
    if success:
        verify_migration_v3()
        
        print("\n🌱 Populating initial data...")
        populate_initial_data()
        
        print("\n✅ Migration v3 completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Run: python Scripts/profile_builder.py build")
        print("   2. Run: python Scripts/quick_assessment.py run")
        print("   3. Run: python Scripts/skill_roi_calculator.py list")
        sys.exit(0)
    else:
        print("\n❌ Migration v3 failed!")
        sys.exit(1)
