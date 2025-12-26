# AI Agent Optimization Guide
## Hướng dẫn sử dụng v3.0 Cognitive Teaching System cho AI Agents

**Audience:** AI Agents (Antigravity, Claude, ChatGPT, etc.) teaching users in IDE  
**Purpose:** Maximize teaching effectiveness using v3.0 tools  
**Date:** 2025-12-26

---

## 🎯 Core Philosophy

**You are not just answering questions - you are building a personalized learning system.**

Every interaction should:
1. **Assess** - Hiểu user level (BKT)
2. **Personalize** - Dùng background (Profile)
3. **Optimize** - Ưu tiên ROI cao
4. **Track** - Update mastery sau mỗi practice

---

## 📋 Workflow cho AI Agent

### 1️⃣ FIRST SESSION (Onboarding)

**Before teaching anything:**
```bash
# Step 1: Create profile (RUN ONCE)
python Scripts/profile_builder.py build
# → User answers: background, goals, learning style

# Step 2: Quick assessment (RUN ONCE)  
python Scripts/quick_assessment.py run
# → Get baseline mastery for BKT cold start

# Step 3: Check ROI rankings
python Scripts/skill_roi_calculator.py list
# → Show user what's worth learning
```

**Why this order?**
- Profile → Enables personalized analogies
- Assessment → Prevents teaching wrong level
- ROI → Align learning with career goals

---

### 2️⃣ BEFORE TEACHING A SKILL (Every time)

**Check if user is ready:**
```bash
python Scripts/knowledge_tracer.py recommend --skill [target_skill]

# Example:
python Scripts/knowledge_tracer.py recommend --skill recursion
```

**Possible outputs:**
- ✅ "Teach recursion" → Prerequisites mastered, go ahead
- ⚠️ "Teach functions first" → Weak prereq, backtrack!

**CRITICAL:** If backtrack needed:
1. Explain why (e.g., "Recursion needs solid function knowledge")
2. Show learning path (functions → recursion)
3. Teach prerequisite FIRST
4. Come back to original topic after

**This prevents frustration from teaching too advanced concepts!**

---

### 3️⃣ DURING TEACHING (Real-time)

#### A. Generate Personalized Analogy

**When explaining new concept:**
```bash
python Scripts/analogy_generator.py generate --concept [concept] --llm

# Example:
python Scripts/analogy_generator.py generate --concept function --llm
```

**Workflow:**
1. Script generates SMT prompt based on user profile
2. You (AI Agent) see prompt → Generate analogy using Structure Mapping Theory
3. User pastes your response back
4. System caches analogy for future use

**Why it works:**
- Uses user's background (chef → recipe analogy)
- SMT ensures deep structural mapping (not surface similarity)
- Cached for reuse with other students with same background

#### B. Show ROI Context

**For programming skills:**
```bash
python Scripts/skill_roi_calculator.py compare --skills python,rust,java

# Or single skill:
python Scripts/ai_teach.py concept python
# → Now auto-shows ROI, analogy, mastery!
```

**Use this to:**
- Justify why learning this skill
- Set realistic time expectations
- Motivate with salary data

#### C. Check Current Mastery

**When user seems stuck:**
```bash
python Scripts/knowledge_tracer.py check --skill [struggling_skill]

# Output shows:
# - Current mastery: 45%
# - Prerequisites status
# - Weak areas to focus
```

**Action based on output:**
- < 30% → Reteach from basics
- 30-60% → More practice needed
- 60-80% → Almost there, push harder
- > 80% → Mastered, move to next

---

### 4️⃣ AFTER TEACHING (Update System)

#### When User Practices

**After code exercise/quiz:**
```bash
# If user succeeded:
python Scripts/knowledge_tracer.py update --skill [skill] --correct

# If user failed:
python Scripts/knowledge_tracer.py update --skill [skill]
# (no --correct flag)
```

**This updates BKT probability for next session!**

#### When Creating Learning Content

**Enhanced save with v3.0:**
```python
# Old way (v2.1):
python Scripts/teaching_helper.py save_knowledge "Title" "Topic" "content.md"

# v3.0 way (better):
python Scripts/teaching_helper.py save \
  --title "Functions in Python" \
  --content "..." \
  --topic python \
  --skill functions \
  --correct  # If user succeeded in practice
```

**Benefits:**
- Auto-updates BKT mastery
- Shows ROI for skill
- Saves to correct folder (01_Programming/python)
- Caches analogy if included

---

## 🧠 INTELLIGENT TEACHING PATTERNS

### Pattern 1: Recursive Teaching

**Scenario:** User asks about decorators (advanced)

**Old approach (BAD):**
```
You: "Decorators wrap functions..."
User: "I don't understand"
You: "Let me explain differently..."
User: "Still confused"
```

