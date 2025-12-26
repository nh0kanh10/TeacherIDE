"""
Meta-Learning Tracker - Analyzes HOW user learns
Phase 2 Feature #4

Tracks:
- Learning velocity (topics/week)
- Time preferences (hour-of-day performance)
- Accuracy trends (30-day rolling)
- Session patterns (optimal length)
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

from performance_guard import async_guard

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'


class MetaLearningTracker:
    """
    Analyzes learning patterns using pre-aggregated data
    
    Focus: Speed over complexity (per expert feedback)
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
    
    @async_guard
    def save_session(self, session_data: Dict):
        """Save completed session to analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO session_analytics (
                user_id, session_start, session_end, duration_minutes,
                topics_covered, total_attempts, correct_attempts,
                avg_response_time, emotions_detected, fatigue_detected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data.get('user_id', 1),
            session_data['session_start'],
            session_data['session_end'],
            session_data['duration_minutes'],
            json.dumps(session_data.get('topics_covered', [])),
            session_data.get('total_attempts', 0),
            session_data.get('correct_attempts', 0),
            session_data.get('avg_response_time', 0),
            json.dumps(session_data.get('emotions_detected', [])),
            session_data.get('fatigue_detected', False)
        ))
        
        conn.commit()
        conn.close()
        
        # Trigger aggregation (async)
        self.aggregate_recent_stats(user_id=session_data.get('user_id', 1))
    
    @async_guard
    def aggregate_recent_stats(self, user_id: int = 1):
        """
        Pre-aggregate stats for fast queries
        
        Aggregates:
        - Learning velocity (last 4 weeks)
        - Hour-of-day performance (last 30 days)
        - Overall accuracy trend
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Learning Velocity (topics per week) - simpler approach
        cursor.execute("""
            SELECT 
                strftime('%Y-W%W', session_start) as week,
                SUM(LENGTH(topics_covered) - LENGTH(REPLACE(topics_covered, ',', '')) + 1) as total_topics,
                COUNT(*) as sessions
            FROM session_analytics
            WHERE user_id = ? 
                AND session_start >= date('now', '-28 days')
                AND topics_covered != '[]'
            GROUP BY week
        """, (user_id,))
        
        for row in cursor.fetchall():
            week, topics, sessions = row
            if sessions > 0:
                velocity = topics / sessions
                
                cursor.execute("""
                    INSERT OR REPLACE INTO meta_learning_stats 
                    (user_id, stat_type, time_bucket, bucket_value, metric_value, sample_size)
                    VALUES (?, 'velocity', 'week', ?, ?, ?)
                """, (user_id, week, velocity, sessions))
        
        # 2. Hour-of-day Performance
        cursor.execute("""
            SELECT 
                strftime('%H', session_start) as hour,
                AVG(CAST(correct_attempts AS REAL) / NULLIF(total_attempts, 0)) as avg_accuracy,
                COUNT(*) as sessions
            FROM session_analytics
            WHERE user_id = ?
                AND session_start >= date('now', '-30 days')
                AND total_attempts > 0
            GROUP BY hour
        """, (user_id,))
        
        for row in cursor.fetchall():
            hour, accuracy, sessions = row
            if accuracy is not None:
                cursor.execute("""
                    INSERT OR REPLACE INTO meta_learning_stats 
                    (user_id, stat_type, time_bucket, bucket_value, metric_value, sample_size)
                    VALUES (?, 'time_perf', 'hour', ?, ?, ?)
                """, (user_id, hour, accuracy, sessions))
        
        # 3. Overall Accuracy Trend (30-day rolling)
        cursor.execute("""
            SELECT 
                AVG(CAST(correct_attempts AS REAL) / NULLIF(total_attempts, 0)) as avg_accuracy,
                COUNT(*) as sessions
            FROM session_analytics
            WHERE user_id = ?
                AND session_start >= date('now', '-30 days')
                AND total_attempts > 0
        """, (user_id,))
        
        row = cursor.fetchone()
        if row[0] is not None:
            cursor.execute("""
                INSERT OR REPLACE INTO meta_learning_stats 
                (user_id, stat_type, time_bucket, bucket_value, metric_value, sample_size)
                VALUES (?, 'accuracy', 'rolling_30d', 'current', ?, ?)
            """, (user_id, row[0], row[1]))
        
        conn.commit()
        conn.close()
    
    def get_learning_profile(self, user_id: int = 1) -> Dict:
        """
        Get comprehensive learning profile (fast lookup)
        
        Returns:
            {
                'learning_velocity': float,  # topics/week
                'optimal_hours': [int],      # Best hours
                'accuracy_trend': str,        # 'improving', 'stable', 'declining'
                'avg_accuracy': float,
                'total_sessions': int
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get velocity
        cursor.execute("""
            SELECT AVG(metric_value), SUM(sample_size)
            FROM meta_learning_stats
            WHERE user_id = ? AND stat_type = 'velocity'
                AND time_bucket = 'week'
                AND bucket_value >= strftime('%Y-W%W', date('now', '-28 days'))
        """, (user_id,))
        
        velocity_row = cursor.fetchone()
        velocity = velocity_row[0] if velocity_row[0] else 0.0
        
        # Get optimal hours (top 3)
        cursor.execute("""
            SELECT bucket_value, metric_value
            FROM meta_learning_stats
            WHERE user_id = ? AND stat_type = 'time_perf'
            ORDER BY metric_value DESC
            LIMIT 3
        """, (user_id,))
        
        optimal_hours = [int(row[0]) for row in cursor.fetchall()]
        
        # Get accuracy
        cursor.execute("""
            SELECT metric_value, sample_size
            FROM meta_learning_stats
            WHERE user_id = ? AND stat_type = 'accuracy'
                AND time_bucket = 'rolling_30d'
        """, (user_id,))
        
        accuracy_row = cursor.fetchone()
        avg_accuracy = accuracy_row[0] if accuracy_row else 0.0
        total_sessions = accuracy_row[1] if accuracy_row else 0
        
        # Determine trend (compare to previous period)
        cursor.execute("""
            SELECT AVG(CAST(correct_attempts AS REAL) / NULLIF(total_attempts, 0))
            FROM session_analytics
            WHERE user_id = ?
                AND session_start BETWEEN date('now', '-60 days') AND date('now', '-30 days')
                AND total_attempts > 0
        """, (user_id,))
        
        prev_accuracy = cursor.fetchone()[0] or avg_accuracy
        
        if avg_accuracy > prev_accuracy + 0.05:
            trend = 'improving'
        elif avg_accuracy < prev_accuracy - 0.05:
            trend = 'declining'
        else:
            trend = 'stable'
        
        conn.close()
        
        return {
            'learning_velocity': round(velocity, 2),
            'optimal_hours': optimal_hours,
            'accuracy_trend': trend,
            'avg_accuracy': round(avg_accuracy, 2) if avg_accuracy else 0.0,
            'total_sessions': total_sessions
        }


if __name__ == "__main__":
    # Demo
    tracker = MetaLearningTracker()
    
    # Simulate a session
    session = {
        'user_id': 1,
        'session_start': datetime.now().isoformat(),
        'session_end': (datetime.now() + timedelta(minutes=45)).isoformat(),
        'duration_minutes': 45,
        'topics_covered': ['functions', 'classes', 'recursion'],
        'total_attempts': 10,
        'correct_attempts': 7,
        'avg_response_time': 65,
        'emotions_detected': ['optimal', 'confident'],
        'fatigue_detected': False
    }
    
    print("📊 Saving session...")
    tracker.save_session(session)
    
    print("\n📈 Learning Profile:")
    profile = tracker.get_learning_profile()
    
    print(f"  Velocity: {profile['learning_velocity']} topics/week")
    print(f"  Optimal Hours: {profile['optimal_hours']}")
    print(f"  Accuracy Trend: {profile['accuracy_trend']}")
    print(f"  Avg Accuracy: {profile['avg_accuracy']:.0%}")
    print(f"  Total Sessions: {profile['total_sessions']}")
