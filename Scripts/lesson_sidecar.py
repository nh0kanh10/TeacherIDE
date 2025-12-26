"""
Lesson Sidecar - Replace Inline Comment Injection
Creates .lessons.md sidecar files next to code files
"""
from pathlib import Path
from datetime import datetime
import sqlite3
import re

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'

def create_sidecar_lesson(
    code_file: str,
    line_number: int,
    lesson: str,
    context: str = None
):
    """
    Create or append lesson to sidecar file
    
    Args:
        code_file: Path to source code file
        line_number: Line number where lesson applies
        lesson: Lesson content
        context: Optional code snippet for context
    
    Returns:
        dict with sidecar path and lesson ID
    """
    code_path = Path(code_file)
    if not code_path.exists():
        raise FileNotFoundError(f"Code file not found: {code_file}")
    
    # Create sidecar path: file.py → file.py.lessons.md
    sidecar_path = Path(f"{code_file}.lessons.md")
    
    # Format lesson entry
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lesson_entry = f"""
## Line {line_number} - {timestamp}

{lesson}

**Location:** `{code_path.name}:{line_number}`
"""
    
    if context:
        lesson_entry += f"""
**Code Context:**
```
{context}
```
"""
    
    lesson_entry += "\n---\n"
    
    # Create or append to sidecar file
    if sidecar_path.exists():
        content = sidecar_path.read_text(encoding='utf-8')
        content += lesson_entry
    else:
        header = f"# Lessons for {code_path.name}\n\n"
        header += f"**File:** `{code_path.absolute()}`\n\n"
        header += "---\n"
        content = header + lesson_entry
    
    sidecar_path.write_text(content, encoding='utf-8')
    
    # Save metadata to database
    lesson_id = save_sidecar_metadata(code_file, line_number, lesson, str(sidecar_path))
    
    return {
        'status': 'ok',
        'sidecar_path': str(sidecar_path),
        'lesson_id': lesson_id,
        'line_number': line_number
    }

def save_sidecar_metadata(code_file: str, line_number: int, lesson: str, sidecar_path: str):
    """Save lesson metadata to database"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    # Check if table has new columns (migration-safe)
    cur.execute("PRAGMA table_info(knowledge_extracts)")
    columns = {row[1] for row in cur.fetchall()}
    
    if 'file_path' in columns:
        # New schema
        cur.execute("""
            INSERT INTO knowledge_extracts 
            (title, content, topic, file_path, line_number, obsidian_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            f"Lesson: {Path(code_file).name}:{line_number}",
            lesson[:500],  # Summary
            "Sidecar",
            code_file,
            line_number,
            sidecar_path
        ))
    else:
        # Old schema fallback
        cur.execute("""
            INSERT INTO knowledge_extracts (title, content, topic, obsidian_path)
            VALUES (?, ?, ?, ?)
        """, (
            f"Lesson: {Path(code_file).name}:{line_number}",
            lesson[:500],
            "Sidecar",
            sidecar_path
        ))
    
    lesson_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return lesson_id

def get_sidecar_lessons(code_file: str, line_number: int = None):
    """
    Get all lessons for a file, optionally filtered by line number
    
    Args:
        code_file: Path to source file
        line_number: Optional line number filter
    
    Returns:
        list of lessons from sidecar file
    """
    sidecar_path = Path(f"{code_file}.lessons.md")
    
    if not sidecar_path.exists():
        return []
    
    content = sidecar_path.read_text(encoding='utf-8')
    
    # Parse lessons (simple regex for now)
    pattern = r'## Line (\d+) - (.+?)\n\n(.+?)(?=\n## Line|\n---\nFile:|$)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    lessons = []
    for match in matches:
        lesson_line = int(match.group(1))
        timestamp = match.group(2)
        lesson_content = match.group(3).strip()
        
        if line_number is None or lesson_line == line_number:
            lessons.append({
                'line': lesson_line,
                'timestamp': timestamp,
                'content': lesson_content
            })
    
    return lessons

def list_files_with_sidecars(directory: str = "."):
    """List all code files that have sidecar lesson files"""
    dir_path = Path(directory)
    sidecar_files = list(dir_path.rglob("*.lessons.md"))
    
    files_with_lessons = []
    for sidecar in sidecar_files:
        # Remove .lessons.md to get original file
        original_name = str(sidecar)[:-11]  # Remove '.lessons.md'
        original_path = Path(original_name)
        
        if original_path.exists():
            lesson_count = len(get_sidecar_lessons(str(original_path)))
            files_with_lessons.append({
                'file': str(original_path),
                'sidecar': str(sidecar),
                'lessons': lesson_count
            })
    
    return files_with_lessons

def main():
    """CLI interface for sidecar lessons"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lesson Sidecar - IDE-native learning without code injection')
    parser.add_argument('command', choices=['create', 'list', 'show'])
    parser.add_argument('--file', help='Code file path')
    parser.add_argument('--line', type=int, help='Line number')
    parser.add_argument('--lesson', help='Lesson content')
    parser.add_argument('--context', help='Code context snippet')
    parser.add_argument('--dir', default='.', help='Directory to search')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        if not args.file or not args.line or not args.lesson:
            print("Error: --file, --line, and --lesson required for create")
            return 1
        
        result = create_sidecar_lesson(args.file, args.line, args.lesson, args.context)
        print(f"✅ Created lesson in: {result['sidecar_path']}")
        print(f"   Line: {result['line_number']}")
        print(f"   Lesson ID: {result['lesson_id']}")
    
    elif args.command == 'show':
        if not args.file:
            print("Error: --file required for show")
            return 1
        
        lessons = get_sidecar_lessons(args.file, args.line)
        if not lessons:
            print(f"No lessons found for {args.file}")
            if args.line:
                print(f"  (filtered by line {args.line})")
        else:
            print(f"\n📚 Lessons for {args.file}:\n")
            for lesson in lessons:
                print(f"Line {lesson['line']} - {lesson['timestamp']}")
                print(f"{lesson['content']}\n")
                print("-" * 60)
    
    elif args.command == 'list':
        files = list_files_with_sidecars(args.dir)
        if not files:
            print(f"No sidecar files found in {args.dir}")
        else:
            print(f"\n📁 Files with lessons in {args.dir}:\n")
            for item in files:
                print(f"  📄 {item['file']}")
                print(f"     Sidecar: {item['sidecar']}")
                print(f"     Lessons: {item['lessons']}")
                print()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
