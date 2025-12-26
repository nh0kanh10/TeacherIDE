"""
/review - Smart Review Command
Shows due reviews with FSRS v5 scheduling
"""
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime
from spaced_repetition import SpacedRepetitionManager, Rating
from emotional_detector import EmotionalDetector
from performance_guard import sync_guard

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'


def get_market_intel(skill_name: str):
    """Get market intelligence for a skill"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.job_count, m.salary_avg, s.market_value
        FROM market_data m
        LEFT JOIN skills s ON s.name = m.skill_name
        WHERE m.skill_name = ?
        ORDER BY m.date DESC
        LIMIT 1
    """, (skill_name,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        job_count, salary_avg, market_value = row
        # Calculate ROI (simplified)
        learning_time = 30  # hours
        roi = (market_value or 0) / learning_time if market_value else 0
        
        return {
            'job_count': job_count or 0,
            'salary_avg': salary_avg or 0,
            'roi': roi
        }
    
    return None

def show_due_reviews():
    """Show all due reviews"""
    manager = SpacedRepetitionManager()
    reviews = manager.get_due_reviews(limit=20)
    
    if not reviews:
        print("\n🎉 No reviews due right now!")
        print("   Great job staying on top of your learning!\n")
        return
    
    print(f"\n📚 You have {len(reviews)} skills to review:\n")
    
    for i, review in enumerate(reviews, 1):
        skill_name = review['skill_name']
        stability = review['stability']
        difficulty = review['difficulty']
        mastery = review.get('mastery_prob', 0)
        market = get_market_intel(skill_name)
        
        print(f"{i}. {skill_name}")
        print(f"   📊 Mastery: {mastery:.0%} | Difficulty: {difficulty:.1f}/10")
        print(f"   ⏱️  Stability: {stability:.1f} days")
        
        if market:
            print(f"   💰 Market: {market['job_count']} jobs/month, {market['salary_avg']/1e6:.0f}M VND avg")
            print(f"   🎯 ROI: {market['roi']/1e6:.1f}M VND per hour learned")
        
        print()

def review_skill_interactive(skill_name: str):
    """Review a skill interactively"""
    manager = SpacedRepetitionManager()
    
    print(f"\n📖 Reviewing: {skill_name}\n")
    print("How well did you remember this?")
    print("  1 - Again (forgot completely)")
    print("  2 - Hard (remembered with difficulty)")
    print("  3 - Good (recalled correctly)")
    print("  4 - Easy (trivial to recall)")
    
    while True:
        try:
            rating_input = input("\nYour rating (1-4): ").strip()
            rating = int(rating_input)
            
            if rating not in [1, 2, 3, 4]:
                print("❌ Please enter 1, 2, 3, or 4")
                continue
            
            # Process review
            result = manager.review_skill(skill_name, rating)
            
            print(f"\n✅ Review saved!")
            print(f"   Difficulty: {result['difficulty']:.2f}")
            print(f"   Stability: {result['stability']:.1f} days")
            print(f"   Next review in: {result['scheduled_days']} days")
            print(f"   Due date: {result['due'][:10]}")  # Just date part
            
            return True
            
        except ValueError:
            print("❌ Please enter a number 1-4")
        except KeyError as e:
            print(f"❌ Skill not found: {skill_name}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def review_session():
    """Interactive review session"""
    manager = SpacedRepetitionManager()
    detector = EmotionalDetector()
    
    reviews = manager.get_due_reviews(limit=10)
    
    if not reviews:
        print("\n🎉 No reviews due! You're all caught up!\n")
        return
    
    print(f"\n🎯 Starting review session with {len(reviews)} skills\n")
    
    completed = 0
    
    for review in reviews:
        skill_name = review['skill_name']
        
        # Show skill info
        market = get_market_intel(skill_name)
        
        print(f"\n{'='*50}")
        print(f"Skill: {skill_name}")
        print(f"Current mastery: {review.get('mastery_prob', 0):.0%}")
        
        if market:
            print(f"💰 Market value: {market['job_count']} jobs, {market['salary_avg']/1e6:.0f}M VND")
            print(f"🎯 Learning ROI: {market['roi']/1e6:.1f}M VND/hour")
        
        print('='*50)
        
        success = review_skill_interactive(skill_name)
        
        if success:
            completed += 1
        
        # Check if user wants to continue
        if completed < len(reviews):
            continue_review = input("\nContinue to next review? (y/n): ").strip().lower()
            if continue_review != 'y':
                break
    
    print(f"\n✅ Session complete! Reviewed {completed} skills.")
    
    # Show stats
    stats = manager.get_review_stats()
    print(f"\n📊 Your Review Stats:")
    print(f"   Total cards: {stats['total_cards']}")
    print(f"   Still due: {stats['due_now']}")
    print(f"   Avg stability: {stats['avg_stability_days']:.1f} days\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Smart Review with FSRS v5')
    parser.add_argument('action', nargs='?', default='session',
                       choices=['session', 'due', 'skill'],
                       help='Action: session (interactive), due (list), skill (review one)')
    parser.add_argument('--skill', help='Skill name to review')
    parser.add_argument('--rating', type=int, choices=[1,2,3,4],
                       help='Rating (1=Again, 2=Hard, 3=Good, 4=Easy)')
    
    args = parser.parse_args()
    
    if args.action == 'session':
        review_session()
    
    elif args.action == 'due':
        show_due_reviews()
    
    elif args.action == 'skill':
        if not args.skill:
            print("Error: --skill required")
        else:
            if args.rating:
                manager = SpacedRepetitionManager()
                result = manager.review_skill(args.skill, args.rating)
                print(f"✅ Next review: {result['scheduled_days']} days")
            else:
                review_skill_interactive(args.skill)
