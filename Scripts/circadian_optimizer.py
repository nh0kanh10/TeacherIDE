"""
Circadian Optimization
Phase 3 Feature #8

Tracks hour-of-day performance and recommends optimal study times
Uses pre-aggregated data from meta_learning_stats
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from performance_guard import sync_guard

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'


class CircadianOptimizer:
    """
    Analyzes performance by hour of day
    
    Recommends:
    - Best times for complex topics (peak hours)
    - Best times for reviews (non-peak hours)
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
    
    @sync_guard
    def get_hourly_performance(self, user_id: int = 1) -> Dict[int, float]:
        """
        Get performance score by hour (0-23)
        
        Returns:
            {hour: accuracy_score}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Use pre-aggregated stats from meta_learning_stats
        cursor.execute("""
            SELECT bucket_value, metric_value
            FROM meta_learning_stats
            WHERE user_id = ? AND stat_type = 'time_perf'
                AND time_bucket = 'hour'
            ORDER BY CAST(bucket_value AS INTEGER)
        """, (user_id,))
        
        hourly_data = {}
        for row in cursor.fetchall():
            hour = int(row[0])
            accuracy = row[1]
            hourly_data[hour] = accuracy
        
        conn.close()
        return hourly_data
    
    def get_peak_hours(self, top_n: int = 3) -> List[int]:
        """Get top N performance hours"""
        hourly = self.get_hourly_performance()
        
        if not hourly:
            # Default: morning hours
            return [9, 10, 14]
        
        # Sort by performance, return top N hours
        sorted_hours = sorted(hourly.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, _ in sorted_hours[:top_n]]
    
    def get_non_peak_hours(self, bottom_n: int = 3) -> List[int]:
        """Get bottom N performance hours (for easier tasks)"""
        hourly = self.get_hourly_performance()
        
        if not hourly:
            # Default: evening hours
            return [20, 21, 22]
        
        # Sort by performance, return bottom N hours
        sorted_hours = sorted(hourly.items(), key=lambda x: x[1])
        return [hour for hour, _ in sorted_hours[:bottom_n]]
    
    def recommend_study_time(self, current_hour: int, task_complexity: str = 'medium') -> Tuple[str, str]:
        """
        Recommend whether to study now or wait
        
        Args:
            current_hour: Current hour (0-23)
            task_complexity: 'easy', 'medium', 'hard'
            
        Returns:
            (recommendation, reason)
        """
        peak_hours = self.get_peak_hours()
        non_peak_hours = self.get_non_peak_hours()
        
        if task_complexity == 'hard':
            if current_hour in peak_hours:
                return ('study_now', f'Peak performance time! Great for complex topics.')
            else:
                best_hour = peak_hours[0]
                return ('wait', f'Complex topic - better at {best_hour}:00 (peak hour)')
        
        elif task_complexity == 'easy':
            if current_hour in non_peak_hours:
                return ('study_now', 'Good time for easier review/practice')
            else:
                return ('study_now', 'Simple tasks work anytime')
        
        else:  # medium
            return ('study_now', 'Medium complexity - study anytime')
    
    def get_circadian_profile(self) -> Dict:
        """Get full circadian profile"""
        peak_hours = self.get_peak_hours()
        non_peak = self.get_non_peak_hours()
        hourly = self.get_hourly_performance()
        
        current_hour = datetime.now().hour
        
        return {
            'peak_hours': peak_hours,
            'non_peak_hours': non_peak,
            'current_hour': current_hour,
            'hourly_performance': hourly,
            'current_recommendation': self.recommend_study_time(current_hour, 'medium')
        }


if __name__ == "__main__":
    # Demo
    optimizer = CircadianOptimizer()
    
    print("⏰ Circadian Optimization Demo\n")
    
    profile = optimizer.get_circadian_profile()
    
    print(f"Current Time: {profile['current_hour']}:00")
    print(f"\nPeak Hours (best for complex topics): {profile['peak_hours']}")
    print(f"Non-Peak Hours (good for reviews): {profile['non_peak_hours']}")
    
    print(f"\nHourly Performance:")
    for hour, perf in sorted(profile['hourly_performance'].items()):
        bar = '█' * int(perf * 20)
        print(f"  {hour:02d}:00 {bar} {perf:.0%}")
    
    print(f"\nCurrent Recommendation:")
    rec, reason = profile['current_recommendation']
    print(f"  Action: {rec}")
    print(f"  Reason: {reason}")
    
    # Test recommendations
    print(f"\n📚 Scenario Tests:")
    scenarios = [
        (9, 'hard', 'Learning advanced recursion'),
        (14, 'medium', 'Practicing Python loops'),
        (21, 'easy', 'Reviewing vocabulary'),
    ]
    
    for hour, complexity, task in scenarios:
        rec, reason = optimizer.recommend_study_time(hour, complexity)
        print(f"\n  {hour}:00 - {task} ({complexity})")
        print(f"    → {rec}: {reason}")
