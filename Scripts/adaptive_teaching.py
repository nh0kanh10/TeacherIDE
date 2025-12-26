"""
Adaptive Teaching Style System
Phase 2 Feature #6

Uses Epsilon-Greedy algorithm (NOT Thompson Sampling - simpler for Phase 2)

Teaching Styles:
- visual: Diagrams, charts, visual explanations
- hands_on: Coding exercises, practice problems
- theoretical: Conceptual explanations
- example_based: Real-world examples
- analogy: Analogies from user background
"""
import sqlite3
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from performance_guard import async_guard

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'

# Epsilon-Greedy parameters
EPSILON = 0.2  # 20% exploration, 80% exploitation


class AdaptiveTeachingSystem:
    """
    Chooses optimal teaching style using Epsilon-Greedy
    
    Simpler than Thompson Sampling per expert feedback
    """
    
    def __init__(self, db_path: Path = DB_PATH, epsilon: float = EPSILON):
        self.db_path = db_path
        self.epsilon = epsilon
    
    def choose_teaching_style(self, skill_name: str = None) -> str:
        """
        Choose teaching style using Epsilon-Greedy
        
        Args:
            skill_name: Optional skill to consider
            
        Returns:
            Teaching style name
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current effectiveness scores
        cursor.execute("""
            SELECT teaching_style, avg_effectiveness, sample_size
            FROM style_preferences
            ORDER BY avg_effectiveness DESC
        """)
        
        styles = cursor.fetchall()
        conn.close()
        
        if random.random() < self.epsilon:
            # Explore: Random style
            return random.choice([s[0] for s in styles])
        else:
            # Exploit: Best style
            return styles[0][0]  # Highest effectiveness
    
    @async_guard
    def record_effectiveness(self, teaching_style: str, skill_name: str,
                           mastery_before: float, mastery_after: float):
        """
        Record teaching effectiveness and update preferences
        
        Args:
            teaching_style: Style used
            skill_name: Skill taught
            mastery_before: Mastery before teaching
            mastery_after: Mastery after teaching
        """
        improvement = mastery_after - mastery_before
        effectiveness_score = improvement  # Simple for now
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save effectiveness record
        cursor.execute("""
            INSERT INTO teaching_effectiveness (
                teaching_style, skill_name, mastery_before, mastery_after,
                improvement, effectiveness_score
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (teaching_style, skill_name, mastery_before, mastery_after,
              improvement, effectiveness_score))
        
        # Update style preferences (running average)
        cursor.execute("""
            SELECT avg_effectiveness, sample_size
            FROM style_preferences
            WHERE teaching_style = ?
        """, (teaching_style,))
        
        row = cursor.fetchone()
        
        if row:
            old_avg, old_n = row
            new_n = old_n + 1
            # Incremental average update
            new_avg = old_avg + (effectiveness_score - old_avg) / new_n
            
            cursor.execute("""
                UPDATE style_preferences
                SET avg_effectiveness = ?,
                    sample_size = ?,
                    last_updated = ?
                WHERE teaching_style = ?
            """, (new_avg, new_n, datetime.now().isoformat(), teaching_style))
        
        conn.commit()
        conn.close()
    
    def get_style_rankings(self) -> Dict[str, Dict]:
        """Get current style rankings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT teaching_style, avg_effectiveness, sample_size
            FROM style_preferences
            ORDER BY avg_effectiveness DESC
        """)
        
        rankings = {}
        for row in cursor.fetchall():
            rankings[row['teaching_style']] = {
                'effectiveness': row['avg_effectiveness'],
                'samples': row['sample_size']
            }
        
        conn.close()
        return rankings


if __name__ == "__main__":
    # Demo
    system = AdaptiveTeachingSystem()
    
    print("🎓 Adaptive Teaching Demo\n")
    
    # Simulate teaching sessions
    sessions = [
        ('hands_on', 'Python Functions', 0.5, 0.8),
        ('visual', 'Python Functions', 0.6, 0.7),
        ('hands_on', 'Python Classes', 0.4, 0.7),
        ('theoretical', 'Python Classes', 0.4, 0.5),
        ('example_based', 'Python Loops', 0.5, 0.75),
    ]
    
    print("Recording teaching sessions...")
    for style, skill, before, after in sessions:
        system.record_effectiveness(style, skill, before, after)
        print(f"  {style}: {skill} ({before:.0%} → {after:.0%})")
    
    print("\n📊 Style Rankings:")
    rankings = system.get_style_rankings()
    for style, data in rankings.items():
        print(f"  {style}: {data['effectiveness']:.2f} ({data['samples']} samples)")
    
    print("\n🎯 Epsilon-Greedy Selection (5 choices):")
    for i in range(5):
        chosen = system.choose_teaching_style()
        print(f"  Choice {i+1}: {chosen}")
