"""
File Tracker - Monitor file lifecycle events
Tracks opens, edits, errors per file for file-specific insights
"""
from pathlib import Path
import sqlite3
from datetime import datetime
import json

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'

def track_file_event(file_path: str, event_type: str):
    """
    Log file activity: open, edit, error, close
    Uses UPSERT (INSERT ... ON CONFLICT) for safe concurrent updates
    
    Args:
        file_path: Absolute path to file
        event_type: 'open' | 'edit' | 'error' | 'close'
    """
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    if event_type == 'open':
        # UPSERT: increment opened_count, update last_opened
        cur.execute("""
            INSERT INTO file_history (file_path, opened_count, last_opened)
            VALUES (?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(file_path) DO UPDATE SET
                opened_count = opened_count + 1,
                last_opened = CURRENT_TIMESTAMP
        """, (file_path,))
    
    elif event_type == 'error':
        # Increment error_count
        cur.execute("""
            INSERT INTO file_history (file_path, error_count)
            VALUES (?, 1)
            ON CONFLICT(file_path) DO UPDATE SET
                error_count = error_count + 1
        """, (file_path,))
    
    elif event_type == 'edit':
        # Just update last_opened (activity timestamp)
        cur.execute("""
            INSERT INTO file_history (file_path, last_opened)
            VALUES (?, CURRENT_TIMESTAMP)
            ON CONFLICT(file_path) DO UPDATE SET
                last_opened = CURRENT_TIMESTAMP
        """, (file_path,))
    
    conn.commit()
    conn.close()

def link_lesson_to_file(file_path: str, lesson_id: int):
    """
    Add lesson ID to file's lessons array (stored as JSON)
    """
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    # Get current lessons
    cur.execute("SELECT lessons FROM file_history WHERE file_path = ?", (file_path,))
    row = cur.fetchone()
    
    if row and row[0]:
        lessons = json.loads(row[0])
    else:
        lessons = []
    
    # Add new lesson if not already present
    if lesson_id not in lessons:
        lessons.append(lesson_id)
    
    # Update
    cur.execute("""
        UPDATE file_history SET lessons = ?
        WHERE file_path = ?
    """, (json.dumps(lessons), file_path))
    
    conn.commit()
    conn.close()

def get_file_insights(file_path: str) -> dict:
    """
    Get learning history and insights for a specific file
    
    Returns:
        dict with opened_count, error_count, lessons, common_mistakes
    """
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    # Get file history
    cur.execute("""
        SELECT opened_count, error_count, last_opened, lessons
        FROM file_history
        WHERE file_path = ?
    """, (file_path,))
    
    row = cur.fetchone()
    if not row:
        conn.close()
        return {
            'file_path': file_path,
            'opened_count': 0,
            'error_count': 0,
            'lessons': [],
            'errors': []
        }
    
    opened, errors, last_opened, lessons_json = row
    lessons = json.loads(lessons_json) if lessons_json else []
    
    # Get error history
    cur.execute("""
        SELECT error_type, error_message, timestamp, resolved
        FROM errors_log
        WHERE file_path = ?
        ORDER BY timestamp DESC
        LIMIT 10
    """, (file_path,))
    
    error_history = [
        {
            'type': row[0],
            'message': row[1],
            'timestamp': row[2],
            'resolved': bool(row[3])
        }
        for row in cur.fetchall()
    ]
    
    # Get lesson details
    if lessons:
        placeholders = ','.join(['?'] * len(lessons))
        cur.execute(f"""
            SELECT id, title, topic, obsidian_path
            FROM knowledge_extracts
            WHERE id IN ({placeholders})
        """, lessons)
        
        lesson_details = [
            {
                'id': row[0],
                'title': row[1],
                'topic': row[2],
                'path': row[3]
            }
            for row in cur.fetchall()
        ]
    else:
        lesson_details = []
    
    conn.close()
    
    return {
        'file_path': file_path,
        'opened_count': opened,
        'error_count': errors,
        'last_opened': last_opened,
        'lessons': lesson_details,
        'errors': error_history
    }

def get_problematic_files(limit: int = 10) -> list:
    """
    Get files with most errors (need attention)
    
    Returns:
        list of dicts with file_path, error_count
    """
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT file_path, error_count, opened_count
        FROM file_history
        WHERE error_count > 0
        ORDER BY error_count DESC
        LIMIT ?
    """, (limit,))
    
    results = [
        {
            'file_path': row[0],
            'error_count': row[1],
            'opened_count': row[2],
            'error_ratio': row[1] / max(row[2], 1)
        }
        for row in cur.fetchall()
    ]
    
    conn.close()
    return results

def main():
    """CLI interface for file tracking"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Track file lifecycle events')
    parser.add_argument('command', choices=['track', 'insights', 'problems'])
    parser.add_argument('--file', help='File path')
    parser.add_argument('--event', choices=['open', 'edit', 'error', 'close'],
                       help='Event type (for track command)')
    parser.add_argument('--limit', type=int, default=10, 
                       help='Limit for problems command')
    
    args = parser.parse_args()
    
    if args.command == 'track':
        if not args.file or not args.event:
            print("Error: --file and --event required for track command")
            return 1
        
        track_file_event(args.file, args.event)
        print(f"✅ Tracked: {args.file} - {args.event}")
    
    elif args.command == 'insights':
        if not args.file:
            print("Error: --file required for insights command")
            return 1
        
        insights = get_file_insights(args.file)
        print(f"\n📊 Insights for: {insights['file_path']}")
        print(f"   Opened: {insights['opened_count']} times")
        print(f"   Errors: {insights['error_count']}")
        print(f"   Lessons learned: {len(insights['lessons'])}")
        
        if insights['lessons']:
            print("\n   📚 Lessons:")
            for lesson in insights['lessons']:
                print(f"      - {lesson['title']} ({lesson['topic']})")
        
        if insights['errors']:
            print("\n   ⚠️  Recent errors:")
            for err in insights['errors'][:5]:
                status = '✓' if err['resolved'] else '✗'
                print(f"      {status} {err['type']}: {err['message'][:60]}...")
    
    elif args.command == 'problems':
        problems = get_problematic_files(args.limit)
        print(f"\n🔥 Top {args.limit} problematic files:\n")
        for i, file in enumerate(problems, 1):
            print(f"{i}. {file['file_path']}")
            print(f"   Errors: {file['error_count']} | Opens: {file['opened_count']} | Ratio: {file['error_ratio']:.1%}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
