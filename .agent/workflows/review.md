---
description: Smart review command - FSRS v5 spaced repetition
---

# /review - Smart Review Command

Quick review with FSRS v5 spaced repetition algorithm.

## Commands

### 1. Interactive Review Session
```bash
python Scripts/review_cli.py session
```
**What it does:**
- Shows all due reviews
- Interactive Q&A for each skill
- Tracks your ratings (1-4)
- Updates FSRS scheduling
- Shows progress stats

### 2. List Due Reviews
```bash
python Scripts/review_cli.py due
```
Shows all skills ready for review with mastery and stability info.

### 3. Review Specific Skill
```bash
python Scripts/review_cli.py skill --skill functions
```
Review one specific skill interactively.

**Quick rate:**
```bash
python Scripts/review_cli.py skill --skill functions --rating 3
```

## Rating Scale

- **1 - Again**: Forgot completely (resets interval shorter)
- **2 - Hard**: Remembered with difficulty (slower growth)
- **3 - Good**: Recalled correctly (optimal growth)
- **4 - Easy**: Trivial (rapid growth)

## Examples

**Daily review routine:**
```bash
# Check what's due
python Scripts/review_cli.py due

# Start session
python Scripts/review_cli.py session
```

**After practice:**
```bash
# Quick mark as reviewed
python Scripts/review_cli.py skill --skill recursion --rating 3
```

## Features

✅ FSRS v5 algorithm (19-parameter DSR model)
✅ Optimal spacing (no "Ease Hell")
✅ Tracks difficulty and stability
✅ Shows next review date
✅ Prevents review backlog
