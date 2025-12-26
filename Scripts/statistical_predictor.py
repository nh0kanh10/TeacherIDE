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

# Prediction constants (extracted from magic numbers)
MAX_ERRORS_BASELINE = 5.0  # Baseline for "many errors"
MAX_TIME_BASELINE = 300.0  # 5 minutes baseline for slow response
GOOD_VELOCITY = 3.0  # topics/week considered good pace

# Weight distribution for evidence factors
ERROR_WEIGHT = 0.5  # 50% weight on error count
TIME_WEIGHT = 0.3   # 30% weight on response time
VELOCITY_WEIGHT = 0.2  # 20% weight on learning velocity

# Confidence thresholds
MIN_DATA_POINTS = 5  # Minimum samples for reliable prediction
COLD_START_CONFIDENCE = 0.3  # Confidence cap during cold start
MIN_CONFIDENCE_FOR_SCAFFOLD = 0.5  # Minimum confidence to scaffold


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
            
        Raises:
            ValueError: If input data is invalid
        """
        
        # Input validation
        if input_data.error_count_by_concept < 0:
            raise ValueError(f"Error count cannot be negative: {input_data.error_count_by_concept}")
        if not (1 <= input_data.prior_difficulty <= 10):
            raise ValueError(f"Difficulty must be 1-10, got: {input_data.prior_difficulty}")
        if input_data.time_to_first_correct < 0:
            raise ValueError(f"Time cannot be negative: {input_data.time_to_first_correct}")
        if input_data.learning_velocity < 0:
            raise ValueError(f"Velocity cannot be negative: {input_data.learning_velocity}")
        
        # 1. Prior from skill difficulty (normalized 0-1)
        prior = input_data.prior_difficulty / 10.0
        
        # 2. Evidence from user performance
        # High errors → high struggle likelihood
        error_factor = min(input_data.error_count_by_concept / MAX_ERRORS_BASELINE, 1.0)
        
        # Slow time → high struggle likelihood
        time_factor = min(input_data.time_to_first_correct / MAX_TIME_BASELINE, 1.0)
        
        # Low velocity → high struggle likelihood  
        velocity_factor = max(0, 1.0 - input_data.learning_velocity / GOOD_VELOCITY)
        
        # Combine evidence (weighted average using constants)
        evidence_score = (error_factor * ERROR_WEIGHT + 
                         time_factor * TIME_WEIGHT + 
                         velocity_factor * VELOCITY_WEIGHT)
        
        # 3. Bayesian update (simplified)
        # Posterior ∝ Likelihood × Prior
        likelihood = evidence_score
        posterior = (likelihood * prior) / ((likelihood * prior) + ((1 - likelihood) * (1 - prior)))
        
        # 4. Confidence based on data quality
        # COLD START HANDLING: Require minimum data points for reliable prediction
        data_points = min(input_data.error_count_by_concept, 10)
        confidence = data_points / 10.0
        
        # If insufficient data (cold start), lower confidence and use conservative approach
        if data_points < MIN_DATA_POINTS:
            confidence = max(confidence, COLD_START_CONFIDENCE)
            # Conservative: Fallback to prior-only (just skill difficulty)
            posterior = prior
        
        # 5. Action decision
        # Only scaffold if BOTH high struggle prob AND sufficient confidence
        if posterior > self.struggle_threshold and confidence >= MIN_CONFIDENCE_FOR_SCAFFOLD:
            action = 'scaffold'
        else:
            action = 'normal'
        
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
