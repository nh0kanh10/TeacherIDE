---
description: Bắt đầu học - AI Agent tự động setup và dạy với v4.0 features
---

# /hoc - Workflow Học Tập v4.0

Workflow hoàn chỉnh với **10 tính năng v4.0** tích hợp.

---

## 🎯 Overview

Workflow `/hoc` giờ bao gồm:
- ✅ FSRS v5 Spaced Repetition
- ✅ Emotional Detection (keystroke + fatigue)
- ✅ Meta-Learning Tracking
- ✅ Circadian Optimization
- ✅ Statistical Prediction
- ✅ Adaptive Teaching Styles

---

## 📋 Workflow Steps

### 1. Pre-Session Check (v4.0 NEW)

```bash
# Check due reviews first
python Scripts/review_cli.py due

# Check best study time
python Scripts/circadian_optimizer.py
```

**AI will:**
- Show any due FSRS reviews
- Recommend if now is peak time for your chosen topic

---

### 2. Start Learning Session

```bash
python Scripts/teaching_helper_v4.py session
```

**Session tracking includes:**
- Duration, attempts, accuracy
- Response times
- Emotional state monitoring
- Fatigue detection

---

### 3. Learning Phase

**AI adapts based on:**

**Your Emotional State:**
- Frustrated (3+ errors, slow) → Simplify or break
- Tired (2hr+ session) → Suggest rest
- Optimal → Continue normally

**Learning Style (Adaptive Teaching):**
- AI uses your best style (hands_on, visual, theoretical, etc.)
- Epsilon-Greedy: 20% tries new styles to discover better ones

**Struggle Prediction:**
- Before new complex topics, AI predicts if you'll struggle
- ≥65% struggle → Add scaffolding (more examples)
- <65% → Normal teaching

---

### 4. Practice & Review

**After learning new concept:**

```python
# Save knowledge with FSRS review
python Scripts/teaching_helper_v4.py save \
  --title "Python Classes" \
  --content "..." \
  --skill classes \
  --rating 3  # 1=Again, 2=Hard, 3=Good, 4=Easy
```

**FSRS will:**
- Calculate next review (e.g., 28 days for Good rating)
- Track stability and difficulty
- NO "Ease Hell" - maintains memory trace

---

### 5. Post-Session Analysis (v4.0 NEW)

**Meta-Learning Profile:**
```bash
python Scripts/meta_learning_tracker.py
```

**Shows:**
- Learning velocity (topics/week)
- Accuracy trend (improving/stable/declining)
- Optimal hours for you
- Total sessions

**Long-Term Memory:**
- Misconceptions saved (confidence ≥70%)
- Error patterns detected (≥2 occurrences)
- Concept links created

---

### 6. Plan Next Steps (v4.0 NEW)

**6-Week Curriculum:**
```bash
python Scripts/curriculum_planner.py
```

**DAG-based plan:**
- Weeks 1-2: Fundamentals
- Weeks 3-4: Data Structures
- Weeks 5-6: Advanced Topics

---

## 🔥 Complete Example Session

### Morning Study (Peak Hours)

```bash
# 1. Check if good time
python Scripts/circadian_optimizer.py
# Output: "Peak hour! Great for complex topics"

# 2. Check reviews first
python Scripts/review_cli.py due
# Output: "2 skills due for review"

# 3. Do reviews
python Scripts/review_cli.py session
# Interactive reviews with FSRS

# 4. Start learning
python Scripts/teaching_helper_v4.py session
```

**During session:**
- AI detects you're making 3+ errors → "Có vẻ mệt rồi. Nghỉ 5 phút nhé?"
- AI uses your best style (e.g., hands_on with coding exercises)
- AI predicts struggle on recursion (85% prob) → Adds extra examples

**After session:**
```bash
# Save with FSRS
python Scripts/teaching_helper_v4.py save \
  --title "Recursion Basics" \
  --content "..." \
  --skill recursion \
  --rating 2  # Hard but managed

# Check progress
python Scripts/meta_learning_tracker.py
# Velocity: 2.1 topics/week (improving!)
```

---

## 🎓 Features by Phase

### Phase 1: During Learning
- **FSRS v5:** Next review in 8-28 days (based on rating)
- **Emotional Detection:** Cooldown 10 min between interventions
- **Proactive Suggestions:** "You mastered X, try Y next?"

### Phase 2: Tracking Progress
- **Meta-Learning:** Sessions tracked, velocity calculated
- **Long-Term Memory:** Misconceptions saved (90% confidence)
- **Adaptive Teaching:** Best style auto-selected

### Phase 3: Planning Ahead
- **Statistical Prediction:** 65%+ struggle → scaffold
- **Circadian:** Peak 9-10am, non-peak 8-9pm
- **Curriculum:** Next 6 weeks planned with dependencies

### Phase 4: Background
- **Silent Assistant:** File changes logged (no spam)

---

## ⚙️ Configuration

Kill-switches in `.ai_coach/config.json`:

```json
{
  "v4_features": {
    "spaced_repetition": true,
    "emotion_detection": true,
    "emotion_threshold": 0.7,
    "proactive_suggestions": true,
    "max_suggestions_per_session": 3
  }
}
```

---

## 📊 Session Example Output

```
📊 Session Activity:
   Attempts: 10
   Accuracy: 70%

😊 Emotional State: optimal
   
📈 FSRS Update:
   Next review: 28 days
   Stability: 3.1 days

🎓 Teaching Style: hands_on (0.85 effectiveness)

📅 Next Topics (from curriculum):
   Week 3-4: list_comprehension, dictionaries
```

---

## 🚀 Pro Tips

1. **Morning = Complex topics** (if peak hours detected)
2. **Evening = Reviews** (non-peak, easier tasks)
3. **Rating 3 (Good)** most of the time for optimal spacing
4. **Session < 90 min** before fatigue kicks in
5. **Check velocity weekly** to stay on track

---

## 🔧 Troubleshooting

**No reviews due?**
- Good! You're on top of learning
- Start new topics from curriculum

**Too many reviews?**
- Do 5-10 per day
- Don't let backlog grow

**AI interventions too much?**
- Check emotion_threshold in config (increase to 0.8)
- Cooldown is 10 min by default

**Wrong teaching style?**
- Epsilon-Greedy will explore alternatives (20% of time)
- Give it 10-15 sessions to find your best style

---

**v4.0 Integration Complete!** 🎉

All 10 features working seamlessly in `/hoc` workflow.
