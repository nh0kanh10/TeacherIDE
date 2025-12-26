"""
User Profile Builder - v3.0 Foundation
Interactive questionnaire to capture user background and goals
"""
import json
from pathlib import Path
from datetime import datetime

PROFILE_PATH = Path(__file__).parent.parent / '.ai_coach' / 'user_profile.json'

BACKGROUND_OPTIONS = {
    "1": {"name": "chef", "domain": "cooking"},
    "2": {"name": "musician", "domain": "music"},
    "3": {"name": "teacher", "domain": "education"},
    "4": {"name": "engineer", "domain": "engineering"},
    "5": {"name": "designer", "domain": "design"},
    "6": {"name": "writer", "domain": "writing"},
    "7": {"name": "business", "domain": "business"},
    "8": {"name": "student", "domain": "academic"},
    "9": {"name": "other", "domain": "general"}
}

CAREER_GOALS = {
    "1": "high_salary",
    "2": "work_life_balance",
    "3": "remote_work",
    "4": "startup_founder",
    "5": "freelance",
    "6": "tech_lead",
    "7": "quick_employment"
}

LEARNING_STYLES = {
    "1": "visual",
    "2": "hands_on",
    "3": "reading",
    "4": "video",
    "5": "project_based"
}

def build_profile():
    """Interactive profile builder"""
    print("=" * 60)
    print("🎯 User Profile Builder - v3.0")
    print("=" * 60)
    print("\nThis helps the AI understand your background and goals")
    print("to provide personalized explanations and career guidance.\n")
    
    profile = {}
    
    # Background
    print("📚 What's your professional background?")
    for key, value in BACKGROUND_OPTIONS.items():
        print(f"  {key}. {value['name'].capitalize()}")
    
    choice = input("\nSelect (1-9): ").strip()
    if choice in BACKGROUND_OPTIONS:
        background = BACKGROUND_OPTIONS[choice]
        profile['background'] = background['name']
        profile['familiar_domain'] = background['domain']
    else:
        profile['background'] = "other"
        profile['familiar_domain'] = "general"
    
    # Career goals (multiple choice)
    print("\n🎯 What are your career goals? (Select all, comma-separated)")
    for key, value in CAREER_GOALS.items():
        print(f"  {key}. {value.replace('_', ' ').capitalize()}")
    
    goals_input = input("\nSelect (e.g., 1,2,7): ").strip()
    selected_goals = []
    for choice in goals_input.split(','):
        choice = choice.strip()
        if choice in CAREER_GOALS:
            selected_goals.append(CAREER_GOALS[choice])
    
    profile['career_goals'] = selected_goals if selected_goals else ["quick_employment"]
    
    # Learning style
    print("\n📖 What's your preferred learning style?")
    for key, value in LEARNING_STYLES.items():
        print(f"  {key}. {value.replace('_', ' ').capitalize()}")
    
    choice = input("\nSelect (1-5): ").strip()
    profile['learning_style'] = LEARNING_STYLES.get(choice, "hands_on")
    
    # Current skill level
    print("\n💪 Current programming experience?")
    print("  1. Complete beginner")
    print("  2. Some basics (variables, loops)")
    print("  3. Intermediate (functions, OOP)")
    print("  4. Advanced (design patterns, architecture)")
    
    choice = input("\nSelect (1-4): ").strip()
    skill_levels = {"1": "beginner", "2": "basic", "3": "intermediate", "4": "advanced"}
    profile['current_skill_level'] = skill_levels.get(choice, "basic")
    
    # Timestamps
    profile['created_at'] = datetime.now().isoformat()
    profile['updated_at'] = datetime.now().isoformat()
    
    # Save
    PROFILE_PATH.parent.mkdir(exist_ok=True)
    with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("✅ Profile created successfully!")
    print("=" * 60)
    print(f"\n📄 Saved to: {PROFILE_PATH}")
    print("\n📊 Your Profile:")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    print("\n💡 The AI will now use this to:")
    print("   - Generate analogies from your background domain")
    print("   - Recommend skills aligned with your career goals")
    print("   - Adapt teaching style to your preferences")
    
    return profile

def load_profile():
    """Load existing profile"""
    if not PROFILE_PATH.exists():
        return None
    
    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_profile():
    """Update existing profile"""
    profile = load_profile()
    if not profile:
        print("❌ No profile found. Run builder first.")
        return None
    
    print("\n📝 Current Profile:")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    
    print("\n🔄 What would you like to update?")
    print("  1. Background")
    print("  2. Career goals")
    print("  3. Learning style")
    print("  4. Skill level")
    print("  5. Cancel")
    
    choice = input("\nSelect (1-5): ").strip()
    
    if choice == "1":
        # Rebuild background
        print("\n📚 New background:")
        for key, value in BACKGROUND_OPTIONS.items():
            print(f"  {key}. {value['name'].capitalize()}")
        new_choice = input("\nSelect (1-9): ").strip()
        if new_choice in BACKGROUND_OPTIONS:
            background = BACKGROUND_OPTIONS[new_choice]
            profile['background'] = background['name']
            profile['familiar_domain'] = background['domain']
    
    elif choice == "2":
        print("\n🎯 New career goals:")
        for key, value in CAREER_GOALS.items():
            print(f"  {key}. {value.replace('_', ' ').capitalize()}")
        goals_input = input("\nSelect (e.g., 1,2,7): ").strip()
        selected_goals = []
        for g in goals_input.split(','):
            g = g.strip()
            if g in CAREER_GOALS:
                selected_goals.append(CAREER_GOALS[g])
        if selected_goals:
            profile['career_goals'] = selected_goals
    
    elif choice == "3":
        print("\n📖 New learning style:")
        for key, value in LEARNING_STYLES.items():
            print(f"  {key}. {value.replace('_', ' ').capitalize()}")
        new_choice = input("\nSelect (1-5): ").strip()
        if new_choice in LEARNING_STYLES:
            profile['learning_style'] = LEARNING_STYLES[new_choice]
    
    elif choice == "4":
        print("\n💪 New skill level:")
        print("  1. Complete beginner")
        print("  2. Some basics")
        print("  3. Intermediate")
        print("  4. Advanced")
        new_choice = input("\nSelect (1-4): ").strip()
        skill_levels = {"1": "beginner", "2": "basic", "3": "intermediate", "4": "advanced"}
        if new_choice in skill_levels:
            profile['current_skill_level'] = skill_levels[new_choice]
    
    else:
        print("❌ Cancelled")
        return profile
    
    profile['updated_at'] = datetime.now().isoformat()
    
    with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Profile updated!")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    
    return profile

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='User Profile Builder for v3.0')
    parser.add_argument('command', choices=['build', 'show', 'update'], 
                       help='build: create new profile, show: display current, update: modify')
    
    args = parser.parse_args()
    
    if args.command == 'build':
        build_profile()
    elif args.command == 'show':
        profile = load_profile()
        if profile:
            print("\n📊 Current Profile:")
            print(json.dumps(profile, indent=2, ensure_ascii=False))
        else:
            print("❌ No profile found. Run: python profile_builder.py build")
    elif args.command == 'update':
        update_profile()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
