"""
Vault Watcher - Sync Obsidian Markdown (Master) to SQLite (Index)
Monitors 05_Extracted_Knowledge/ for changes and updates database
"""
from pathlib import Path
import sqlite3
import time
import re
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️  Warning: watchdog not installed. Run: pip install watchdog")

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
VAULT_PATH = Path(__file__).parent.parent / '05_Extracted_Knowledge'

class VaultEventHandler(FileSystemEventHandler):
    """Handle file system events in knowledge vault"""
    
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        print(f"📝 New file: {event.src_path}")
        sync_file_to_db(event.src_path, is_new=True)
    
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        print(f"✏️  Modified: {event.src_path}")
        sync_file_to_db(event.src_path, is_new=False)
    
    def on_deleted(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        print(f"🗑️  Deleted: {event.src_path}")
        mark_deleted_in_db(event.src_path)
    
    def on_moved(self, event):
        if event.is_directory or not event.dest_path.endswith('.md'):
            return
        print(f"📦 Moved: {event.src_path} → {event.dest_path}")
        update_file_path_in_db(event.src_path, event.dest_path)

def parse_markdown_metadata(content: str):
    """
    Extract metadata from markdown content
    Returns: dict with title, topic, etc.
    """
    metadata = {}
    
    # Extract title (first # heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    
    # Extract topic from **Topic:** pattern
    topic_match = re.search(r'\*\*Topic:\*\*\s*(.+)', content)
    if topic_match:
        metadata['topic'] = topic_match.group(1).strip()
    
    # Extract file/line if error lesson
    file_match = re.search(r'\*\*File:\*\*\s*(.+?):(\d+)', content)
    if file_match:
        metadata['file_path'] = file_match.group(1).strip()
        metadata['line_number'] = int(file_match.group(2))
    
    # Extract error type
    error_match = re.search(r'\*\*Type:\*\*\s*(\w+)', content)
    if error_match:
        metadata['error_type'] = error_match.group(1).strip()
    
    return metadata

def sync_file_to_db(markdown_path: str, is_new: bool = False):
    """
    Sync markdown file to database
    Markdown = Source of Truth
    """
    path = Path(markdown_path)
    if not path.exists():
        return
    
    # Read content
    content = path.read_text(encoding='utf-8')
    metadata = parse_markdown_metadata(content)
    
    # Extract summary (first 500 chars)
    summary = content[:500]
    
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    # Check if entry exists by obsidian_path
    cur.execute("SELECT id FROM knowledge_extracts WHERE obsidian_path = ?", (str(path),))
    existing = cur.fetchone()
    
    if existing:
        # Update existing
        cur.execute("""
            UPDATE knowledge_extracts
            SET title = ?, content = ?, topic = ?, file_path = ?, line_number = ?, error_type = ?
            WHERE obsidian_path = ?
        """, (
            metadata.get('title', path.stem),
            summary,
            metadata.get('topic', 'General'),
            metadata.get('file_path'),
            metadata.get('line_number'),
            metadata.get('error_type'),
            str(path)
        ))
        print(f"  ✅ Updated DB entry ID: {existing[0]}")
    else:
        # Insert new
        cur.execute("""
            INSERT INTO knowledge_extracts 
            (title, content, topic, file_path, line_number, error_type, obsidian_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata.get('title', path.stem),
            summary,
            metadata.get('topic', 'General'),
            metadata.get('file_path'),
            metadata.get('line_number'),
            metadata.get('error_type'),
            str(path)
        ))
        print(f"  ✅ Created DB entry ID: {cur.lastrowid}")
    
    conn.commit()
    conn.close()

def mark_deleted_in_db(markdown_path: str):
    """Remove DB entry when markdown file deleted"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    cur.execute("DELETE FROM knowledge_extracts WHERE obsidian_path = ?", (markdown_path,))
    deleted_count = cur.rowcount
    
    conn.commit()
    conn.close()
    
    if deleted_count > 0:
        print(f"  ✅ Removed {deleted_count} DB entry(ies)")

def update_file_path_in_db(old_path: str, new_path: str):
    """Update path when file moved/renamed"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE knowledge_extracts SET obsidian_path = ? WHERE obsidian_path = ?
    """, (new_path, old_path))
    
    conn.commit()
    conn.close()
    print(f"  ✅ Updated path in DB")

def initial_sync():
    """Sync all existing markdown files to DB"""
    print("🔄 Initial vault sync...")
    
    markdown_files = list(VAULT_PATH.rglob("*.md"))
    print(f"   Found {len(markdown_files)} markdown files")
    
    for md_file in markdown_files:
        try:
            sync_file_to_db(str(md_file), is_new=True)
        except Exception as e:
            print(f"   ⚠️  Error syncing {md_file}: {e}")
    
    print("✅ Initial sync complete")

def start_watcher():
    """Start watching vault for changes"""
    if not WATCHDOG_AVAILABLE:
        print("❌ Cannot start watcher: watchdog not installed")
        return
    
    if not VAULT_PATH.exists():
        print(f"❌ Vault path not found: {VAULT_PATH}")
        return
    
    print(f"👁️  Watching vault: {VAULT_PATH}")
    print("   Press Ctrl+C to stop")
    
    event_handler = VaultEventHandler()
    observer = Observer()
    observer.schedule(event_handler, str(VAULT_PATH), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n⏹️  Watcher stopped")
    
    observer.join()

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Vault Watcher - Sync Markdown to SQLite')
    parser.add_argument('command', choices=['sync', 'watch'], 
                       help='sync: one-time sync, watch: continuous monitoring')
    
    args = parser.parse_args()
    
    if args.command == 'sync':
        initial_sync()
    elif args.command == 'watch':
        # Do initial sync first
        initial_sync()
        # Then start watching
        start_watcher()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
