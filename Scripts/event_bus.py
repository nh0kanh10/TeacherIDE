"""
Event Bus System for v4.0 Premium Tutor
Central event dispatcher to coordinate all v4 features
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Any
from enum import Enum

# Event types
class EventType(Enum):
    """Core event types for v4.0 system"""
    USER_ACTION = "user_action"
    ERROR_OCCURRED = "error_occurred"
    REVIEW_DONE = "review_done"
    EMOTION_DETECTED = "emotion_detected"
    SUGGESTION_SHOWN = "suggestion_shown"
    SUGGESTION_ACCEPTED = "suggestion_accepted"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    SKILL_MASTERY_UPDATED = "skill_mastery_updated"
    KNOWLEDGE_SAVED = "knowledge_saved"


# ✅ Event versioning for future migration
EVENT_VERSION = "v4.0"

# ✅ Event schema validation
EVENT_SCHEMAS = {
    EventType.REVIEW_DONE: ['skill_name', 'rating', 'correct', 'new_stability', 'new_difficulty'],
    EventType.EMOTION_DETECTED: ['emotion', 'confidence', 'fatigue_zscore'],
    EventType.SKILL_MASTERY_UPDATED: ['skill_name', 'old_mastery', 'new_mastery', 'correct'],
    EventType.SUGGESTION_SHOWN: ['suggestion_type', 'skill_name', 'priority'],
    # Add more as needed
}


class EventBus:
    """
    Central event dispatcher for v4.0 features
    
    Prevents spaghetti code by decoupling modules:
    - Emotional detector listens to ERROR_OCCURRED
    - Spaced repetition listens to REVIEW_DONE
    - Proactive suggester listens to SESSION_START
    """
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
        self._event_log: List[Dict[str, Any]] = []
        self._max_log_size = 1000
        
    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
                      Signature: callback(event_data: Dict) -> None
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        self._listeners[event_type].append(callback)
        print(f"✅ Subscribed to {event_type.value}")
    
    def publish(self, event_type: EventType, event_data: Dict[str, Any]):
        """
        Publish an event to all listeners
        
        Args:
            event_type: Type of event
            event_data: Event payload (dict)
        """
        # ✅ Validate schema if defined
        if event_type in EVENT_SCHEMAS:
            required_keys = EVENT_SCHEMAS[event_type]
            missing = [k for k in required_keys if k not in event_data]
            if missing:
                print(f"⚠️ Event {event_type.value} missing keys: {missing}")
        
        # Log event with version
        event = {
            'version': EVENT_VERSION,  # ✅ For migration
            'type': event_type.value,
            'timestamp': datetime.now().isoformat(),
            'data': event_data
        }
        self._event_log.append(event)
        
        # Trim log if too large
        if len(self._event_log) > self._max_log_size:
            self._event_log = self._event_log[-self._max_log_size:]
        
        # Notify listeners
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    print(f"⚠️ Error in event listener for {event_type.value}: {e}")
    
    def get_recent_events(self, event_type: EventType = None, limit: int = 10) -> List[Dict]:
        """Get recent events, optionally filtered by type"""
        events = self._event_log
        
        if event_type:
            events = [e for e in events if e['type'] == event_type.value]
        
        return events[-limit:]
    
    def clear_log(self):
        """Clear event log (for testing or memory management)"""
        self._event_log = []


# Global singleton
_event_bus = None

def get_event_bus() -> EventBus:
    """Get global event bus instance (singleton)"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


# Example usage / integration helpers

def emit_error(file_path: str, line_number: int, error_type: str, message: str):
    """Helper to emit error events"""
    bus = get_event_bus()
    bus.publish(EventType.ERROR_OCCURRED, {
        'file_path': file_path,
        'line_number': line_number,
        'error_type': error_type,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })


def emit_skill_update(skill_name: str, old_mastery: float, new_mastery: float, correct: bool):
    """Helper to emit skill mastery updates"""
    bus = get_event_bus()
    bus.publish(EventType.SKILL_MASTERY_UPDATED, {
        'skill_name': skill_name,
        'old_mastery': old_mastery,
        'new_mastery': new_mastery,
        'correct': correct,
        'delta': new_mastery - old_mastery
    })


def emit_session_start(user_id: int = 1):
    """Helper to emit session start"""
    bus = get_event_bus()
    bus.publish(EventType.SESSION_START, {
        'user_id': user_id,
        'timestamp': datetime.now().isoformat()
    })


def emit_session_end(user_id: int = 1, duration_minutes: int = 0):
    """Helper to emit session end"""
    bus = get_event_bus()
    bus.publish(EventType.SESSION_END, {
        'user_id': user_id,
        'duration_minutes': duration_minutes,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == "__main__":
    # Demo usage
    print("🔧 Event Bus Demo\n")
    
    bus = get_event_bus()
    
    # Subscribe to errors
    def on_error(data):
        print(f"❌ Error detected: {data['error_type']} at {data['file_path']}:{data['line_number']}")
    
    def on_mastery_update(data):
        print(f"📊 Mastery updated: {data['skill_name']} {data['old_mastery']:.0%} → {data['new_mastery']:.0%}")
    
    bus.subscribe(EventType.ERROR_OCCURRED, on_error)
    bus.subscribe(EventType.SKILL_MASTERY_UPDATED, on_mastery_update)
    
    # Emit events
    emit_error('test.py', 45, 'NameError', 'undefined variable')
    emit_skill_update('python_functions', 0.6, 0.7, True)
    emit_session_start()
    
    # Check log
    print(f"\n📝 Recent events: {len(bus.get_recent_events())}")
    for event in bus.get_recent_events(limit=3):
        print(f"  - {event['type']} at {event['timestamp']}")
