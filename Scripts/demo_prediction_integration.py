"""
Demo: End-to-End Prediction + Feedback Loop Integration
Shows full workflow from prediction → teaching → feedback
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from teaching_helper_v4 import TeachingSession, update_skill_mastery
import sqlite3
import time

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'


def demo_full_workflow():
    """Demonstrates prediction + teaching + feedback loop"""
    
    print("🎓 Full Prediction + Feedback Loop Demo\n")
    print("=" * 70)
    
    # Test skill
    skill_name = "python_decorators"
    
    # === PHASE 1: START SESSION WITH PREDICTION ===
    print(f"\n📚 PHASE 1: Start Teaching Session for '{skill_name}'")
    print("-" * 70)
    
    session = TeachingSession(skill_name=skill_name)
    
    # Generate prediction
    print("\n🔮 Generating prediction...")
    prediction_context = session.predict_for_skill(skill_name)
    
    print(f"\n✅ Prediction Generated:")
    print(f"   Mode: {prediction_context.teaching_mode}")
    print(f"   Struggle Probability: {prediction_context.struggle_probability:.0%}")
    print(f"   Confidence: {prediction_context.confidence:.0%}")
    print(f"   Recommended Style: {prediction_context.recommended_style}")
    print(f"   Strategy: {prediction_context.socratic_strategy}")
    print(f"   Prediction ID: {session.prediction_id}")
    
    # === PHASE 2: SIMULATE TEACHING SESSION ===
    print(f"\n\n📖 PHASE 2: Teaching Session (simulated)")
    print("-" * 70)
    
    # Simulate practice attempts with response times
    attempts = [
        (True, 45.2),   # Correct, 45 seconds
        (False, 120.5), # Wrong, 120 seconds
        (True, 60.3),   # Correct, 60 seconds
        (True, 50.1),   # Correct, 50 seconds
    ]
    
    print("\n📝 Recording practice attempts:")
    for i, (correct, response_time) in enumerate(attempts, 1):
        session.record_attempt(skill_name, correct, response_time)
        status = "✅" if correct else "❌"
        print(f"   Attempt {i}: {status} ({response_time:.1f}s)")
    
    # Simulate mastery update
    accuracy = session.correct_answers / session.total_attempts
    print(f"\n📊 Session Stats:")
    print(f"   Accuracy: {accuracy:.0%}")
    print(f"   Total Attempts: {session.total_attempts}")
    print(f"   Avg Response Time: {sum(session.response_times)/len(session.response_times):.1f}s")
    
    # Update mastery (simulates learning)
    final_correct = session.total_attempts >= 3 and accuracy >= 0.75
    update_skill_mastery(skill_name, final_correct)
    
    time.sleep(0.5)  # Brief pause for mastery to propagate
    
    # === PHASE 3: RECORD FEEDBACK ===
    print(f"\n\n📈 PHASE 3: Record Teaching Outcome (Feedback Loop)")
    print("-" * 70)
    
    session.record_teaching_outcome()
    
    print("\n✅ Feedback recorded!")
    
    # === PHASE 4: SHOW PREDICTION ACCURACY ===
    print(f"\n\n📊 PHASE 4: Prediction Accuracy Metrics")
    print("-" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get this prediction's accuracy
    cursor.execute("""
        SELECT prediction_correct, actual_struggled, predicted_action, 
               mastery_before, mastery_after
        FROM prediction_tracking
        WHERE id = ?
    """, (session.prediction_id,))
    
    row = cursor.fetchone()
    if row:
        pred_correct, actual_struggled, predicted_action, mastery_before, mastery_after = row
        
        print(f"\n🎯 This Prediction:")
        print(f"   Predicted: {'Scaffold needed' if predicted_action == 'scaffold' else 'Normal teaching'}")
        print(f"   Actual: {'User struggled' if actual_struggled else 'User did well'}")
        print(f"   Mastery: {mastery_before:.0%} → {mastery_after:.0%}")
        print(f"   Prediction Correct: {'✅ YES' if pred_correct else '❌ NO'}")
    
    # Get overall accuracy
    cursor.execute("SELECT * FROM prediction_accuracy")
    accuracy_row = cursor.fetchone()
    
    if accuracy_row:
        total, correct, accuracy_pct, avg_conf, scaffold_count, normal_count = accuracy_row
        
        print(f"\n📈 Overall Accuracy:")
        print(f"   Total Predictions: {total}")
        print(f"   Correct: {correct}/{total}")
        print(f"   Accuracy: {accuracy_pct:.1f}%")
        print(f"   Avg Confidence: {avg_conf:.0%}")
        print(f"   Scaffolds Used: {scaffold_count}")
        print(f"   Normal Teaching: {normal_count}")
    
    conn.close()
    
    # === PHASE 5: SHOW RESPONSE TIMES STORED ===
    print(f"\n\n⏱️  PHASE 5: Response Times Stored")
    print("-" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*), AVG(response_time_sec)
        FROM response_times
        WHERE skill_name = ?
    """, (skill_name,))
    
    count, avg_time = cursor.fetchone()
    print(f"\n✅ Response Times for '{skill_name}':")
    print(f"   Total Recorded: {count}")
    print(f"   Average Time: {avg_time:.1f}s")
    
    conn.close()
    
    # Done
    session.end_session()
    
    print(f"\n\n{'=' * 70}")
    print("✅ DEMO COMPLETE!")
    print("\nKey Features Demonstrated:")
    print("  ✅ Auto prediction before teaching")
    print("  ✅ Response time persistence to DB")
    print("  ✅ Feedback loop (prediction vs actual)")
    print("  ✅ Prediction accuracy tracking")
    print("  ✅ Self-learning potential")
    print("=" * 70)


if __name__ == "__main__":
    demo_full_workflow()
