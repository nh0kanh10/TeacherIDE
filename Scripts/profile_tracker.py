"""
Profile Tracker - AI learns user over time
v4.7 Week 3

Automatically track user preferences and decisions
"""
import json
from pathlib import Path
from datetime import datetime

PROFILE_DIR = Path(__file__).parent.parent / '.ai_coach'
LOG_FILE = PROFILE_DIR / 'interaction_log.md'
PROFILE_FILE = PROFILE_DIR / 'user_profile.json'


class ProfileTracker:
    """
    Track user preferences and decisions
    """
    
    def __init__(self):
        self.profile_dir = PROFILE_DIR
        self.profile_dir.mkdir(exist_ok=True)
        
    def log_decision(self, decision: str, reason: str, category: str = "general"):
        """
        Log a user decision
        
        Args:
            decision: What was decided ("Rejected GPT-4")
            reason: Why ("Too expensive")
            category: Type (technical, budget, scope, etc.)
        """
        timestamp = datetime.now().isoformat()
        
        entry = f"\n### Decision: {decision}\n"
        entry += f"- **Time:** {timestamp}\n"
        entry += f"- **Reason:** {reason}\n"
        entry += f"- **Category:** {category}\n"
        
        # Append to log
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        print(f"✅ Logged: {decision}")
    
    def update_preference(self, key: str, value: any):
        """
        Update user preference
        
        Args:
            key: Preference key ("budget_sensitivity")
            value: Value ("high", "low", etc.)
        """
        # Load existing profile
        if PROFILE_FILE.exists():
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                profile = json.load(f)
        else:
            profile = {}
        
        # Update
        profile[key] = value
        profile['last_updated'] = datetime.now().isoformat()
        
        # Save
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated preference: {key} = {value}")
    
    def get_profile(self):
        """Get current user profile"""
        if PROFILE_FILE.exists():
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_summary(self) -> str:
        """
        Get profile summary for AI to read
        
        Returns quick summary of key preferences
        """
        if not LOG_FILE.exists():
            return "No interaction history yet."
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Extract key patterns
        summary = "📋 User Profile Summary:\n\n"
        
        if "budget" in log_content.lower():
            summary += "- Budget-sensitive (prefers $0 > $50)\n"
        
        if "local-first" in log_content.lower():
            summary += "- Architecture: Local-first always\n"
        
        if "pragmatic" in log_content.lower():
            summary += "- Approach: Pragmatic > Perfect\n"
        
        if "roi" in log_content.lower():
            summary += "- Focus: High ROI features only\n"
        
        summary += "\n📖 Full log: .ai_coach/interaction_log.md"
        
        return summary


def demo():
    """Demo profile tracking"""
    tracker = ProfileTracker()
    
    print("🧪 Profile Tracker Demo\n")
    
    # Log some decisions
    tracker.log_decision(
        decision="Rejected Cloud-Native",
        reason="Too expensive + overkill for solo dev",
        category="architecture"
    )
    
    tracker.log_decision(
        decision="Manual market data > Scraping",
        reason="Pragmatic, ships faster",
        category="implementation"
    )
    
    # Update preferences
    tracker.update_preference("budget_sensitivity", "high")
    tracker.update_preference("over_engineering_threshold", "low")
    tracker.update_preference("preferred_language", "vietnamese")
    
    # Show summary
    print("\n" + tracker.get_summary())
    
    print("\n✅ Profile tracking ready!")
    print("   AI will read this next session")


if __name__ == "__main__":
    demo()
