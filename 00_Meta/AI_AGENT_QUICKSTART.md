# QUICK START for AI Agents
**5-Minute Guide to Using v3.0 Cognitive Teaching System**

---

## 🚦 3-Step Teaching Flow

### STEP 1: Check Readiness (BEFORE teaching)
```bash
python Scripts/knowledge_tracer.py recommend --skill [topic]
```
- ✅ "Teach [topic]" → Go ahead
- ⚠️ "Teach [prereq] first" → Backtrack!

### STEP 2: Personalize (DURING teaching)
```bash
python Scripts/ai_teach.py concept [topic]
```
Auto-shows:
- 💡 Analogy (user background)
- 💰 ROI (salary, time)
- 📊 Mastery (current %)

### STEP 3: Update (AFTER practice)
```bash
# Success:
python Scripts/knowledge_tracer.py update --skill [topic] --correct

# Failure:
python Scripts/knowledge_tracer.py update --skill [topic]
```

---

## 🎯 When to Use Each Tool

| Tool | Use When | Example |
|------|----------|---------|
| `profile_builder.py` | First session (once) | Get user background |
| `quick_assessment.py` | First session (once) | Baseline mastery |
| `knowledge_tracer.py recommend` | **Before EVERY new topic** | Check readiness |
| `ai_teach.py concept` | **Teaching explanation** | Show analogy+ROI+mastery |
| `analogy_generator.py` | Need custom analogy | Generate SMT analogy |
| `skill_roi_calculator.py` | Career guidance | Compare skill value |
| `knowledge_tracer.py update` | **After EVERY practice** | Update BKT |
| `knowledge_tracer.py check` | User stuck/confused | Diagnose gaps |

---

## ⚡ Power Combos

### Combo 1: Smart Backtracking
```bash
# User asks about decorators
python Scripts/knowledge_tracer.py recommend --skill decorators
# → "Teach higher_order_functions first"

# Explain why, teach prereq
python Scripts/ai_teach.py concept higher_order_functions

# After user practices
python Scripts/knowledge_tracer.py update --skill higher_order_functions --correct

# Check if ready now
python Scripts/knowledge_tracer.py recommend --skill decorators
# → "Teach decorators" ✅
```

### Combo 2: Career-Driven Learning
```bash
# User: "What should I learn?"
python Scripts/skill_roi_calculator.py list

# Show top 5 ROI skills
# User picks one
python Scripts/knowledge_tracer.py recommend --skill [chosen_skill]
# Check if ready or need prereqs
```

### Combo 3: Personalized Teaching
```bash
# Get user background
cat .ai_coach/user_profile.json

# Use in analogy
python Scripts/analogy_generator.py generate --concept function --llm
# → Generates SMT prompt with user background
# → You create relational analogy
```

---

## 🚨 CRITICAL RULES

1. **ALWAYS check `recommend` before teaching new topic**
2. **ALWAYS update mastery after practice**
3. **NEVER teach without knowing user background** (run profile_builder first)
4. **NEVER ignore weak prerequisites** (backtrack if recommended)

---

## 📊 Quick Diagnostics

**User struggling?**
```bash
python Scripts/knowledge_tracer.py check --skill [current_topic]
```
Look at:
- Mastery < 30% → Reteach basics
- Weak prereqs → Backtrack
- Low attempts → Need more practice

**Need curriculum ideas?**
```bash
python Scripts/skill_roi_calculator.py list | head -10
```
→ Top 10 high-value skills

**Check user readiness for advanced path?**
```bash
# Example: Machine Learning path
python Scripts/knowledge_tracer.py check --skill python
python Scripts/knowledge_tracer.py check --skill numpy
python Scripts/knowledge_tracer.py check --skill linear_algebra
```
→ All > 80%? Ready for ML!

---

## 🎓 Optimization Tips

**Pre-load at session start:**
```bash
# User profile
cat .ai_coach/user_profile.json

# Weak skills
SELECT skill_name, mastery_prob FROM skill_mastery WHERE mastery_prob < 0.6;

# Recent progress
SELECT skill_name, mastery_prob FROM skill_mastery ORDER BY last_practiced DESC LIMIT 5;
```

**Cache good analogies:**
After generating excellent analogy:
```python
# Save for reuse
python Scripts/teaching_helper.py save_analogy \
  --concept [concept] --domain [user_bg] --text "..." --quality 5
```

---

## ✅ Success Checklist

Before ending session, verify:
- [ ] All practice attempts updated in BKT
- [ ] Important concepts saved to vault
- [ ] User knows what to practice next
- [ ] Progress tracked (mastery improved?)

---

**Read full guide:** `00_Meta/AI_AGENT_GUIDE.md`

**Remember:** Check readiness → Personalize → Update mastery. That's the formula! 🚀
