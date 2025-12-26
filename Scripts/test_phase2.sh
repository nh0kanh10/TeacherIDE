# Phase 2 Complete - Comprehensive Test Suite

## Test 1: Meta-Learning Tracker
python Scripts/meta_learning_tracker.py

## Test 2: Long-Term Memory
python Scripts/long_term_memory.py

## Test 3: Adaptive Teaching
python Scripts/adaptive_teaching.py

## Test 4: Integration Test (All Phase 2)
python -c "
from meta_learning_tracker import MetaLearningTracker
from long_term_memory import LongTermMemory
from adaptive_teaching import AdaptiveTeachingSystem
from datetime import datetime, timedelta

print('🧪 PHASE 2 INTEGRATION TEST\n')

# 1. Meta-Learning
print('1. Meta-Learning Tracker...')
tracker = MetaLearningTracker()
session = {
    'user_id': 1,
    'session_start': datetime.now().isoformat(),
    'session_end': (datetime.now() + timedelta(minutes=30)).isoformat(),
    'duration_minutes': 30,
    'topics_covered': ['classes', 'inheritance'],
    'total_attempts': 8,
    'correct_attempts': 6,
    'avg_response_time': 55,
    'emotions_detected': ['optimal'],
    'fatigue_detected': False
}
tracker.save_session(session)
profile = tracker.get_learning_profile()
print(f'   ✅ Velocity: {profile[\"learning_velocity\"]} topics/week')

# 2. Long-Term Memory
print('\n2. Long-Term Memory...')
memory = LongTermMemory()
memory.save_misconception(
    'Python Inheritance',
    'Child class cannot override parent methods',
    'Child class CAN override parent methods - polymorphism',
    'When I successfully overrode __init__!',
    0.85
)
memories = memory.get_validated_memories()
print(f'   ✅ {len(memories)} validated memories')

# 3. Adaptive Teaching
print('\n3. Adaptive Teaching...')
teaching = AdaptiveTeachingSystem()
teaching.record_effectiveness('hands_on', 'Python OOP', 0.5, 0.75)
style = teaching.choose_teaching_style()
print(f'   ✅ Best style: {style}')

print('\n✅ ALL PHASE 2 FEATURES INTEGRATED!\n')
"