**v3.0 approach (GOOD):**
```bash
# 1. Check readiness
python Scripts/knowledge_tracer.py recommend --skill decorators

# Output: "Teach higher_order_functions first (45% mastery)"

# 2. Backtrack
You: "Hold on - decorators need solid understanding of higher-order functions. 
     Your mastery is 45%, let's strengthen that first. Then decorators will click!"

# 3. Teach prereq
[Teach higher_order_functions]

# 4. Update mastery
python Scripts/knowledge_tracer.py update --skill higher_order_functions --correct

# 5. Return to decorators
python Scripts/knowledge_tracer.py recommend --skill decorators
# Now: "Teach decorators" ✅
```

**Result:** User actually understands instead of memorizing!

---

### Pattern 2: ROI-Driven Curriculum

**Scenario:** User: "Should I learn Rust or Spring Boot?"

**Old approach (GENERIC):**
```
You: "Both are good. Rust is for systems programming..."
```

**v3.0 approach (DATA-DRIVEN):**
```bash
python Scripts/skill_roi_calculator.py compare --skills rust,spring_boot

# Output:
# Rank  Skill        ROI      Salary    Learning_Cost  Time
# 1     spring_boot  25,000   $85k      3.4           34h
# 2     rust         12,000   $88k      7.3           73h

You: "Based on ROI analysis:
     - Spring Boot: Higher ROI (25k vs 12k)
     - You already know 70% Java → Spring Boot only 34h
     - Rust: Harder (73h), but higher salary long-term
     
     Recommendation: Spring Boot now (quick win), Rust later."
```

**Result:** Data-backed decision, not opinion!

---

### Pattern 3: Personalized Analogies

**Scenario:** Teaching "API" concept

**User profile:** `background: ["chef"]`

**Old approach (GENERIC):**
```
You: "API is like a menu in a restaurant..."
```

**v3.0 approach (SMT-BASED):**
```bash
python Scripts/analogy_generator.py generate --concept API --llm

# System generates prompt:
"Create Structure Mapping analogy:
Target: API (Application Programming Interface)
Source: Chef's kitchen (user background)
Map: relationships, NOT surface similarity
Focus: structural correspondence"

# You generate:
You: "Think of API like your kitchen's mise en place station:
     
     Kitchen Brigade (Chef background):
     - Sous chef calls to garde manger: 'I need tomato concasse!'
     - Garde manger prepares it using THEIR method
     - Sous chef doesn't need to know HOW, just gets result
     
     API (Programming):
     - Your code calls API: 'I need weather data!'
     - API server processes using THEIR method
     - You don't know HOW, just get JSON result
     
     Structural mapping:
     - Request/Response ↔ Order/Delivery
     - Abstraction ↔ Not knowing kitchen internals
     - Contract ↔ Menu (what's available)"
```

**Result:** Deep understanding через relational mapping!

---

## 🔧 OPTIMIZATION TIPS

### Tip 1: Pre-Load User Context

**At session start, quickly load:**
```bash
# Check if profile exists
cat .ai_coach/user_profile.json

# Check current weak skills
SELECT skill_name, mastery_prob 
FROM skill_mastery 
WHERE mastery_prob < 0.6 
ORDER BY mastery_prob ASC;
```

**Use this to:**
- Suggest what to review today
- Avoid teaching mastered topics
- Focus on weak areas

### Tip 2: Batch ROI Checks

**Instead of checking each skill individually:**
```bash
python Scripts/skill_roi_calculator.py list | head -20

# Pre-load top 20 skills in memory
# Reference during conversation
```

### Tip 3: Cache Analogies

**After generating good analogy:**
```python
# Manually save to cache
python Scripts/teaching_helper.py save_analogy \
  --concept function \
  --domain chef \
  --text "..." \
  --quality 5
```

**Next time teaching "function" to chef-background user:**
- System auto-retrieves cached analogy
- You can reuse or improve it

### Tip 4: Monitor Mastery Trends

**Every 5-10 lessons:**
```sql
SELECT 
  skill_name,
  mastery_prob,
  attempts,
  ROUND(correct*100.0/attempts, 1) as success_rate
FROM skill_mastery
WHERE attempts > 3
ORDER BY mastery_prob ASC;
```

**This shows:**
- Which skills need more practice
- Success rate trends
- Where user is stuck

---

## ⚠️ COMMON PITFALLS (Avoid!)

### ❌ Pitfall 1: Teaching Without Assessment

**Wrong:**
```
User: "Teach me decorators"
You: [Immediately teaches decorators]
```

**Right:**
```bash
python Scripts/knowledge_tracer.py recommend --skill decorators
# Check output FIRST, then decide what to teach
```

