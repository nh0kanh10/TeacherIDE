"""
Populate skills table from skill_graph.json
"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
GRAPH_PATH = Path(__file__).parent / 'skill_graph.json'

def populate_skills():
    """Populate skills table from skill graph"""
    
    # Load skill graph
    with open(GRAPH_PATH, 'r', encoding='utf-8') as f:
        graph = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    skills_to_insert = []
    skill_id_counter = 1
    
    # Extract skills from nested structure
    for lang_key in ['python', 'javascript', 'csharp']:
        if lang_key not in graph:
            continue
        
        lang_data = graph[lang_key]
        
        # Traverse categories (fundamentals, oop, etc.)
        for category_name, category_skills in lang_data.items():
            if not isinstance(category_skills, dict):
                continue
            
            # Each skill is a key with prereqs and complexity
            for skill_name, skill_info in category_skills.items():
                complexity = skill_info.get('complexity', 5) if isinstance(skill_info, dict) else 5
                
                skills_to_insert.append((
                    skill_id_counter,
                    skill_name,
                    lang_key,
                    complexity
                ))
                skill_id_counter += 1
    
    # Batch insert
    cursor.executemany('''
        INSERT OR IGNORE INTO skills (id, name, category, complexity)
        VALUES (?, ?, ?, ?)
    ''', skills_to_insert)
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM skills")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Populated {count} skills from skill graph")
    print(f"   Languages: python, javascript, csharp")
    print(f"   Sample skills: {[s[1] for s in skills_to_insert[:5]]}")
    return count

if __name__ == "__main__":
    populate_skills()
