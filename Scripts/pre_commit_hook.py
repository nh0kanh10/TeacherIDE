#!/usr/bin/env python
"""
Pre-commit hook: Strip AI-Coach comments before committing
Install: Copy to .git/hooks/pre-commit and chmod +x
"""
import sys
import re
from pathlib import Path

MARKER_PATTERN = re.compile(r'(#|//)\s*AI-COACH-(START|END)', re.IGNORECASE)

def strip_ai_comments(file_path: Path) -> bool:
    """
    Remove AI-Coach comment blocks from file
    Returns True if file was modified
    """
    if not file_path.exists():
        return False
    
    lines = file_path.read_text(encoding='utf-8').splitlines()
    new_lines = []
    in_ai_block = False
    modified = False
    
    for line in lines:
        if 'AI-COACH-START' in line or 'AI-COACH' in line and 'START' in line:
            in_ai_block = True
            modified = True
            continue
        
        if 'AI-COACH-END' in line:
            in_ai_block = False
            continue
        
        if not in_ai_block:
            new_lines.append(line)
    
    if modified:
        file_path.write_text('\n'.join(new_lines), encoding='utf-8')
        return True
    
    return False

def main():
    """Process staged files"""
    import subprocess
    import json
    
    # Check if stripping is enabled in config
    config_path = Path('.ai_coach/config.json')
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding='utf-8'))
        if not config.get('injection', {}).get('strip_on_commit', True):
            # User disabled stripping
            return 0
    
    # Get staged files
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return 0
    
    staged_files = result.stdout.strip().split('\n')
    stripped_files = []
    
    for file_path_str in staged_files:
        if not file_path_str:
            continue
        
        file_path = Path(file_path_str)
        
        # Only process code files
        if file_path.suffix not in ['.py', '.cs', '.js', '.java', '.cpp', '.c', '.ts']:
            continue
        
        if strip_ai_comments(file_path):
            stripped_files.append(str(file_path))
            # Re-stage modified file
            subprocess.run(['git', 'add', str(file_path)])
    
    if stripped_files:
        print("\n✂️  Stripped AI-Coach comments from:")
        for f in stripped_files:
            print(f"   - {f}")
        print("\n✅ Files re-staged. Commit will proceed without AI comments.\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
