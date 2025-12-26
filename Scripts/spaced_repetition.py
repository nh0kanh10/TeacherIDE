"""
Spaced Repetition Manager - Integration layer for FSRS v5
Connects FSRS algorithm với database và teaching workflow
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json

from fsrs_v5 import FSRS, Card as FSRSCard, Rating, State
from event_bus import get_event_bus, EventType, emit_skill_update
from performance_guard import async_guard

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'


class SpacedRepetitionManager:
    """
    Manages spaced repetition for skills using FSRS v5
    
    Features:
    - Automatic scheduling based on review performance
    - Integration with skill_mastery table
    - Event-driven updates
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.scheduler = FSRS()
        self.event_bus = get_event_bus()
        
        # Subscribe to skill mastery updates
        self.event_bus.subscribe(EventType.SKILL_MASTERY_UPDATED, self._on_skill_updated)
    
    @async_guard
    def get_due_reviews(self, user_id: int = 1, limit: int = 20) -> List[Dict]:
        """Get skills due for review"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
        SELECT 
            sr.card_id,
            s.name as skill_name,
            sr.stability,
            sr.difficulty,
            sr.due,
            sr.state,
            sm.mastery_prob
        FROM spaced_repetition sr
        JOIN skills s ON sr.skill_id = s.id
        LEFT JOIN skill_mastery sm ON s.name = sm.skill_name
        WHERE sr.due <= datetime('now')
        ORDER BY sr.due ASC
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        reviews = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return reviews
    
    @async_guard
    def review_skill(self, skill_name: str, rating: int, user_id: int = 1) -> Dict:
        """
        Process a review and update scheduling
        
        Args:
            skill_name: Name of skill reviewed
            rating: 1-4 (Again, Hard, Good, Easy)
            user_id: User ID
            
        Returns:
            Updated card state
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get skill_id
        cursor.execute("SELECT id FROM skills WHERE name = ?", (skill_name,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Skill '{skill_name}' not found")
        skill_id = row[0]
        
        # Get or create FSRS card
        cursor.execute("""
            SELECT * FROM spaced_repetition 
            WHERE skill_id = ? AND user_id = ?
        """, (skill_id, user_id))
        
        row = cursor.fetchone()
        
        if row:
            # Existing card
            card = FSRSCard(card_id=row[0])
            card.difficulty = row[3]
            card.stability = row[4]
            card.elapsed_days = row[5]
            card.scheduled_days = row[6]
            card.reps = row[7]
            card.lapses = row[8]
            card.state = row[9]
            card.last_review = datetime.fromisoformat(row[10]) if row[10] else None
            card.due = datetime.fromisoformat(row[11]) if row[11] else None
        else:
            # New card
            card = FSRSCard()
            card.card_id = None
        
        # Process review with FSRS v5
        updated_card = self.scheduler.review_card(card, rating)
        
        # Save to database
        if card.card_id:
            # Update existing
            cursor.execute("""
                UPDATE spaced_repetition SET
                    stability = ?,
                    difficulty = ?,
                    elapsed_days = ?,
                    scheduled_days = ?,
                    reps = ?,
                    lapses = ?,
                    state = ?,
                    last_review = ?,
                    due = ?
                WHERE card_id = ?
            """, (
                updated_card.stability,
                updated_card.difficulty,
                updated_card.elapsed_days,
                updated_card.scheduled_days,
                updated_card.reps,
                updated_card.lapses,
                updated_card.state,
                updated_card.last_review.isoformat(),
                updated_card.due.isoformat(),
                updated_card.card_id
            ))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO spaced_repetition (
                    user_id, skill_id, stability, difficulty,
                    elapsed_days, scheduled_days, reps, lapses,
                    state, last_review, due
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, skill_id,
                updated_card.stability,
                updated_card.difficulty,
                updated_card.elapsed_days,
                updated_card.scheduled_days,
                updated_card.reps,
                updated_card.lapses,
                updated_card.state,
                updated_card.last_review.isoformat(),
                updated_card.due.isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        # Emit event
        correct = rating > Rating.AGAIN
        self.event_bus.publish(EventType.REVIEW_DONE, {
            'skill_name': skill_name,
            'rating': rating,
            'correct': correct,
            'new_stability': updated_card.stability,
            'new_difficulty': updated_card.difficulty,
            'next_review_days': updated_card.scheduled_days
        })
        
        return updated_card.to_dict()
    
    def _on_skill_updated(self, event_data: Dict):
        """Event listener: Update FSRS when skill mastery changes"""
        # We could auto-trigger review here if needed
        pass
    
    @async_guard
    def get_review_stats(self, user_id: int = 1) -> Dict:
        """Get overview of review schedule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_cards,
                SUM(CASE WHEN due <= datetime('now') THEN 1 ELSE 0 END) as due_now,
                SUM(CASE WHEN state = ? THEN 1 ELSE 0 END) as new_cards,
                AVG(stability) as avg_stability,
                AVG(difficulty) as avg_difficulty
            FROM spaced_repetition
            WHERE user_id = ?
        """, (State.NEW, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_cards': row[0] or 0,
            'due_now': row[1] or 0,
            'new_cards': row[2] or 0,
            'avg_stability_days': round(row[3], 1) if row[3] else 0,
            'avg_difficulty': round(row[4], 1) if row[4] else 0
        }


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Spaced Repetition Manager - FSRS v5')
    parser.add_argument('action', choices=['due', 'review', 'stats'], 
                       help='Action to perform')
    parser.add_argument('--skill', help='Skill name for review')
    parser.add_argument('--rating', type=int, choices=[1,2,3,4],
                       help='Rating: 1=Again, 2=Hard, 3=Good, 4=Easy')
    parser.add_argument('--limit', type=int, default=20,
                       help='Limit for due reviews')
    
    args = parser.parse_args()
    
    manager = SpacedRepetitionManager()
    
    if args.action == 'due':
        reviews = manager.get_due_reviews(limit=args.limit)
        print(f"\n📚 Due Reviews: {len(reviews)}\n")
        for r in reviews:
            print(f"  🔹 {r['skill_name']}")
            print(f"     Difficulty: {r['difficulty']:.1f} | Stability: {r['stability']:.1f} days")
            print(f"     Mastery: {r['mastery_prob']:.0%}" if r['mastery_prob'] else "")
            print()
    
    elif args.action == 'review':
        if not args.skill or args.rating is None:
            print("Error: --skill and --rating required for review")
        else:
            result = manager.review_skill(args.skill, args.rating)
            print(f"\n✅ Reviewed: {args.skill}")
            print(f"   Rating: {args.rating}")
            print(f"   Difficulty: {result['difficulty']:.2f}")
            print(f"   Stability: {result['stability']:.1f} days")
            print(f"   Next review: {result['scheduled_days']} days\n")
    
    elif args.action == 'stats':
        stats = manager.get_review_stats()
        print("\n📊 Review Statistics:\n")
        print(f"  Total Cards: {stats['total_cards']}")
        print(f"  Due Now: {stats['due_now']}")
        print(f"  New Cards: {stats['new_cards']}")
        print(f"  Avg Stability: {stats['avg_stability_days']} days")
        print(f"  Avg Difficulty: {stats['avg_difficulty']:.1f}/10\n")
