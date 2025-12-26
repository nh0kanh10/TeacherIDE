"""
Emotional Detector with Keystroke Dynamics
Enhanced with cooldown mechanism (Fix #4)
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from collections import deque
import numpy as np

from v4_config import get_config


class EmotionalState:
    """Enum for emotional states"""
    FRUSTRATED = "frustrated"
    BORED = "bored"
    TIRED = "tired"
    CONFIDENT = "confident"
    OPTIMAL = "optimal"


class EmotionalDetector:
    """
    Detects learner emotional state from behavior patterns
    
    ✅ Fix #4: Added cooldown mechanism to prevent spam
    """
    
    def __init__(self):
        self.config = get_config("emotion")
        self.keystroke_monitor = KeystrokeMonitor()
        
        # ✅ Cooldown tracking
        self.last_intervention_time = None
        self.last_detected_emotion = EmotionalState.OPTIMAL
        
    def analyze_state(self, recent_activity: Dict) -> Tuple[str, Dict]:
        """
        Analyze emotional state from activity patterns
        
        Args:
            recent_activity: Dict with keys:
                - errors: int
                - avg_response_time: float (seconds)
                - session_duration: int (minutes)
                - correct_streak: int
                - accuracy: float (0-1)
                
        Returns:
            (emotion, metadata) tuple
        """
        # ✅ Get fatigue biomarker
        fatigue_score = self.keystroke_monitor.get_fatigue_zscore()
        
        # FRUSTRATED: Errors + slow + fatigued
        if (recent_activity.get('errors', 0) >= 3 and 
            recent_activity.get('avg_response_time', 0) > 120 and
            fatigue_score > self.config['fatigue_zscore_threshold']):
            
            return EmotionalState.FRUSTRATED, {
                'confidence': 0.9,
                'fatigue_zscore': fatigue_score,
                'suggestion': 'simplify_or_break',
                'message': 'Có vẻ mệt rồi. Nghỉ 5 phút nhé?'
            }
        
        # BORED: Too easy
        if (recent_activity.get('correct_streak', 0) > 5 and
            recent_activity.get('avg_response_time', 0) < 30):
            
            return EmotionalState.BORED, {
                'confidence': 0.75,
                'suggestion': 'increase_difficulty',
                'message': 'Bạn đang làm tốt! Thử challenge khó hơn?'
            }
        
        # TIRED: Long session + declining
        if (recent_activity.get('session_duration', 0) > 120 and
            recent_activity.get('accuracy', 1.0) < 0.6):
            
            return EmotionalState.TIRED, {
                'confidence': 0.85,
                'fatigue_zscore': fatigue_score,
                'suggestion': 'end_session',
                'message': 'Hôm nay đã học nhiều rồi. Nghỉ ngơi nhé!'
            }
        
        # CONFIDENT: High performance
        if (recent_activity.get('accuracy', 0) > 0.8 and
            30 < recent_activity.get('avg_response_time', 0) < 90):
            
            return EmotionalState.CONFIDENT, {
                'confidence': 0.7,
                'suggestion': 'push_harder',
                'message': 'Tuyệt vời! Sẵn sàng level tiếp?'
            }
        
        return EmotionalState.OPTIMAL, {
            'confidence': 1.0,
            'suggestion': 'continue'
        }
    
    def should_intervene(self, emotion: str, confidence: float) -> bool:
        """
        ✅ Fix #4: Cooldown-aware intervention decision
        
        Prevents spam by ensuring:
        1. High confidence
        2. State changed
        3. Cooldown period passed
        """
        # Check threshold
        if confidence < self.config['threshold']:
            return False
        
        # Check state change
        if emotion == self.last_detected_emotion and emotion != EmotionalState.OPTIMAL:
            return False
        
        # ✅ Check cooldown
        if self.last_intervention_time:
            elapsed = datetime.now() - self.last_intervention_time
            cooldown = timedelta(minutes=self.config['cooldown_minutes'])
            
            if elapsed < cooldown:
                # Still in cooldown
                return False
        
        # All checks passed
        self.last_intervention_time = datetime.now()
        self.last_detected_emotion = emotion
        
        return True


class KeystrokeMonitor:
    """
    ✅ RESEARCH: Privacy-preserving keystroke dynamics
    
    Monitors ONLY timing patterns, NEVER actual characters
    """
    
    def __init__(self):
        config = get_config("emotion")
        self.window_size = 50
        self.calibration_keystrokes = config['calibration_keystrokes']
        
        # Timing buffers (ms)
        self.flight_times = deque(maxlen=self.window_size)
        self.hold_times = deque(maxlen=self.window_size)
        
        # Baseline (calibrated)
        self.baseline_ft_mean = None
        self.baseline_ft_std = None
        self.baseline_ht_mean = None
        self.baseline_ht_std = None
        
        self.calibration_count = 0
        self.last_key_up_time = None
    
    def on_key_event(self, event_type: str, timestamp_ms: float):
        """
        Process keystroke event
        
        Args:
            event_type: 'press' or 'release'
            timestamp_ms: Timestamp in milliseconds
        """
        if event_type == 'press':
            self.last_key_down_time = timestamp_ms
            
            # Calculate Flight Time (if previous key exists)
            if self.last_key_up_time:
                ft = timestamp_ms - self.last_key_up_time
                self.flight_times.append(ft)
                
        elif event_type == 'release':
            self.last_key_up_time = timestamp_ms
            
            # Calculate Hold Time
            if hasattr(self, 'last_key_down_time'):
                ht = timestamp_ms - self.last_key_down_time
                self.hold_times.append(ht)
        
        # Calibration
        if self.calibration_count < self.calibration_keystrokes:
            self.calibration_count += 1
            if self.calibration_count == self.calibration_keystrokes:
                self._build_baseline()
    
    def _build_baseline(self):
        """Build baseline statistics from calibration period"""
        if len(self.flight_times) > 10:
            self.baseline_ft_mean = np.mean(list(self.flight_times))
            self.baseline_ft_std = np.std(list(self.flight_times))
        
        if len(self.hold_times) > 10:
            self.baseline_ht_mean = np.mean(list(self.hold_times))
            self.baseline_ht_std = np.std(list(self.hold_times))
    
    def get_fatigue_zscore(self) -> float:
        """
        Calculate fatigue Z-score
        
        Z = (μ_window - μ_baseline) / σ_baseline
        
        Z > 1.5 = Fatigued (significantly slower)
        """
        if self.baseline_ft_mean is None or len(self.flight_times) < self.window_size:
            return 0.0  # Not ready
        
        window_mean = np.mean(list(self.flight_times))
        
        if self.baseline_ft_std == 0:
            return 0.0
        
        z_score = (window_mean - self.baseline_ft_mean) / self.baseline_ft_std
        
        return z_score


if __name__ == "__main__":
    # Demo
    detector = EmotionalDetector()
    
    # Simulate frustrated state
    activity = {
        'errors': 4,
        'avg_response_time': 150,
        'session_duration': 45,
        'correct_streak': 0,
        'accuracy': 0.4
    }
    
    # Set high fatigue for demo
    detector.keystroke_monitor.baseline_ft_mean = 100
    detector.keystroke_monitor.baseline_ft_std = 20
    detector.keystroke_monitor.flight_times.extend([150] * 50)  # Slowed down
    
    emotion, meta = detector.analyze_state(activity)
    
    print(f"Emotion: {emotion}")
    print(f"Confidence: {meta['confidence']}")
    print(f"Fatigue Z-score: {meta.get('fatigue_zscore', 'N/A')}")
    print(f"Message: {meta['message']}")
    print(f"\nShould intervene? {detector.should_intervene(emotion, meta['confidence'])}")
    
    # Try again immediately (should be blocked by cooldown)
    print(f"Try again immediately: {detector.should_intervene(emotion, meta['confidence'])}")
