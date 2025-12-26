"""
Quick Assessment Module - v3.0
Solves BKT "Cold Start" problem by initial skill evaluation

Creates baseline mastery probabilities for skill_mastery table
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'

# Assessment questions organized by skill
ASSESSMENT_QUESTIONS = {
    "python_basics": {
        "name": "Python Basics",
        "questions": [
            {
                "q": "What does this do? x = [i**2 for i in range(5)]",
                "options": ["A) List of squares 0-16", "B) Error", "C) Sum of squares", "D) Don't know"],
                "correct": "A",
                "skill": "list_comprehension"
            },
            {
                "q": "What's the output? print(type(lambda x: x*2))",
                "options": ["A) <class 'function'>", "B) <class 'lambda'>", "C) Error", "D) Don't know"],
                "correct": "A",
                "skill": "functions"
            },
            {
                "q": "What's a dict in Python?",
                "options": ["A) Key-value pairs", "B) Ordered list", "C) String", "D) Don't know"],
                "correct": "A",
                "skill": "dictionaries"
            }
        ]
    },
    
    "programming_fundamentals": {
        "name": "Programming Fundamentals",
        "questions": [
            {
                "q": "What's a variable?",
                "options": ["A) Storage for data", "B) A function", "C) A loop", "D) Don't know"],
                "correct": "A",
                "skill": "variables"
            },
            {
                "q": "What does a 'for loop' do?",
                "options": ["A) Repeat code", "B) Make decisions", "C) Store data", "D) Don't know"],
                "correct": "A",
                "skill": "for_loops"
            },
            {
                "q": "What's recursion?",
                "options": ["A) Function calls itself", "B) Infinite loop", "C) Type of variable", "D) Don't know"],
                "correct": "A",
                "skill": "recursion"
            }
        ]
    },
    
    "data_structures": {
        "name": "Data Structures",
        "questions": [
            {
                "q": "What's the time complexity of list.append()?",
                "options": ["A) O(1) average", "B) O(n)", "C) O(log n)", "D) Don't know"],
                "correct": "A",
                "skill": "lists"
            },
            {
                "q": "When would you use a set vs a list?",
                "options": ["A) Need unique items", "B) Need ordering", "C) Need duplicates", "D) Don't know"],
                "correct": "A",
                "skill": "sets"
            }
        ]
    }
}

def run_assessment(category="programming_fundamentals"):
    """
    Run quick assessment quiz
    Returns: dict of {skill_name: mastery_prob}
    """
    if category not in ASSESSMENT_QUESTIONS:
        print(f"❌ Category '{category}' not found")
        return {}
    
    quiz = ASSESSMENT_QUESTIONS[category]
    questions = quiz['questions']
    
    print("\n" + "=" * 60)
    print(f"📝 Quick Assessment: {quiz['name']}")
    print("=" * 60)
    print("\nThis helps the system understand your current skill level.")
    print("Answer honestly - there's no penalty for 'Don't know'!\n")
    
    skill_results = {}
    
    for i, item in enumerate(questions, 1):
        print(f"\nQuestion {i}/{len(questions)}:")
        print(f"  {item['q']}")
        for opt in item['options']:
            print(f"    {opt}")
        
        answer = input("\nYour answer (A/B/C/D): ").strip().upper()
        
        skill = item['skill']
        is_correct = (answer == item['correct'])
        
        # Initialize skill tracking
        if skill not in skill_results:
            skill_results[skill] = {"correct": 0, "total": 0}
        
        skill_results[skill]['total'] += 1
        if is_correct:
            skill_results[skill]['correct'] += 1
    
    # Calculate initial mastery probabilities
    mastery_probs = {}
    for skill, data in skill_results.items():
        # Simple formula: mastery = (correct + 1) / (total + 2)
        # Smoothing prevents 0 or 1 extremes
        mastery = (data['correct'] + 1) / (data['total'] + 2)
        mastery_probs[skill] = mastery
    
    print("\n" + "=" * 60)
    print("✅ Assessment Complete!")
    print("=" * 60)
    print("\n📊 Your Initial Skill Profile:")
    
    for skill, prob in mastery_probs.items():
        level = "Expert" if prob > 0.8 else "Proficient" if prob > 0.6 else "Learning" if prob > 0.4 else "Beginner"
        print(f"  {skill:<25} {prob:.0%} ({level})")
    
    # Save to database
    save_assessment_results(mastery_probs)
    
    return mastery_probs

def save_assessment_results(mastery_probs):
    """Save assessment results to skill_mastery table"""
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=30)
        cur = conn.cursor()
        
        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS skill_mastery (
                user_id INTEGER DEFAULT 1,
                skill_name TEXT,
                mastery_prob REAL,
                attempts INTEGER DEFAULT 1,
                correct INTEGER,
                last_practiced TIMESTAMP,
                PRIMARY KEY (user_id, skill_name)
            )
        """)
        
        # Insert/update mastery data
        for skill, prob in mastery_probs.items():
            cur.execute("""
                INSERT OR REPLACE INTO skill_mastery 
                (user_id, skill_name, mastery_prob, attempts, correct, last_practiced)
                VALUES (1, ?, ?, 1, ?, ?)
            """, (skill, prob, int(prob), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"\n💾 Saved {len(mastery_probs)} skill assessments to database")
    
    except Exception as e:
        print(f"\n⚠️  Error saving to database: {e}")

def get_all_assessed_skills():
    """Get all skills that have been assessed"""
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=30)
        cur = conn.cursor()
        
        cur.execute("SELECT skill_name, mastery_prob, last_practiced FROM skill_mastery ORDER BY mastery_prob DESC")
        results = cur.fetchall()
        conn.close()
        
        return [{"skill": r[0], "mastery": r[1], "last_practiced": r[2]} for r in results]
    
    except Exception:
        return []

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick Assessment - Solve BKT Cold Start')
    parser.add_argument('command', choices=['run', 'show'],
                       help='run: take assessment, show: show current skills')
    parser.add_argument('--category', default='programming_fundamentals',
                       choices=list(ASSESSMENT_QUESTIONS.keys()),
                       help='Assessment category')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        print("\n🎯 This assessment will take ~2 minutes")
        print("It helps the AI understand where you are so it can teach effectively.\n")
        
        input("Press Enter to start...")
        
        run_assessment(args.category)
        
        print("\n💡 Tip: Run assessments for other categories:")
        for cat in ASSESSMENT_QUESTIONS.keys():
            if cat != args.category:
                print(f"   python quick_assessment.py run --category {cat}")
        print()
    
    elif args.command == 'show':
        skills = get_all_assessed_skills()
        
        if not skills:
            print("\n❌ No assessments found. Run: python quick_assessment.py run")
            return 1
        
        print("\n" + "=" * 60)
        print("📊 Your Assessed Skills")
        print("=" * 60)
        print(f"\n{'Skill':<30} {'Mastery':<10} {'Last Practiced'}")
        print("-" * 60)
        
        for s in skills:
            print(f"{s['skill']:<30} {s['mastery']:.0%}       {s['last_practiced'][:10]}")
        
        print()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
