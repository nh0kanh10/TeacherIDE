"""
Statistical Prediction Engine
Phase 3 Feature #7

Uses Bayesian updating - NOT neural networks
Predicts struggle probability on new skills

Input: error_count, time_to_correct, difficulty, velocity
Output: struggle_prob, confidence, action
"""
import sqlite3
from pathlib import Path
from typing import Dict, Tuple
from dataclasses import dataclass
import math

from performance_guard import sync_guard

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'


@dataclass
class PredictionInput:
    """Input contract - LOCKED per expert feedback"""
    error_count_by_concept: int
    time_to_first_correct: float  # seconds
    prior_difficulty: float  # 1-10 static rating
    learning_velocity: float  # topics/week


@dataclass
class PredictionOutput:
    """Output contract - LOCKED"""
    struggle_probability: float  # 0-1
    confidence: float  # 0-1
    action: str  # 'scaffold' or 'normal'


class StatisticalPredictor:
    """
    Bayesian prediction engine for struggle probability
    
    Algorithm:
    1. Prior P(struggle) from skill difficulty
    2. Likelihood P(evidence|struggle) from user history
    3. Posterior P(struggle|evidence) via Bayes rule
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.struggle_threshold = 0.65  # Action threshold
    
    @sync_guard
    def predict_struggle(self, input_data: PredictionInput) -> PredictionOutput:
        """
        Predict struggle probability using Bayesian updating
        
        Args:
            input_data: PredictionInput with user performance data
            
        Returns:
            PredictionOutput with struggle prob, confidence, action
        """
        
        # 1. Prior from skill difficulty (normalized 0-1)
        prior = input_data.prior_difficulty / 10.0
        
        # 2. Evidence from user performance
        # High errors → high struggle likelihood
        error_factor = min(input_data.error_count_by_concept / 5.0, 1.0)
        
        # Slow time → high struggle likelihood
        time_factor = min(input_data.time_to_first_correct / 300.0, 1.0)  # 5 min baseline
        
        # Low velocity → high struggle likelihood  
        velocity_factor = max(0, 1.0 - input_data.learning_velocity / 3.0)  # 3 topics/week = good
        
        # Combine evidence (weighted average)
        evidence_score = (error_factor * 0.5 + 
                         time_factor * 0.3 + 
                         velocity_factor * 0.2)
        
        # 3. Bayesian update (simplified)
        # Posterior ∝ Likelihood × Prior
        likelihood = evidence_score
        posterior = (likelihood * prior) / ((likelihood * prior) + ((1 - likelihood) * (1 - prior)))
        
        # 4. Confidence based on data quality
        # More data → higher confidence
        data_points = min(input_data.error_count_by_concept, 10)
        confidence = data_points / 10.0
        
        # 5. Action decision
        action = 'scaffold' if posterior > self.struggle_threshold else 'normal'
        
        return PredictionOutput(
            struggle_probability=round(posterior, 3),
            confidence=round(confidence, 2),
            action=action
        )
    
    def get_user_history_on_similar_skills(self, target_skill: str) -> Dict:
        """
        Get user performance on skills similar to target
        
        Returns:
            {
                'avg_errors': float,
                'avg_time': float,
                'sample_size': int
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get similar skills (same complexity range)
        cursor.execute("""
            SELECT AVG(error_count), AVG(time_to_mastery), COUNT(*)
            FROM (
                SELECT 
                    s.name,
                    0 as error_count,  -- Placeholder
                    0 as time_to_mastery  -- Placeholder
                FROM skills s
                WHERE s.complexity BETWEEN 
                    (SELECT complexity - 1 FROM skills WHERE name = ?) AND
                    (SELECT complexity + 1 FROM skills WHERE name = ?)
            )
        """, (target_skill, target_skill))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'avg_errors': row[0] or 0,
            'avg_time': row[1] or 0,
            'sample_size': row[2] or 0
        }


if __name__ == "__main__":
    # Demo
    predictor = StatisticalPredictor()
    
    print("🔮 Statistical Prediction Demo\n")
    
    # Test scenarios
    scenarios = [
        ("Easy learner", PredictionInput(
            error_count_by_concept=1,
            time_to_first_correct=60,
            prior_difficulty=5,
            learning_velocity=3.0
        )),
        ("Struggling learner", PredictionInput(
            error_count_by_concept=5,
            time_to_first_correct=400,
            prior_difficulty=8,
            learning_velocity=0.5
        )),
        ("Average learner", PredictionInput(
            error_count_by_concept=3,
            time_to_first_correct=180,
            prior_difficulty=6,
            learning_velocity=2.0
        )),
    ]
    
    for name, input_data in scenarios:
        result = predictor.predict_struggle(input_data)
        
        print(f"{name}:")
        print(f"  Input: {input_data.error_count_by_concept} errors, {input_data.time_to_first_correct}s, "
              f"difficulty {input_data.prior_difficulty}, velocity {input_data.learning_velocity}")
        print(f"  Struggle Prob: {result.struggle_probability:.1%}")
        print(f"  Confidence: {result.confidence:.0%}")
        print(f"  Action: {result.action}")
        print()
