# Quick Reference - IDE-Native Learning Workspace

**Version:** 2.1  
**Last Updated:** 2025-12-26

---

## 📂 Workspace Structure

```
C:\Users\ADMIN\Desktop\Học\
├── 00_Meta/               # Documentation & plans
├── 01_Programming/        # Programming subjects
├── 02_Languages/          # Foreign languages
├── 03_Soft_Skills/        # Productivity, career
├── 04_Projects/           # Learning projects
├── 05_Extracted_Knowledge/# Knowledge vault (Markdown master)
├── Scripts/               # IDE-native tools
├── .ai_coach/             # Database & config
└── START_LEARNING.bat     # Dashboard launcher
```

---

## 🛠️ Core Scripts

| Script | Purpose | Example |
|--------|---------|---------|
| `ai_teach.py` | IDE teaching commands | `python Scripts/ai_teach.py error` |
| `error_listener.py` | Auto-capture errors | `python script.py 2>&1 \| python Scripts/error_listener.py` |
| `lesson_sidecar.py` | Safe lesson files | `python Scripts/lesson_sidecar.py create --file f.py --line 45 --lesson "text"` |
| `file_tracker.py` | File lifecycle | `python Scripts/file_tracker.py insights --file f.py` |
| `vault_watcher.py` | Markdown sync | `python Scripts/vault_watcher.py watch` |
| `teaching_helper.py` | Persistence layer | Called by AI Agent |
| `run_migration_v2.py` | Database schema v2 | `python Scripts/run_migration_v2.py` |
| `app.py` | Streamlit dashboard | `streamlit run Scripts/app.py` |

---

## 🎯 Common Commands

**Error-driven learning:**
```bash
python my_script.py 2>&1 | python Scripts/error_listener.py
python Scripts/ai_teach.py error
```

**Sidecar lessons:**
```bash
python Scripts/lesson_sidecar.py create --file file.py --line 45 --lesson "Always validate input"
python Scripts/lesson_sidecar.py show --file file.py
python Scripts/lesson_sidecar.py list --dir .
```

**File insights:**
```bash
python Scripts/file_tracker.py insights --file BookingService.cs
python Scripts/file_tracker.py problems --limit 10
```

**Vault sync:**
```bash
python Scripts/vault_watcher.py sync    # One-time
python Scripts/vault_watcher.py watch   # Continuous
```

---

## 📊 Database

**Location:** `.ai_coach/progress.db`  
**Schema:** v2 (junction tables, FKs, indexes)  
**Mode:** WAL (concurrent access)

**Key Tables:**
- `knowledge_extracts` - Lessons with file/line/topic
- `file_history` - Per-file stats
- `file_lessons_map` - Junction table (file ↔ lesson)
- `errors_log` - Error tracking
- `schema_version` - Migration tracking

---

## 📝 Documentation

### Essential Docs
- **SRS.md** - Software Requirements (v2.1)
- **PROJECT_STATUS.md** - Current state & features
- **REFINEMENT_PLAN.md** - Active improvements
- **SRS_V2.1_IMPROVEMENTS.md** - v2.1 changes summary

### Workflows (.agent/workflows/)
- **teaching_mode.md** - Teaching principles
- **resume_learning.md** - Resume workspace guide
- **teach.md** - /teach commands
- **update_workspace.md** - Maintenance guide

---

## 🔄 Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.0 | 2025-12-25 | Initial ASP.NET-focused system |
| 2.0 | 2025-12-26 | Multi-subject rewrite |
| 2.1 | 2025-12-26 | Sidecar files, vault watcher, DB v2 |

---

## 🚀 Quick Start

**For AI Agent:**
1. Read `/teaching_mode` workflow
2. Use `teaching_helper.py` to save knowledge
3. User reviews via `START_LEARNING.bat`

**For User:**
1. Run `START_LEARNING.bat` for dashboard
2. Use IDE commands for learning
3. Check `PROJECT_STATUS.md` for features

---

## 🔒 Configuration

**File:** `.ai_coach/config.json`

**Key Settings:**
```json
{
  "privacy": {
    "send_code_to_api": false,
    "allow_remote_analysis": true
  },
  "file_tracking": {
    "enabled": true,
    "ignore_patterns": ["*.pyc", "__pycache__"]
  }
}
```

---

## ⚡ Deprecated (v2.1)

- `comment_injector.py` → Use `lesson_sidecar.py`
- `pre_commit_hook.py` → Not needed (sidecar approach)
- Inline injection → Sidecar files
- `injections` table → No longer used

---

**For full docs, see 00_Meta/ folder**