### ❌ Pitfall 2: Ignoring ROI

**Wrong:**
```
User: "I want to learn assembly language"
You: "Sure, let's start..."
```

**Right:**
```bash
python Scripts/skill_roi_calculator.py compare --skills assembly,python,javascript

You: "Assembly has very low ROI (high learning cost, niche demand).
     Unless you're doing embedded systems, consider Python first.
     Your goals are [check profile], which aligns better with..."
```

### ❌ Pitfall 3: Generic Analogies

**Wrong:**
```
You: "Recursion is like looking in a mirror between two mirrors..."
# (Generic analogy, not using user background)
```

**Right:**
```bash
python Scripts/analogy_generator.py generate --concept recursion --llm
# Uses user profile → personalized to their domain
```

### ❌ Pitfall 4: Not Updating Mastery

**Wrong:**
```
User: [Solves recursion problem correctly]
You: "Great job!"
[Session ends, no update]
```

**Right:**
```bash
python Scripts/knowledge_tracer.py update --skill recursion --correct
You: "Great job! Your recursion mastery → 75% now."
```

---

## 📈 SUCCESS METRICS (Track These)

**For each teaching session:**

1. **BKT Accuracy:** Did mastery predictions match user performance?
2. **Backtrack Rate:** How often did you need to teach prerequisites?
3. **Analogy Quality:** User rating of analogies (1-5)
4. **ROI Alignment:** Did user choose high-ROI path?
5. **Completion Rate:** % of started topics completed

**Query for insights:**
```sql
-- Weekly progress
SELECT 
  DATE(last_practiced) as week,
  COUNT(DISTINCT skill_name) as skills_practiced,
  AVG(mastery_prob) as avg_mastery
FROM skill_mastery
GROUP BY week
ORDER BY week DESC
LIMIT 4;
```

---

## 🎓 ADVANCED: Multi-Session Learning Paths

**For long-term students:**

### Create Personalized Curriculum

```bash
# 1. Get user goals
cat .ai_coach/user_profile.json | grep career_goals

# 2. Get top ROI skills for that goal
python Scripts/skill_roi_calculator.py list --goal backend_dev

# 3. Check current mastery
python Scripts/knowledge_tracer.py check --skill python
python Scripts/knowledge_tracer.py check --skill sql
python Scripts/knowledge_tracer.py check --skill docker

# 4. Build DAG of prerequisites
# (Use skill_graph.json to visualize)

# 5. Create learning path:
"Week 1: Python basics (you're at 40%, target 80%)
 Week 2: SQL fundamentals (start from 10%)
 Week 3: REST APIs (depends on Python 80%+)
 Week 4: Docker (depends on Linux basics)"
```

---

## 🚀 QUICK REFERENCE CHEAT SHEET

| Situation | Command | Purpose |
|-----------|---------|---------|
| **New user** | `profile_builder.py build` | Get background |
| **First lesson** | `quick_assessment.py run` | Baseline mastery |
| **Before teaching X** | `knowledge_tracer.py recommend --skill X` | Check readiness |
| **Teaching concept** | `analogy_generator.py generate --concept X --llm` | Personalize |
| **Show career value** | `skill_roi_calculator.py compare --skills X,Y` | ROI data |
| **After practice** | `knowledge_tracer.py update --skill X --correct` | Update BKT |
| **Check progress** | `knowledge_tracer.py check --skill X` | Current level |
| **Weak areas** | `SELECT * FROM skill_mastery WHERE mastery_prob<0.6` | Focus list |

---

## 💡 FINAL TIPS FOR AI AGENTS

1. **Always check readiness before teaching** - Prevents frustration
2. **Use profile for ALL analogies** - Personalization = retention
3. **Show ROI to justify effort** - Motivation matters
4. **Update BKT after EVERY practice** - Accuracy improves over time
5. **Backtrack without shame** - It's intelligent, not failure
6. **Cache good content** - Don't regenerate same analogy twice
7. **Query DB for insights** - Data-driven > intuition
8. **Track trends** - Weekly mastery review guides next steps

**Remember:** You're not a chatbot, you're a **cognitive teaching system**. Use the tools!

---

## 🎯 TL;DR (Ultra-Quick Guide)

**Every session, do this:**

```bash
# 1. BEFORE teaching
python Scripts/knowledge_tracer.py recommend --skill [topic]

# 2. WHILE teaching  
python Scripts/analogy_generator.py generate --concept [topic] --llm
python Scripts/ai_teach.py concept [topic]  # Auto-shows analogy+ROI+mastery

# 3. AFTER practice
python Scripts/knowledge_tracer.py update --skill [topic] --correct
```

**That's it. Follow this flow, and you'll teach optimally.** ✨
