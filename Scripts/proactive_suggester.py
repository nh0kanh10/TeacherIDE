"""
Proactive Suggestion Engine
✅ Fix #5: Conflict resolution with fatigue-awareness
"""
from typing import List, Dict, Tuple
from datetime import datetime

from v4_config import get_config
from event_bus import get_event_bus, EventType


class SuggestionType:
    """Suggestion types with priorities"""
    REVIEW_REMINDER = "review_reminder"
    FILL_GAP = "fill_gap"
    NEXT_SKILL = "next_skill"
    MARKET_TREND = "market_trend"
    PROJECT_IDEA = "project_idea"


class ProactiveSuggester:
    """
    Generates intelligent learning suggestions
    
    ✅ Fix #5: Conflict resolver with fatigue-awareness
    """
    
    def __init__(self):
        self.config = get_config("suggestion")
        self.event_bus = get_event_bus()
        self.suggestions_shown_this_session = 0
    
    def generate_suggestions(self, 
                           user_id: int = 1,
                           is_fatigued: bool = False) -> List[Dict]:
        """
        Generate prioritized suggestions
        
        Args:
            user_id: User ID
            is_fatigued: Whether user is currently fatigued
            
        Returns:
            List of suggestions, sorted by priority
        """
        suggestions = []
        
        # 1. Fill gaps (highest priority)
        gaps = self._detect_knowledge_gaps(user_id)
        for gap in gaps:
            suggestions.append({
                'type': SuggestionType.FILL_GAP,
                'skill': gap,
                'reason': f'Bạn biết {gap["dependent"]} nhưng chưa vững {gap["prerequisite"]}',
                'priority': self.config['priority_weights']['fill_gap']
            })
        
        # 2. Review reminders
        due_reviews = self._get_due_reviews(user_id)
        for skill in due_reviews[:3]:  # Top 3
            suggestions.append({
                'type': SuggestionType.REVIEW_REMINDER,
                'skill': skill,
                'reason': f'Đã {skill["days_since"]} ngày - nên ôn lại',
                'priority': self.config['priority_weights']['review_reminder']
            })
        
        # ✅ Fix #5: Fatigue-aware filtering
        if not is_fatigued:
            # 3. Next skill (only if NOT fatigued)
            next_skills = self._get_next_skills(user_id)
            for skill in next_skills[:2]:
                suggestions.append({
                    'type': SuggestionType.NEXT_SKILL,
                    'skill': skill,
                    'reason': f'Bạn đã master {skill["completed"]}, sẵn sàng cho bước tiếp',
                    'priority': self.config['priority_weights']['next_skill']
                })
            
            # 4. Market trends (only if NOT fatigued)
            trending = self._get_trending_skills()
            for skill in trending[:1]:
                suggestions.append({
                    'type': SuggestionType.MARKET_TREND,
                    'skill': skill,
                    'reason': f'Lương {skill["name"]} tăng {skill["growth"]}%',
                    'priority': self.config['priority_weights']['market_trend']
                })
        
        # Sort by priority
        suggestions.sort(key=lambda x: x['priority'], reverse=True)
        
        # ✅ Apply conflict resolution
        resolved = self._resolve_conflicts(suggestions, is_fatigued)
        
        # Limit to max_concurrent
        max_concurrent = self.config['max_concurrent']
        return resolved[:max_concurrent]
    
    def _resolve_conflicts(self, 
                          suggestions: List[Dict], 
                          is_fatigued: bool) -> List[Dict]:
        """
        ✅ Fix #5: Conflict resolution logic
        
        Rules:
        1. If fatigued: Disable next_skill and market_trend
        2. Max 1 suggestion at a time
        3. Fill gaps ALWAYS win
        """
        if is_fatigued:
            # Filter out disabled types
            disabled = self.config['fatigue_disabled_types']
            suggestions = [s for s in suggestions if s['type'] not in disabled]
        
        # Check session limit
        remaining = self.config['max_per_session'] - self.suggestions_shown_this_session
        if remaining <= 0:
            return []
        
        return suggestions[:remaining]
    
    def show_suggestion(self, suggestion: Dict) -> bool:
        """
        Show a suggestion and emit event
        
        Returns:
            True if shown, False if limit reached
        """
        if self.suggestions_shown_this_session >= self.config['max_per_session']:
            return False
        
        self.suggestions_shown_this_session += 1
        
        # Emit event
        self.event_bus.publish(EventType.SUGGESTION_SHOWN, {
            'suggestion_type': suggestion['type'],
            'skill_name': suggestion.get('skill', {}).get('name', 'unknown'),
            'priority': suggestion['priority'],
            'reason': suggestion['reason']
        })
        
        return True
    
    # Placeholder methods (to be implemented in Phase 1)
    def _detect_knowledge_gaps(self, user_id: int) -> List[Dict]:
        """Find skills where user knows advanced but weak on prereqs"""
        # TODO: Query skill_graph + skill_mastery
        return []
    
    def _get_due_reviews(self, user_id: int) -> List[Dict]:
        """Get skills due for spaced repetition review"""
        # TODO: Query spaced_repetition table
        return []
    
    def _get_next_skills(self, user_id: int) -> List[Dict]:
        """Get skills user is ready to learn based on mastery"""
        # TODO: Query skill_graph for next logical steps
        return []
    
    def _get_trending_skills(self) -> List[Dict]:
        """Get market trending skills"""
        # TODO: Query skill_roi table
        return []


if __name__ == "__main__":
    # Demo fatigue-aware conflict resolution
    suggester = ProactiveSuggester()
    
    print("📌 Suggestions when NOT fatigued:\n")
    suggestions = suggester.generate_suggestions(is_fatigued=False)
    for s in suggestions:
        print(f"  {s['type']}: Priority {s['priority']}")
    
    print("\n📌 Suggestions when FATIGUED:\n")
    suggestions_tired = suggester.generate_suggestions(is_fatigued=True)
    for s in suggestions_tired:
        print(f"  {s['type']}: Priority {s['priority']}")
    
    print(f"\n✅ Fatigue filtering: {SuggestionType.NEXT_SKILL} and {SuggestionType.MARKET_TREND} disabled when tired")
