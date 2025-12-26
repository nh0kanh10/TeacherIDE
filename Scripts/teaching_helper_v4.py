"""
Enhanced teaching_helper with v4.0 features integration
Integrates: Event system, FSRS, Emotional detection
"""
import argparse
import json
from pathlib import Path
from datetime import datetime

# v4.0 imports
from event_bus import get_event_bus, EventType, emit_skill_update
from spaced_repetition import SpacedRepetitionManager
from emotional_detector import EmotionalDetector
from performance_guard import sync_guard, async_guard

# Legacy imports
import sqlite3

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
VAULT_PATH = Path(__file__).parent.parent


class TeachingSession:
    """
    Enhanced teaching session with v4.0 features
    
    Tracks:
    - Session duration
    - Errors and accuracy
    - Emotional state
    - Reviews completed
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.errors = 0
        self.correct_answers = 0
        self.total_attempts = 0
        self.response_times = []
        
        # v4.0 integrations
        self.event_bus = get_event_bus()
        self.emotional_detector = EmotionalDetector()
        self.spaced_rep_manager = SpacedRepetitionManager()
        
        # Emit session start
        self.event_bus.publish(EventType.SESSION_START, {
            'user_id': 1,
            'timestamp': self.start_time.isoformat()
        })
    
    def record_attempt(self, skill_name: str, correct: bool, response_time_sec: float = None):
        """Record a practice attempt"""
        self.total_attempts += 1
        
        if correct:
            self.correct_answers += 1
        else:
            self.errors += 1
        
        if response_time_sec:
            self.response_times.append(response_time_sec)
    
    @sync_guard
    def get_activity_summary(self) -> dict:
        """Get current session activity for emotional analysis"""
        duration_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        
        return {
            'errors': self.errors,
            'correct_streak': self._get_current_streak(),
            'avg_response_time': sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            'session_duration': duration_minutes,
            'accuracy': self.correct_answers / self.total_attempts if self.total_attempts > 0 else 0
        }
    
    def _get_current_streak(self) -> int:
        """Calculate current correct streak"""
        # TODO: Track actual streak
        return self.correct_answers
    
    def check_emotional_state(self) -> tuple:
        """
        Check emotional state and suggest intervention
        
        Returns:
            (emotion, should_show_message, message)
        """
        activity = self.get_activity_summary()
        emotion, meta = self.emotional_detector.analyze_state(activity)
        
        should_intervene = self.emotional_detector.should_intervene(
            emotion, 
            meta.get('confidence', 0)
        )
        
        return emotion, should_intervene, meta.get('message', '')
    
    def end_session(self):
        """End session and emit event"""
        duration = (datetime.now() - self.start_time).total_seconds() / 60
        
        self.event_bus.publish(EventType.SESSION_END, {
            'user_id': 1,
            'duration_minutes': int(duration),
            'total_attempts': self.total_attempts,
            'correct': self.correct_answers,
            'accuracy': self.correct_answers / self.total_attempts if self.total_attempts > 0 else 0
        })


@async_guard
def save_knowledge_with_review(title: str, content: str, skill_name: str = None, 
                               correct: bool = None, rating: int = None):
    """
    Enhanced save_knowledge with FSRS integration
    
    Args:
        title: Knowledge title
        content: Content to save
        skill_name: Associated skill
        correct: Whether practice was correct
        rating: FSRS rating (1-4) if doing spaced repetition
    """
    # Save to vault (existing logic)
    vault_path = VAULT_PATH
    knowledge_file = vault_path / f"{title}.md"
    
    with open(knowledge_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Emit knowledge saved event
    event_bus = get_event_bus()
    event_bus.publish(EventType.KNOWLEDGE_SAVED, {
        'title': title,
        'skill_name': skill_name,
        'file_path': str(knowledge_file)
    })
    
    # Update skill mastery if provided
    if skill_name and correct is not None:
        update_skill_mastery(skill_name, correct)
    
    # Process FSRS review if rating provided
    if skill_name and rating is not None:
        sr_manager = SpacedRepetitionManager()
        result = sr_manager.review_skill(skill_name, rating)
        print(f"\n📊 FSRS Update:")
        print(f"   Next review: {result['scheduled_days']} days")
        print(f"   Stability: {result['stability']:.1f} days")
    
    print(f"✅ Saved: {knowledge_file}")


def update_skill_mastery(skill_name: str, correct: bool):
    """Update skill mastery in database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current mastery
    cursor.execute("""
        SELECT mastery_prob, attempts, correct 
        FROM skill_mastery 
        WHERE skill_name = ?
    """, (skill_name,))
    
    row = cursor.fetchone()
    
    if row:
        old_mastery = row[0]
        attempts = row[1] + 1
        correct_count = row[2] + (1 if correct else 0)
        
        # Simple Bayesian update (placeholder for full BKT)
        success_rate = correct_count / attempts
        new_mastery = 0.7 * old_mastery + 0.3 * success_rate
        
        cursor.execute("""
            UPDATE skill_mastery 
            SET mastery_prob = ?, attempts = ?, correct = ?, last_practiced = ?
            WHERE skill_name = ?
        """, (new_mastery, attempts, correct_count, datetime.now().isoformat(), skill_name))
    else:
        # New skill
        new_mastery = 0.8 if correct else 0.3
        cursor.execute("""
            INSERT INTO skill_mastery (skill_name, mastery_prob, attempts, correct, last_practiced)
            VALUES (?, ?, 1, ?, ?)
        """, (skill_name, new_mastery, 1 if correct else 0, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    # Emit skill mastery update event
    emit_skill_update(skill_name, row[0] if row else 0, new_mastery, correct)
    
    print(f"📈 {skill_name}: {(row[0] if row else 0):.0%} → {new_mastery:.0%}")


# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Teaching Helper - v4.0')
    parser.add_argument('action', choices=['save', 'session', 'emotional_check'],
                       help='Action to perform')
    parser.add_argument('--title', help='Knowledge title')
    parser.add_argument('--content', help='Content')
    parser.add_argument('--skill', help='Skill name')
    parser.add_argument('--correct', action='store_true', help='Practice was correct')
    parser.add_argument('--rating', type=int, choices=[1,2,3,4],
                       help='FSRS rating (1=Again, 2=Hard, 3=Good, 4=Easy)')
    
    args = parser.parse_args()
    
    if args.action == 'save':
        if not args.title or not args.content:
            print("Error: --title and --content required")
        else:
            save_knowledge_with_review(
                args.title, 
                args.content,
                args.skill,
                args.correct if args.correct else None,
                args.rating
            )
    
    elif args.action == 'session':
        # Demo session with emotional check
        session = TeachingSession()
        
        # Simulate some activity
        session.record_attempt('python_functions', True, 45)
        session.record_attempt('python_functions', False, 120)
        session.record_attempt('python_functions', True, 60)
        
        # Check emotional state
        emotion, should_intervene, message = session.check_emotional_state()
        
        print(f"\n📊 Session Activity:")
        print(f"   Attempts: {session.total_attempts}")
        print(f"   Accuracy: {session.correct_answers/session.total_attempts:.0%}")
        print(f"\n😊 Emotional State: {emotion}")
        if should_intervene:
            print(f"   💬 {message}")
        
        session.end_session()
    
    elif args.action == 'emotional_check':
        detector = EmotionalDetector()
        
        # Mock activity
        activity = {
            'errors': 2,
            'avg_response_time': 80,
            'session_duration': 45,
            'correct_streak': 3,
            'accuracy': 0.7
        }
        
        emotion, meta = detector.analyze_state(activity)
        print(f"Emotion: {emotion}")
        print(f"Confidence: {meta['confidence']}")
        if 'message' in meta:
            print(f"Message: {meta['message']}")
