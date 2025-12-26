"""
Scaffolding System with Adaptive Teaching Integration
Determines when and how to provide learning scaffolds
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from statistical_predictor import StatisticalPredictor, PredictionInput
from adaptive_teaching import AdaptiveTeachingSystem

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'


@dataclass
class ScaffoldingContext:
    """Context for AI Agent to adapt teaching"""
    teaching_mode: str  # 'normal' or 'scaffold'
    struggle_probability: float  # 0-1
    confidence: float  # 0-1
    recommended_style: str  # Teaching style to use
    socratic_strategy: str  # How to apply Socratic method


class ScaffoldingSystem:
    """
    Determines scaffolding strategy compatible with Socratic teaching
    
    Strategy:
    - Normal mode: Socratic questions with minimal examples
    - Scaffold mode: Socratic questions + extra examples AFTER each question
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.predictor = StatisticalPredictor(db_path)
        self.adaptive_teaching = AdaptiveTeachingSystem(db_path)
    
    def get_scaffolding_context(self, skill_name: str) -> ScaffoldingContext:
        """
        Generate scaffolding context for AI Agent
        
        Args:
            skill_name: Skill to teach
            
        Returns:
            ScaffoldingContext with teaching guidance
        """
        # Get user learning history
        history = self._get_learning_history()
        
        # Get skill difficulty
        difficulty = self._get_skill_difficulty(skill_name)
        
        # Predict struggle
        prediction_input = PredictionInput(
            error_count_by_concept=history['avg_errors'],
            time_to_first_correct=history['avg_time'],
            prior_difficulty=difficulty,
            learning_velocity=history['velocity']
        )
        
        prediction = self.predictor.predict_struggle(prediction_input)
        
        # Determine teaching style
        if prediction.action == 'scaffold':
            # Override to visual/example-based styles for scaffolding
            recommended_style = self._choose_scaffold_style()
            socratic_strategy = "Ask Socratic questions, then provide detailed examples after each answer"
        else:
            # Use best style from adaptive system
            recommended_style = self.adaptive_teaching.choose_teaching_style()
            socratic_strategy = "Ask Socratic questions with minimal hints"
        
        return ScaffoldingContext(
            teaching_mode=prediction.action,
            struggle_probability=prediction.struggle_probability,
            confidence=prediction.confidence,
            recommended_style=recommended_style,
            socratic_strategy=socratic_strategy
        )
    
    def _get_learning_history(self) -> dict:
        """Get user learning history for prediction"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Get average errors from skill mastery (use attempts as proxy for errors)
            cursor.execute("""
                SELECT AVG(attempts) as avg_errors, COUNT(*) as count
                FROM skill_mastery
                WHERE last_practiced >= date('now', '-30 days')
                LIMIT 10
            """)
            
            row = cursor.fetchone()
            avg_errors = min(int(row[0] or 2), 5)  # Cap at 5, default to 2
            sample_count = row[1] or 0
            
            # FIXED: Use REAL response times from DB (not hardcoded)
            cursor.execute("""
                SELECT AVG(response_time_sec), COUNT(*)
                FROM response_times
                WHERE timestamp >= date('now', '-30 days')
            """)
            
            time_row = cursor.fetchone()
            avg_time = float(time_row[0] or 120.0)  # Default to 120s only if no data
            time_sample_count = time_row[1] or 0
            
            # Calculate learning velocity (topics/week)
            cursor.execute("""
                SELECT COUNT(*) as topics
                FROM skill_mastery
                WHERE last_practiced >= date('now', '-7 days')
            """)
            
            topics_this_week = cursor.fetchone()[0] or 0
            velocity = max(topics_this_week, 1.0)  # Default to 1 topic/week, minimum 1
            
            return {
                'avg_errors': avg_errors,
                'avg_time': avg_time,
                'velocity': float(velocity),
                'sample_count': sample_count
            }
        finally:
            conn.close()
    
    def _get_skill_difficulty(self, skill_name: str) -> float:
        """Get skill difficulty rating (1-10)"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT complexity FROM skills WHERE name = ?
            """, (skill_name,))
            
            row = cursor.fetchone()
            
            if row:
                # complexity is 1-10 scale
                return float(row[0])
            else:
                # Unknown skill - assume medium difficulty
                return 5.0
        finally:
            conn.close()
    
    def _choose_scaffold_style(self) -> str:
        """
        Choose teaching style optimized for scaffolding
        
        Priority:
        1. visual (diagrams help with complex topics)
        2. example_based (concrete examples reduce abstraction)
        3. hands_on (practice solidifies understanding)
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Get effectiveness of scaffold-friendly styles
            cursor.execute("""
                SELECT teaching_style, avg_effectiveness
                FROM style_preferences
                WHERE teaching_style IN ('visual', 'example_based', 'hands_on')
                ORDER BY avg_effectiveness DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            
            if row:
                return row[0]
            else:
                # Default: visual is universally helpful for scaffolding
                return 'visual'
        finally:
            conn.close()
    
    def format_for_ai_agent(self, context: ScaffoldingContext) -> str:
        """
        Format scaffolding context for AI Agent system prompt
        
        Returns:
            Formatted instruction string
        """
        if context.teaching_mode == 'scaffold':
            return f"""[TEACHING_MODE: SCAFFOLD]
[STRUGGLE_PROB: {context.struggle_probability:.0%}]
[CONFIDENCE: {context.confidence:.0%}]
[STYLE: {context.recommended_style}]
[STRATEGY: {context.socratic_strategy}]

IMPORTANT: User may struggle with this topic. Apply Socratic method BUT provide detailed examples after each question. Use {context.recommended_style} style."""
        else:
            return f"""[TEACHING_MODE: NORMAL]
[STYLE: {context.recommended_style}]
[STRATEGY: {context.socratic_strategy}]

Standard Socratic teaching approach."""


if __name__ == "__main__":
    # Demo
    system = ScaffoldingSystem()
    
    print("🎓 Scaffolding System Demo\n")
    
    test_skills = [
        "python_variables",  # Easy
        "python_decorators",  # Medium
        "asyncio_advanced",  # Hard
    ]
    
    for skill in test_skills:
        context = system.get_scaffolding_context(skill)
        
        print(f"\n{'='*60}")
        print(f"Skill: {skill}")
        print(f"{'='*60}")
        print(system.format_for_ai_agent(context))
