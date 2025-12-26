"""
Teaching Helper - v3.0 Enhanced Persistence Layer
Handles saving knowledge, skill mastery, ROI tracking, and profile-aware persistence
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
CONFIG_PATH = Path(__file__).parent.parent / '.ai_coach' / 'config.json'
PROFILE_PATH = Path(__file__).parent.parent / '.ai_coach' / 'user_profile.json'
VAULT_PATH = Path(__file__).parent.parent / '05_Extracted_Knowledge'

def load_config():
    """Load configuration"""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    return {}

def load_profile():
    """Load user profile (v3.0)"""
    if PROFILE_PATH.exists():
        return json.loads(PROFILE_PATH.read_text(encoding='utf-8'))
    return None


def save_knowledge_block(title: str, content: str, topic: str, 
                        skill_name: str = None, is_practice: bool = False, 
                        practice_correct: bool = None) -> str:
    """
    Save knowledge block với v3.0 enhancements
    
    New in v3.0:
    - Updates skill_mastery if skill_name provided
    - Triggers ROI calculation if new skill
    - Saves analogies to cache if detected
    - Profile-aware storage location
    
    Args:
        title: Lesson title
        content: Lesson content
        topic: Topic/category
        skill_name: Related skill (v3.0) for BKT tracking
        is_practice: Whether this is practice attempt (v3.0)
        practice_correct: If practice, was it correct? (v3.0)
    
    Returns:
        str: Path to saved markdown file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{timestamp}_{safe_title}.md"
    
    # Determine storage location based on topic
    if topic in ["python", "javascript", "csharp"]:
        filepath = VAULT_PATH / "01_Programming" / filename
    elif topic in ["english", "japanese", "korean"]:
        filepath = VAULT_PATH / "02_Languages" / filename  
    elif topic in ["productivity", "career", "communication"]:
        filepath = VAULT_PATH / "03_Soft_Skills" / filename
    else:
        filepath = VAULT_PATH / filename
    
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Write markdown file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"**Topic:** {topic}\n")
        f.write(f"**Extracted:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        if skill_name:
            f.write(f"**Skill:** {skill_name}\n")
        f.write("\n---\n\n")
        f.write(content)
    
    # Save to SQLite
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO knowledge_extracts (title, content, topic, obsidian_path)
            VALUES (?, ?, ?, ?)
        """, (title, content, topic, str(filepath)))
        lesson_id = cursor.lastrowid
        
        # v3.0: Update skill mastery if provided
        if skill_name and is_practice and practice_correct is not None:
            try:
                from knowledge_tracer import KnowledgeTracer
                tracer = KnowledgeTracer()
                new_mastery = tracer.update_mastery(skill_name, practice_correct)
                print(f"📊 Updated {skill_name}: mastery → {new_mastery:.0%}")
            except Exception as e:
                print(f"⚠️  Skill tracking failed: {e}")
        
        # v3.0: Trigger ROI calculation if new skill
        if skill_name:
            try:
                from skill_roi_calculator import calculate_roi
                roi = calculate_roi(skill_name, use_cache=True)
                if roi.get('status') != 'error':
                    print(f"💰 {skill_name} ROI: {roi['roi_score']:,.0f}")
            except:
                pass
        
        conn.commit()
        conn.close()
        
        print(f"✅ Saved: {filepath}")
        return str(filepath)
        
    except Exception as e:
        print(f"❌ Database save failed: {e}")
        return str(filepath)


def save_analogy(target_concept: str, source_domain: str, analogy_text: str, 
                quality_score: float = 0.0) -> bool:
    """
    Save generated analogy to cache (v3.0)
    
    Args:
        target_concept: Programming concept
        source_domain: User's familiar domain
        analogy_text: Generated analogy
        quality_score: User rating (0-5)
    
    Returns:
        bool: Success
    """
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT OR REPLACE INTO analogies
            (target_concept, source_domain, analogy_text, quality_score, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (target_concept, source_domain, analogy_text, quality_score, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Cached analogy: {target_concept} ({source_domain})")
        return True
    
    except Exception as e:
        print(f"❌ Analogy save failed: {e}")
        return False


def update_profile(updates: dict) -> bool:
    """Update user profile với thông tin mới"""
    try:
        if PROFILE_PATH.exists():
            with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                profile = data.get('user_profile', {})
        else:
            profile = {}
        
        # Generic update logic
        for section, content in updates.items():
            if section not in profile:
                profile[section] = {}
            
            if isinstance(profile[section], dict) and isinstance(content, dict):
                profile[section].update(content)
            elif isinstance(profile[section], list) and isinstance(content, list):
                # Append unique items
                for item in content:
                    if item not in profile[section]:
                        profile[section].append(item)
        
        # Save back
        with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({"user_profile": profile}, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False

def log_interaction(user_msg: str, ai_response: str, topic: str = None):
    """Ghi log tương tác vào database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO interaction_log (user_message, ai_response, topic, session_id)
            VALUES (?, ?, ?, ?)
        """, (user_msg, ai_response[:500], topic, f"session_{datetime.now().strftime('%Y%m%d')}"))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging interaction: {e}")
        return False

def update_progress(topic_name: str, percent: int):
    """Cập nhật tiến độ học topic"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Find or create topic
        cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
        result = cursor.fetchone()
        
        if result:
            topic_id = result[0]
        else:
            cursor.execute("INSERT INTO topics (name) VALUES (?)", (topic_name,))
            topic_id = cursor.lastrowid
        
        # Update progress
        cursor.execute("""
            INSERT OR REPLACE INTO progress (topic_id, progress_percent, last_studied)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (topic_id, percent))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating progress: {e}")
        return False

def main():
    """CLI for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Teaching Helper v3.0')
    parser.add_argument('command', choices=['save', 'analogy'],
                       help='save: save knowledge, analogy: save analogy')
    parser.add_argument('--title', help='Lesson title')
    parser.add_argument('--content', help='Lesson content')
    parser.add_argument('--topic', default='general', help='Topic')
    parser.add_argument('--skill', help='Related skill (v3.0)')
    parser.add_argument('--correct', action='store_true', help='Practice was correct')
    
    args = parser.parse_args()
    
    if args.command == 'save':
        if not args.title or not args.content:
            print("❌ --title and --content required")
            return 1
        
        result = save_knowledge_block(
            args.title, 
            args.content, 
            args.topic,
            skill_name=args.skill,
            is_practice=args.skill is not None,
            practice_correct=args.correct if args.skill else None
        )
        
        print(f"\n📄 Saved to: {result}")
    
    elif args.command == 'analogy':
        print("Use analogy_generator.py directly for analogy management")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
