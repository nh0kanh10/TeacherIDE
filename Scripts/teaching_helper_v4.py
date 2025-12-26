"""
Enhanced teaching_helper with v4.7 features integration
Integrates: Event system, FSRS, Emotional detection, Auto Prediction
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

# v4.7 imports
from scaffolding_system import ScaffoldingSystem, ScaffoldingContext

# Legacy imports
import sqlite3

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
VAULT_PATH = Path(__file__).parent.parent


class TeachingSession:
    """
    Enhanced teaching session with v4.7 features
    
    Tracks:
    - Session duration
    - Errors and accuracy
    - Emotional state
    - Reviews completed
    - Prediction feedback loop (v4.7)
    """
    
    def __init__(self, skill_name: str = None):
        self.skill_name = skill_name
        self.start_time = datetime.now()
        self.errors = 0
        self.correct_answers = 0
        self.total_attempts = 0
        self.response_times = []
        
        # v4.0 integrations
        self.event_bus = get_event_bus()
        self.emotional_detector = EmotionalDetector()
        self.spaced_rep_manager = SpacedRepetitionManager()
        
        # v4.7 integrations
        self.scaffolding_system = ScaffoldingSystem()
        self.prediction_context = None
        self.prediction_id = None  # Track prediction for feedback loop
        self.mastery_before = None
        
        # Emit session start
        self.event_bus.publish(EventType.SESSION_START, {
            'user_id': 1,
            'timestamp': self.start_time.isoformat()
        })
    
    def record_attempt(self, skill_name: str, correct: bool, response_time_sec: float = None):
        """Record a practice attempt (v4.7: persists to DB)"""
        self.total_attempts += 1
        
        if correct:
            self.correct_answers += 1
        else:
            self.errors += 1
        
        if response_time_sec:
            self.response_times.append(response_time_sec)
            
            # v4.7: Persist to DB for prediction accuracy
            self._save_response_time(skill_name, response_time_sec, correct)
    
    def _save_response_time(self, skill_name: str, response_time_sec: float, correct: bool):
        """Save response time to DB for future predictions"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO response_times (skill_name, response_time_sec, correct)
            VALUES (?, ?, ?)
        """, (skill_name, response_time_sec, 1 if correct else 0))
        
        conn.commit()
        conn.close()
    
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
        """End session and emit event (v4.7: auto-record teaching outcome)"""
        duration = (datetime.now() - self.start_time).total_seconds() / 60
        
        # v4.7: Auto-record teaching outcome for feedback loop
        if self.prediction_id and self.skill_name:
            try:
                self.record_teaching_outcome()
            except Exception as e:
                print(f"⚠️  Failed to record teaching outcome: {e}")
        
        self.event_bus.publish(EventType.SESSION_END, {
            'user_id': 1,
            'duration_minutes': int(duration),
            'total_attempts': self.total_attempts,
            'correct': self.correct_answers,
            'accuracy': self.correct_answers / self.total_attempts if self.total_attempts > 0 else 0
        })
    
    # v4.7: Prediction Integration Methods
    
    def predict_for_skill(self, skill_name: str) -> ScaffoldingContext:
        """
        Generate prediction and scaffolding context for skill
        
        Args:
            skill_name: Skill to teach
            
        Returns:
            ScaffoldingContext with teaching guidance (fallback to normal on error)
        """
        self.skill_name = skill_name
        
        try:
            # Get current mastery for feedback loop
            self.mastery_before = self._get_current_mastery(skill_name)
            
            # Generate prediction
            self.prediction_context = self.scaffolding_system.get_scaffolding_context(skill_name)
            
            # Save prediction to DB for feedback loop
            self.prediction_id = self._save_prediction(skill_name, self.prediction_context)
            
            return self.prediction_context
        
        except Exception as e:
            # Graceful fallback to normal teaching on prediction error
            print(f"⚠️  Prediction failed: {e}")
            print(f"   Falling back to normal teaching mode")
            
            # Return safe default context
            fallback_context = ScaffoldingContext(
                teaching_mode='normal',
                struggle_probability=0.5,
                confidence=0.0,
                recommended_style='hands_on',
                socratic_strategy='Ask Socratic questions with minimal hints'
            )
            
            self.prediction_context = fallback_context
            return fallback_context
    
    def record_teaching_outcome(self):
        """
        Record actual teaching outcome for feedback loop
        Should be called AFTER teaching session completes
        
        v4.7.3: Uses gradient struggle detection (severe/mild/none)
        """
        if not self.prediction_id or not self.skill_name:
            return  # No prediction to verify
        
        # Get mastery after teaching
        mastery_after = self._get_current_mastery(self.skill_name)
        
        # IMPROVED: Use gradient instead of binary threshold
        mastery_improvement = mastery_after - self.mastery_before
        
        if mastery_improvement < 0.05:
            actual_struggled = 2  # Severe struggle (almost no improvement)
        elif mastery_improvement < 0.15:
            actual_struggled = 1  # Mild struggle (some improvement)
        else:
            actual_struggled = 0  # No struggle (good improvement)
        
        # Check if prediction was correct
        # Predicted scaffold if struggle (1 or 2), normal if no struggle (0)
        predicted_struggle = 1 if self.prediction_context.teaching_mode == 'scaffold' else 0
        
        # Correct if:
        # - Predicted scaffold AND actually struggled (1 or 2)
        # - Predicted normal AND didn't struggle (0)
        if predicted_struggle == 1:
            prediction_correct = 1 if actual_struggled >= 1 else 0
        else:
            prediction_correct = 1 if actual_struggled == 0 else 0
        
        # Update DB
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            
            duration_min = (datetime.now() - self.start_time).total_seconds() / 60
            
            cursor.execute("""
                UPDATE prediction_tracking
                SET actual_struggled = ?,
                    mastery_before = ?,
                    mastery_after = ?,
                    session_duration_min = ?,
                    prediction_correct = ?
                WHERE id = ?
            """, (actual_struggled, self.mastery_before, mastery_after, 
                  duration_min, prediction_correct, self.prediction_id))
            
            conn.commit()
        finally:
            conn.close()
    
    def _get_current_mastery(self, skill_name: str) -> float:
        """Get current mastery probability for skill"""
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mastery_prob FROM skill_mastery WHERE skill_name = ?
            """, (skill_name,))
            
            row = cursor.fetchone()
            return row[0] if row else 0.0
        finally:
            conn.close()
    
    def _save_prediction(self, skill_name: str, context: ScaffoldingContext) -> int:
        """Save prediction to DB, return prediction ID"""
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO prediction_tracking (
                    skill_name, prediction_timestamp,
                    struggle_probability, confidence, predicted_action,
                    mastery_before
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (skill_name, datetime.now().isoformat(),
                  context.struggle_probability, context.confidence,
                  context.teaching_mode, self.mastery_before))
            
            prediction_id = cursor.lastrowid
            conn.commit()
            return prediction_id
        finally:
            conn.close()


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
