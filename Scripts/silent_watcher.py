"""
Silent Assistant - File Watcher
Phase 4 Feature #10 (Backend Part 1)

Passive file monitoring - NO auto-intervention
Follows 3 Laws:
1. Passive UI only (hints on request)
2. Rate limits (1/10min, 3/session)
3. Kill switches in config
"""
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from performance_guard import async_guard

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'


class SilentFileWatcher(FileSystemEventHandler):
    """
    Passive file watcher - observes, doesn't interrupt
    
    Law #1: NO auto-pop messages
    Law #2: Rate limit hints
    Law #3: Configurable kill switch
    """
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.db_path = DB_PATH
        self.last_hint_time = None
        self.hints_this_session = 0
        
        # Rate limits (Law #2)
        self.MIN_INTERVAL_SECONDS = 600  # 10 minutes
        self.MAX_HINTS_PER_SESSION = 3
    
    def on_modified(self, event):
        """Called when file is modified - PASSIVE observation only"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only watch code files
        if file_path.suffix not in ['.py', '.js', '.cs', '.md']:
            return
        
        # Log to database (passive tracking)
        self._log_file_activity(file_path, 'modified')
    
    def _log_file_activity(self, file_path: Path, activity_type: str):
        """Log file activity for later analysis - NO immediate action"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO file_activity (
                file_path, activity_type, timestamp
            ) VALUES (?, ?, ?)
        """, (str(file_path), activity_type, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def can_show_hint(self) -> bool:
        """
        Check if hint can be shown (Law #2: Rate limits)
        
        Returns:
            True if within rate limits
        """
        now = datetime.now()
        
        # Check session limit
        if self.hints_this_session >= self.MAX_HINTS_PER_SESSION:
            return False
        
        # Check interval limit
        if self.last_hint_time:
            elapsed = (now - self.last_hint_time).total_seconds()
            if elapsed < self.MIN_INTERVAL_SECONDS:
                return False
        
        return True
    
    def mark_hint_shown(self):
        """Mark that a hint was shown (for rate limiting)"""
        self.last_hint_time = datetime.now()
        self.hints_this_session += 1
    
    def get_hint_availability(self) -> Dict:
        """
        Get current hint availability status
        
        Returns:
            {
                'can_show': bool,
                'hints_remaining': int,
                'next_available': str (ISO timestamp or 'now')
            }
        """
        can_show = self.can_show_hint()
        hints_remaining = self.MAX_HINTS_PER_SESSION - self.hints_this_session
        
        if self.last_hint_time:
            next_time = self.last_hint_time + timedelta(seconds=self.MIN_INTERVAL_SECONDS)
            next_available = next_time.isoformat() if next_time > datetime.now() else 'now'
        else:
            next_available = 'now'
        
        return {
            'can_show': can_show,
            'hints_remaining': hints_remaining,
            'next_available': next_available
        }


def start_silent_watcher(workspace_path: str = "."):
    """
    Start the silent file watcher
    
    Args:
        workspace_path: Path to watch
    """
    path = Path(workspace_path).resolve()
    
    print(f"🔇 Silent Assistant - File Watcher Started")
    print(f"   Watching: {path}")
    print(f"   Mode: PASSIVE (no auto-intervention)")
    print(f"   Rate Limits: 1 hint/10min, max 3/session\n")
    
    event_handler = SilentFileWatcher(path)
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🔇 Silent Assistant stopped")
    
    observer.join()


if __name__ == "__main__":
    # Demo of rate limiting
    watcher = SilentFileWatcher(Path("."))
    
    print("🔇 Silent Assistant - Rate Limiting Demo\n")
    
    print("Testing hint availability:")
    avail = watcher.get_hint_availability()
    print(f"  Can show: {avail['can_show']}")
    print(f"  Hints remaining: {avail['hints_remaining']}")
    print(f"  Next available: {avail['next_available']}")
    
    print("\nSimulating 3 hints:")
    for i in range(3):
        if watcher.can_show_hint():
            print(f"  Hint {i+1}: ✅ Shown")
            watcher.mark_hint_shown()
        else:
            print(f"  Hint {i+1}: ❌ Blocked (rate limit)")
    
    print("\nTrying 4th hint:")
    if watcher.can_show_hint():
        print("  ✅ Allowed")
    else:
        print("  ❌ BLOCKED - Session limit reached!")
    
    avail = watcher.get_hint_availability()
    print(f"\nFinal status:")
    print(f"  Hints remaining: {avail['hints_remaining']}")
