"""
Error Listener - Production-Ready
Captures terminal errors and auto-creates lessons with file context
"""
import re
import json
from pathlib import Path
from datetime import datetime
import sqlite3
import sys

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'

# Multiline regex patterns for error parsing
ERROR_PATTERNS = {
    'python': re.compile(r'File "(.+?)", line (\d+).*?\n\s*(\w+Error): (.+)', re.DOTALL),
    'csharp': re.compile(r'(.+?\.cs)\((\d+),\d+\): error (CS\d+): (.+)'),
    'javascript': re.compile(r'(.+?\.js):(\d+)\s*\n.*?(\w+Error): (.+)', re.DOTALL)
}

def parse_terminal_error(output: str, language: str = None):
    """
    Parse error from terminal output
    If language not specified, try all patterns
    """
    languages = [language] if language else ERROR_PATTERNS.keys()
    
    for lang in languages:
        pattern = ERROR_PATTERNS.get(lang)
        if not pattern:
            continue
        match = pattern.search(output)
        if match:
            return {
                'file': match.group(1),
                'line': int(match.group(2)),
                'error_type': match.group(3),
                'message': match.group(4).strip(),
                'language': lang
            }
    return None

def save_error_to_db(errinfo: dict):
    """Save error to errors_log table"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO errors_log (file_path, line_number, error_type, error_message)
        VALUES (?, ?, ?, ?)
    """, (errinfo['file'], errinfo['line'], errinfo['error_type'], errinfo['message']))
    error_id = cur.lastrowid
    conn.commit()
    conn.close()
    return error_id

def create_lesson_from_error(errinfo: dict, ai_explanation: str):
    """
    Create knowledge entry from error
    Hook: Call AI to generate explanation before calling this
    """
    vault_dir = Path(__file__).parent.parent / '05_Extracted_Knowledge'
    vault_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = f"error_{Path(errinfo['file']).stem}_L{errinfo['line']}_{timestamp}.md"
    path = vault_dir / fname
    
    content = f"""# Error: {errinfo['error_type']} 

**File:** {errinfo['file']}:{errinfo['line']}
**Type:** {errinfo['error_type']}
**Language:** {errinfo['language']}

## Error Message
```
{errinfo['message']}
```

## Explanation
{ai_explanation}

## How to Fix
[AI should provide steps here]

## Pattern to Remember
[AI should extract pattern here]

---
*Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    path.write_text(content, encoding='utf-8')
    
    # Save metadata to knowledge_extracts table
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    cur = conn.cursor()
    
    # Check if table has new columns (migration-safe)
    cur.execute("PRAGMA table_info(knowledge_extracts)")
    columns = [row[1] for row in cur.fetchall()]
    
    if 'file_path' in columns:
        # New schema
        cur.execute("""
            INSERT INTO knowledge_extracts 
            (title, content, topic, file_path, line_number, error_type, obsidian_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"Error: {errinfo['error_type']}",
            content[:500],
            f"AutoError-{errinfo['language']}",
            errinfo['file'],
            errinfo['line'],
            errinfo['error_type'],
            str(path)
        ))
    else:
        # Old schema (fallback)
        cur.execute("""
            INSERT INTO knowledge_extracts (title, content, topic, obsidian_path)
            VALUES (?, ?, ?, ?)
        """, (
            f"Error: {errinfo['error_type']}",
            content[:500],
            "AutoError",
            str(path)
        ))
    
    lesson_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return {'path': str(path), 'lesson_id': lesson_id}

def main():
    """
    CLI usage:
    python Scripts/error_listener.py < failing_output.txt
    OR
    python Scripts/error_listener.py --file error_output.txt --language python
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='Path to error output file')
    parser.add_argument('--language', choices=['python', 'csharp', 'javascript'], 
                       help='Force specific language parser')
    args = parser.parse_args()
    
    # Read from stdin or file
    if args.file:
        output = Path(args.file).read_text(encoding='utf-8')
    else:
        output = sys.stdin.read()
    
    # Parse error
    errinfo = parse_terminal_error(output, args.language)
    
    if not errinfo:
        print("❌ No error pattern matched")
        return 1
    
    print(f"✅ Parsed error: {errinfo['error_type']} in {errinfo['file']}:{errinfo['line']}")
    
    # Save to database
    error_id = save_error_to_db(errinfo)
    print(f"📝 Saved to errors_log (ID: {error_id})")
    
    # Generate AI explanation (placeholder for now)
    # TODO: Call AI Agent to explain error
    ai_explanation = f"Auto-detected {errinfo['error_type']}. Human review needed for explanation."
    
    # Create lesson
    result = create_lesson_from_error(errinfo, ai_explanation)
    print(f"📚 Created lesson: {result['path']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
