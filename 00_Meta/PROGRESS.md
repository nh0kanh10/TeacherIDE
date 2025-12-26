# Learning Progress - Multi-Subject

**Last Updated:** 2025-12-26

## 📊 Overview

Multi-subject learning workspace with IDE-native AI teaching.

## 🎓 Active Subjects

Track progress for each subject you're learning:

### Programming
- **Languages:** [e.g., C#, Python, JavaScript]
- **Current Focus:** [What you're learning now]
- **Progress:** [Your status or %]

### Foreign Languages
- **Languages:** [e.g., English, Japanese]
- **Current Level:** [e.g., JLPT N3, Intermediate]
- **Progress:** [Your status]

### Soft Skills
- **Focus Areas:** [e.g., Productivity, Career Development]
- **Current Goal:** [What you're working on]

---

## 📈 Metrics

View detailed metrics via:
```bash
# Check knowledge vault
ls 05_Extracted_Knowledge/

# Query database
sqlite3 .ai_coach/progress.db "SELECT topic, COUNT(*) FROM knowledge_extracts GROUP BY topic"

# Problematic files (need review)
python Scripts/file_tracker.py problems
```

---

## 🎯 Next Steps

- [ ] [Your next learning goal]
- [ ] [Another goal]

---

**Update this file regularly to track your multi-subject learning journey!**
