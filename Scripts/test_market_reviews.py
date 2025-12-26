"""
Test market intel display
Create reviews for skills with market data
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'

def create_test_reviews():
    """Create reviews for top ROI skills"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get top 5 ROI skills
    cursor.execute("""
        SELECT name, id FROM skills 
        WHERE market_value > 0 
        ORDER BY market_value DESC 
        LIMIT 5
    """)
    
    skills = cursor.fetchall()
    
    print("Creating test reviews for top ROI skills:\n")
    
    for skill_name, skill_id in skills:
        # Check if review exists
        cursor.execute("""
            SELECT card_id FROM spaced_repetition 
            WHERE skill_id = ?
        """, (skill_id,))
        
        if cursor.fetchone():
            print(f"✅ {skill_name} - already has review")
            continue
        
        # Create review (due now for testing)
        cursor.execute("""
            INSERT INTO spaced_repetition (
                user_id, skill_id, stability, difficulty,
                elapsed_days, scheduled_days, reps, lapses,
                state, last_review, due
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1,  # user_id
            skill_id,
            5.0,  # stability
            5.0,  # difficulty
            0,  # elapsed_days
            0,  # scheduled_days
            1,  # reps
            0,  # lapses
            2,  # state (review)
            datetime.now().isoformat(),
            datetime.now().isoformat()  # due now!
        ))
        
        print(f"✅ {skill_name} - review created (due now)")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Test reviews created!")
    print("Run: python Scripts/review_cli.py due")

if __name__ == "__main__":
    create_test_reviews()
