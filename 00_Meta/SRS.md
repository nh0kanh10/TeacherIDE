# Software Requirements Specification (SRS)
# IDE-Native Multi-Subject Learning System with AI Coach

**Version:** 3.0 (Cognitive Teaching System)
**Date:** 2025-12-26  
**Author:** AI Agent (Antigravity)  
**Status:** Production  

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for an **IDE-Native Multi-Subject Learning System** that transforms a traditional chat-based AI learning assistant into an intelligent teaching environment integrated directly into the developer's IDE workflow.

### 1.2 Scope
The system provides:
- **Multi-subject learning** (Programming, Languages, Soft Skills)
- **IDE-native teaching** (zero context switching)
- **Error-driven learning** (auto-capture terminal errors)
- **Code-level knowledge persistence** (lessons linked to files/lines)
- **Sidecar lesson files** (v2.1: safe alternative to inline injection)
- **File lifecycle tracking** (monitor learning history per file)
- **Privacy controls** (opt-in for remote analysis)

### 1.3 Intended Audience
- **Primary:** Self-learners using IDEs (VSCode, Cursor, Windsurf, etc.)
- **Secondary:** Students, bootcamp attendees, career changers
- **Tertiary:** Educators using AI-assisted teaching

### 1.4 Definitions

| Term | Definition |
|------|------------|
| **IDE-Native** | Features integrated into IDE workflow without context switching |
| **Error-Driven Learning** | Automatic lesson creation from code errors |
| **Code-Level Memory** | Lessons linked to specific files, lines, symbols |
| **Inline Teaching** | AI-generated comments injected directly into code |
| **Spatial Memory** | AI remembers which file/line had which error/lesson |

---

## 2. System Overview

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User (IDE)                          │
└────────────┬────────────────────────────────────┬──────────┘
             │                                    │
    ┌────────▼─────────┐                ┌────────▼─────────┐
    │ Terminal Errors  │                │  IDE Commands    │
    │ (error_listener) │                │  (ai_teach.py)   │
    └────────┬─────────┘                └────────┬─────────┘
             │                                    │
    ┌────────▼────────────────────────────────────▼─────────┐
    │            AI Agent (Teaching Logic)                  │
    │  - Error parsing      - Concept teaching             │
    │  - Lesson generation  - File insights                │
    └────────┬──────────────────────────────────┬──────────┘
             │                                  │
    ┌────────▼─────────┐           ┌───────────▼──────────┐
    │ Inline Teaching  │           │  Knowledge Vault     │
    │ (comment_inject) │           │  (Obsidian/SQLite)   │
    └────────┬─────────┘           └───────────┬──────────┘
             │                                  │
    ┌────────▼──────────────────────────────────▼─────────┐
    │         Persistence Layer (teaching_helper.py)       │
    │  - SQLite (code-level memory)                       │
    │  - Markdown vault (05_Extracted_Knowledge/)         │
    │  - File tracking (file_history table)               │
    └─────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.11+ |
| **Database** | SQLite 3 (WAL mode) |
| **Knowledge Vault** | Markdown (Obsidian-compatible) |
| **Dashboard** | Streamlit |
| **AI Integration** | AI Agent API (extensible) |
| **Version Control** | Git (with pre-commit hooks) |

### 2.3 Deployment Model
- **Local-first:** All data stored locally
- **Privacy-focused:** Opt-in for remote API calls
- **IDE-agnostic:** CLI tools work with any IDE

---

## 3. Functional Requirements

### 3.1 Error-Driven Teaching

**FR-01: Automatic Error Capture**
- **Description:** System shall capture terminal errors automatically via pipe or file input
- **Input:** Terminal output containing error messages
- **Processing:** 
  - Parse error type, file path, line number, message
  - Support Python, C#, JavaScript errors (extensible to other languages)
- **Output:** Structured error record in `errors_log` table
- **Priority:** HIGH

**FR-02: Error-to-Lesson Conversion**
- **Description:** System shall convert captured errors into knowledge entries
- **Input:** Parsed error information
- **Processing:**
  - Create markdown file in `05_Extracted_Knowledge/`
  - Format: `error_[filename]_L[line]_[timestamp].md`
  - Include: error type, message, file context, AI explanation
- **Output:** Knowledge entry with file/line linkage
- **Priority:** HIGH

**FR-03: Multi-Language Error Support**
- **Description:** System shall parse errors from multiple programming languages
- **Supported:** Python, C#, JavaScript, TypeScript (initial set)
- **Extensible:** Regex patterns easily added for new languages
- **Priority:** MEDIUM

### 3.2 Code-Level Memory

**FR-04: File/Line/Symbol Tracking**
- **Description:** Knowledge entries shall be linked to specific code locations
- **Data Model:**
  - `file_path`: Absolute path to source file
  - `line_number`: Specific line (integer)
  - `symbol_name`: Function/class name (optional)
  - `error_type`: Error category (if applicable)
- **Query:** Enable spatial queries like "Show lessons from BookingService.cs:67"
- **Priority:** HIGH

**FR-05: File History Tracking**
- **Description:** System shall maintain usage history per file
- **Tracked Metrics:**
  - `opened_count`: Number of times file opened
  - `error_count`: Number of errors in this file
  - `last_opened`: Timestamp
  - `lessons`: JSON array of linked lesson IDs
- **Use Case:** Identify problematic files needing review
- **Priority:** MEDIUM

**FR-06: Spatial Memory Queries**
- **Description:** System shall support querying lessons by code location
- **Examples:**
  - "Show all lessons from file X"
  - "What errors occurred in this function?"
  - "Files with most errors"
- **Priority:** MEDIUM

### 3.3 Sidecar Lesson Files (Inline Teaching Alternative)

**FR-07: Sidecar Lesson Creation**
- **Description:** System shall create `.lessons.md` sidecar files next to code files
- **Input:** File path, line number, lesson text, optional code context
- **Processing:**
  - Create sidecar: `file.py` → `file.py.lessons.md`
  - Format lesson with line number, timestamp, context
  - Preserve spatial relationship (sidecar next to code)
- **Output:** Markdown sidecar file with lessons
- **Priority:** HIGH
- **Rationale:** Safer than inline injection - no syntax risk, no linter conflicts

**FR-08: Sidecar Safety & Benefits**
- **Description:** Sidecar approach provides safety without code modification
- **Benefits:**
  - **No syntax risk** - Never touches source code
  - **No linter conflicts** - Lessons in separate file
  - **Git-friendly** - Can gitignore `.lessons.md` files
  - **Spatial memory** - Sidecar next to code preserves location context
  - **IDE extensible** - Future extensions can show hover tooltips
- **Priority:** HIGH

**FR-09: Sidecar Metadata Tracking**
- **Description:** System shall track sidecar lessons in database
- **Mechanism:**
  - Save metadata to `knowledge_extracts` table
  - Link to file path and line number
  - `sidecar_type` column distinguishes from vault lessons
- **Query Support:** Find lessons by file, line, or topic
- **Priority:** HIGH

**FR-10: Multi-Format Sidecar Support**
- **Description:** Sidecar format adapts to code file type
- **Supported:** Any code file (.py, .cs, .js, .ts, .java, .cpp, etc.)
- **Format:** Line-based entries with timestamps and context
- **Extensible:** Same format for all languages (markdown)
- **Priority:** MEDIUM

### 3.4 File Lifecycle Tracking

**FR-11: File Event Tracking**
- **Description:** System shall track file lifecycle events
- **Events:** open, edit, error, close
- **Storage:** `file_history` table with UPSERT logic
- **Priority:** MEDIUM

**FR-12: File Insights**
- **Description:** System shall provide file-specific insights
- **Insights:**
  - Total opens/errors
  - Linked lessons
  - Error history (last 10 errors)
  - Resolved vs. unresolved errors
- **Priority:** MEDIUM

**FR-13: Problematic Files Detection**
- **Description:** System shall identify files needing attention
- **Criteria:** Ranked by `error_count` or `error_ratio` (errors/opens)
- **Output:** Top N problematic files
- **Priority:** LOW

### 3.5 IDE Commands

**FR-14: /teach error**
- **Description:** Explain last unresolved error
- **Behavior:**
  - Query `errors_log` for latest error where `resolved=0`
  - Display error details and linked lesson (if exists)
  - Show lesson content from knowledge vault
- **Priority:** HIGH

**FR-15: /teach concept**
- **Description:** Teach a concept on-demand
- **Input:** Concept name (e.g., "LINQ", "Pomodoro Technique")
- **Behavior:**
  - AI generates explanation
  - Save to knowledge vault with appropriate topic tag
- **Priority:** HIGH

**FR-16: /teach insights**
- **Description:** Show file learning history
- **Input:** File path
- **Output:** Opens, errors, lessons, error history
- **Priority:** MEDIUM

**FR-17: Command-Line Interface**
- **Description:** All commands accessible via CLI
- **Format:** `python Scripts/ai_teach.py <command> [args]`
- **Examples:**
  - `ai_teach.py error`
  - `ai_teach.py concept "topic"`
  - `ai_teach.py insights file.py`
- **Priority:** HIGH

### 3.6 Knowledge Persistence

**FR-18: Multi-Subject Topic Tagging**
- **Description:** Knowledge entries shall be tagged by subject/topic
- **Topics:**
  - Programming: `CSharp`, `Python`, `JavaScript`, `WebDev`
  - Languages: `English`, `Japanese`
  - Soft Skills: `Productivity`, `TimeManagement`, `Career`
- **Extensible:** User can create any topic tag
- **Priority:** HIGH

**FR-19: Obsidian-Compatible Vault**
- **Description:** Knowledge saved as markdown files in Obsidian format
- **Location:** `05_Extracted_Knowledge/`
- **Format:** 
  - Filename: `YYYYMMDD_HHMMSS_[Title].md`
  - Error lessons: `error_[file]_L[line]_[timestamp].md`
- **Benefits:** Searchable, linkable, portable
- **Priority:** HIGH

**FR-20: Dual Storage (SQLite + Markdown)**
- **Description:** Knowledge metadata in SQLite, content in markdown
- **SQLite:** `knowledge_extracts` table
- **Markdown:** Full content with formatting
- **Sync:** Both updated atomically
- **Priority:** HIGH

### 3.7 Database Schema

**FR-21: Idempotent Migrations**
- **Description:** Schema migrations shall be safe to run multiple times
- **Mechanism:**
  - `schema_version` table tracks applied migrations (v1, v2, etc.)
  - `CREATE TABLE IF NOT EXISTS`
  - Column existence checks before `ALTER TABLE`
  - JSON-to-junction migration for v2
- **Priority:** HIGH

**FR-22: WAL Mode & Foreign Keys**
- **Description:** SQLite shall use Write-Ahead Logging and enforce FKs
- **Commands:** 
  - `PRAGMA journal_mode=WAL`
  - `PRAGMA foreign_keys=ON`
- **Benefit:** Better concurrent read/write performance + data integrity
- **Priority:** HIGH

**FR-23: Core Tables (v2 Schema)**
- **Description:** Database shall include these tables:
  - `knowledge_extracts` - Lessons with file/line/symbol/sidecar_type fields
  - `file_history` - Per-file usage stats (UNIQUE on `file_path`)
  - `file_lessons_map` - **NEW:** Junction table for file-lesson relationships
  - `errors_log` - Error tracking with resolution status + file_id FK
  - `schema_version` - Migration tracking (current: v2)
- **Indexes:** All FKs and frequently queried columns indexed
- **Priority:** HIGH

**FR-23a: Markdown-First Sync (Vault Watcher)**
- **Description:** System shall sync Markdown (master) to SQLite (index)
- **Mechanism:**
  - Watch `05_Extracted_Knowledge/` for file changes
  - On create/modify: Parse markdown → update SQLite
  - On delete: Remove DB entry
  - On move: Update path
- **Rationale:** Prevents orphaned records when user edits Obsidian manually
- **Tool:** `vault_watcher.py` using watchdog library
- **Priority:** MEDIUM

### 3.8 Privacy & Security

**FR-24: Opt-In Privacy Controls**
- **Description:** User shall control data sharing via `config.json`
- **Settings:**
  - `send_code_to_api`: false (default - don't send code to remote)
  - `send_error_messages`: true (default - error messages only)
  - `allow_remote_analysis`: true (user choice)
- **Priority:** HIGH

**FR-25: Per-Repo Opt-In**
- **Description:** Privacy settings can be per-repository
- **Mechanism:** Each repo has own `.ai_coach/config.json`
- **Priority:** LOW

**FR-26: Git Integration**
- **Description:** Pre-commit hook shall strip AI comments before commit
- **File:** `Scripts/pre_commit_hook.py`
- **Behavior:**
  - Detect `AI-COACH-START/END` markers
  - Remove comment blocks
  - Re-stage files
  - Respect `strip_on_commit` config setting
- **Priority:** MEDIUM

### 3.9 Dashboard (Review Mode)

**FR-27: Streamlit Dashboard**
- **Description:** Web UI for reviewing knowledge, progress, profile
- **Launch:** `START_LEARNING.bat`
- **Features:**
  - View all knowledge entries
  - Filter by topic/subject
  - View progress charts
  - Manage user profile
- **Priority:** MEDIUM

**FR-28: Read-Only Dashboard**
- **Description:** Dashboard is for review only, not teaching
- **Rationale:** Active learning happens in IDE, dashboard for retrospective
- **Priority:** LOW

### 3.10 Multi-Subject Support

**FR-29: Subject-Agnostic Architecture**
- **Description:** System shall support any subject via topic tags
- **No Hard-Coding:** No subject-specific logic
- **Extensibility:** User adds folders and topics as needed
- **Priority:** HIGH

**FR-30: Folder Organization**
- **Description:** Subject folders provide optional structure
- **Structure:**
  ```
  01_Programming/
  02_Languages/
  03_Soft_Skills/
  04_Projects/
  ```
- **Flexibility:** User can create any structure
- **Priority:** LOW

### 3.11 Cognitive Teaching System (v3.0) ✨ NEW

**FR-31: User Profile & Background Context**
- **Description:** System shall captu re user background and career goals for personalization
- **Components:**
  - Interactive questionnaire (`profile_builder.py`)
  - Background domains (chef, musician, teacher, etc.)
  - Career goals (backend_dev, high_salary, remote_work, etc.)
  - Learning style preferences (visual, hands-on, theoretical)
- **Storage:** `.ai_coach/user_profile.json`
- **Impact:** Enables personalized analogies and career-driven recommendations
- **Priority:** HIGH

**FR-32: Skill ROI Calculator**
- **Description:** System shall calculate return-on-investment for programming skills
- **Formula:** `ROI = (Market_Salary × Demand_Trend) / Learning_Cost`
- **Data Sources:**
  - Stack Overflow Developer Survey (salary data)
  - O*NET Database (job growth trends)
  - Internal complexity ratings
- **Learning Cost:** `Complexity × (1 - Current_Mastery_Probability)`
- **Output:** ROI rankings with salary, trend, learning time estimates
- **Tools:** `skill_roi_calculator.py`, `market_intelligence.py`
- **Priority:** HIGH

**FR-33: Bayesian Knowledge Tracing (BKT)**
- **Description:** System shall track skill mastery using pyBKT algorithm
- **Mechanism:**
  - Track mastery probability per skill (0.0 to 1.0)
  - Update on each practice attempt (correct/incorrect)
  - Account for guessing and slip rates
- **Database:** `skill_mastery` table with attempts, correct, mastery_prob
- **Tool:** `knowledge_tracer.py`
- **Priority:** HIGH

**FR-34: Skill Dependency Graph**
- **Description:** System shall maintain prerequisite relationships between skills
- **Implementation:**
  - JSON skill graph (`skill_graph.json`)
  - 115+ skills mapped (Python: 58, JavaScript: 30+, C#: 25+)
  - Auto-populate `skill_dependencies` table on init
- **Query:** Get prerequisites for any skill
- **Priority:** HIGH

**FR-35: Recursive Teaching Algorithm**
- **Description:** System shall automatically backtrack to weak prerequisites
- **Logic:**
  1. User struggles with skill X
  2. Check prerequisites of X
  3. If weak prereq found → teach prereq first
  4. Recursively check prereq's prereqs
  5. Find solid foundation level
- **Example:** Fails recursion → Check functions (60%) → Teach functions first
- **Tool:** `knowledge_tracer.py recommend` command
- **Priority:** HIGH

**FR-36: Quick Assessment (BKT Cold Start)**
- **Description:** System shall establish baseline skill mastery via assessment
- **Problem Solved:** BKT "cold start" (doesn't know user level initially)
- **Mechanism:**
  - Quick quiz (2-3 minutes)
  - 5-10 questions per skill domain
  - Creates initial mastery probabilities
- **Tool:** `quick_assessment.py`
- **Priority:** HIGH

**FR-37: Analogy Generator (SMT-based)**
- **Description:** System shall create personalized analogies using Structure Mapping Theory
- **Approach:**
  1. Get user background from profile (e.g., "Chef")
  2. Query ConceptNet for target concept keywords
  3. Generate SMT prompt for AI Agent
  4. Create relational mapping (not surface similarity)
  5. Cache with quality scores
- **Example:** Function → Recipe (Chef background)
- **Tools:** `analogy_generator.py`, `ai_agent_integration.py`
- **Database:** `analogies` table with quality_score
- **Priority:** HIGH

**FR-38: AI Agent Integration Workflow**
- **Description:** System shall use AI Agent (in IDE) for content generation
- **Benefits:**
  - No external API costs
  - Context-aware (reads user code)
  - Privacy-first (local)
- **Workflow:**
  1. Generate SMT prompt
  2. User pastes to AI Agent
  3. AI Agent generates analogy
  4. User pastes back
  5. System caches result
- **Future:** Automate via VS Code Extension API
- **Priority:** MEDIUM

**FR-39: Market Intelligence APIs**
- **Description:** System shall fetch real market data for skills
- **APIs:**
  - Stack Overflow Tags API (popularity proxy)
  - O*NET Occupation API (job growth)
- **Caching:** 90-day cache to reduce API calls
- **Fallback:** Hardcoded estimates if APIs unavailable
- **Tool:** `market_intelligence.py`
- **Priority:** MEDIUM

**FR-40: Enhanced teaching_helper (v3.0)**
- **Description:** Persistence layer shall integrate v3.0 features
- **Enhancements:**
  - `save_knowledge_block()` updates skill mastery if practice
  - Logs ROI for newly encountered skills
  - Profile-aware storage paths (by topic)
  - `save_analogy()` function for cache
- **Parameters:** `skill_name`, `is_practice`, `practice_correct`
- **Priority:** HIGH



## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-01: Fast Error Capture**
- **Requirement:** Error parsing shall complete in < 100ms
- **Rationale:** Should not slow down development workflow
- **Priority:** MEDIUM

**NFR-02: Efficient Queries**
- **Requirement:** Database queries return in < 500ms
- **Indexes:** All foreign keys and frequently queried columns indexed
- **Priority:** MEDIUM

**NFR-03: Small Footprint**
- **Requirement:** Database size < 100MB for 10,000 lessons
- **Mechanism:** Store content in markdown, only metadata in SQLite
- **Priority:** LOW

### 4.2 Reliability

**NFR-04: Data Integrity**
- **Requirement:** No data loss during injection/undo
- **Mechanism:** Backups before every file modification
- **Priority:** HIGH

**NFR-05: Crash Recovery**
- **Requirement:** System recovers gracefully from interrupted operations
- **Mechanism:** WAL mode, atomic operations, transaction rollback
- **Priority:** MEDIUM

**NFR-06: Migration Safety**
- **Requirement:** Migrations never corrupt existing data
- **Mechanism:** Idempotent SQL, version check, transaction wrapping
- **Priority:** HIGH

### 4.3 Usability

**NFR-07: Zero Setup for Basic Use**
- **Requirement:** Error capture works without configuration
- **Mechanism:** Sane defaults, auto-create directories
- **Priority:** HIGH

**NFR-08: Clear Error Messages**
- **Requirement:** CLI tools provide helpful error messages
- **Examples:** "File not found: X", "Migration already applied"
- **Priority:** MEDIUM

**NFR-09: Fast Onboarding**
- **Requirement:** User productive in < 5 minutes
- **Documentation:** README with quick start
- **Priority:** MEDIUM

### 4.4 Maintainability

**NFR-10: Modular Architecture**
- **Requirement:** Each script has single responsibility
- **Modules:** error_listener, lesson_sidecar, file_tracker, vault_watcher, teaching_helper
- **Priority:** HIGH

**NFR-11: Extensible Parsers**
- **Requirement:** Easy to add new language error parsers
- **Mechanism:** Dictionary of regex patterns
- **Priority:** MEDIUM

**NFR-12: Clear Code Comments**
- **Requirement:** All public functions documented
- **Format:** Docstrings with args, returns, examples
- **Priority:** MEDIUM

### 4.5 Portability

**NFR-13: Cross-Platform**
- **Requirement:** Works on Windows, macOS, Linux
- **Mechanism:** Python pathlib, platform-agnostic code
- **Priority:** HIGH

**NFR-14: IDE-Agnostic**
- **Requirement:** CLI tools work with any IDE
- **No Dependencies:** No VSCode-specific APIs
- **Future:** VSCode extension optional add-on
- **Priority:** HIGH

### 4.6 Security

**NFR-15: Local-First**
- **Requirement:** All data stored locally by default
- **No Cloud:** No mandatory cloud sync
- **Priority:** HIGH

**NFR-16: Secure Backups**
- **Requirement:** Backups stored with restrictive permissions
- **Location:** `.ai_coach/backups/` (user-only read/write)
- **Priority:** MEDIUM

---

## 5. Use Cases

### 5.1 Primary Use Cases

**UC-01: Learning from Error**
1. User writes code with bug
2. Runs script → error occurs
3. Error piped to `error_listener.py`
4. System parses error, saves to `errors_log`
5. System creates knowledge entry with file/line context
6. User runs `/teach error` to review explanation
7. (Optional) User creates sidecar lesson via `lesson_sidecar.py`

**UC-02: On-Demand Concept Learning**
1. User wants to learn concept (e.g., "LINQ")
2. Runs `ai_teach.py concept "LINQ"`
3. AI generates explanation
4. System saves to knowledge vault with topic tag
5. User reviews via dashboard or markdown file

**UC-03: File-Specific Review**
1. User opens file with past errors
2. Runs `ai_teach.py insights BookingService.cs`
3. System shows: 12 opens, 4 errors, 2 lessons
4. User reviews linked lessons to avoid past mistakes

**UC-04: Sidecar Learning Hints**
1. User encounters error
2. AI explains error via `/teach error`
3. User decides to create sidecar lesson
4. Runs `lesson_sidecar.py create --file file.py --line 45 --lesson "..."`
5. Sidecar file `file.py.lessons.md` created
6. Lesson appears next to code (spatial memory preserved)
7. No code modification, no syntax risk

**UC-05: Clean Commits (Sidecar Approach)**
1. User has `.lessons.md` sidecar files
2. Commits to git
3. Sidecar files can be gitignored (optional)
4. Source code files committed clean (never modified by AI)
5. No pre-commit hook needed

### 5.2 Secondary Use Cases

**UC-06: Multi-Subject Learning**
1. User learns C# in morning
2. Studies Japanese vocabulary in afternoon
3. Reviews productivity technique in evening
4. All knowledge saved to same vault with different topics
5. Dashboard shows progress across all subjects

**UC-07: Problematic Files Detection**
1. User runs `file_tracker.py problems`
2. System ranks files by error count
3. User identifies `PaymentService.cs` has 8 errors
4. Reviews that file's lessons to improve code quality

**UC-08: File-Based Lesson Management**
1. User wants to review all lessons for a file
2. Runs `lesson_sidecar.py show --file BookingService.cs`
3. System displays all lessons with line numbers and timestamps
4. User can manually edit `.lessons.md` file if needed (markdown format)
5. Vault watcher syncs changes to database

---

## 6. Data Model

### 6.1 SQLite Schema (v2)

**knowledge_extracts**
```sql
CREATE TABLE knowledge_extracts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    topic TEXT,
    obsidian_path TEXT,
    file_path TEXT,           -- Code location
    line_number INTEGER,
    symbol_name TEXT,
    error_type TEXT,
    sidecar_type TEXT DEFAULT 'vault',  -- NEW v2: 'vault' or 'sidecar'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_knowledge_file_path ON knowledge_extracts(file_path);
CREATE INDEX idx_knowledge_topic ON knowledge_extracts(topic);
```

**file_history**
```sql
CREATE TABLE file_history (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    opened_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    last_opened TIMESTAMP,
    lessons TEXT              -- DEPRECATED v2: use file_lessons_map
);
CREATE INDEX idx_file_history_path ON file_history(file_path);
```

**file_lessons_map (NEW v2 - Junction Table)**
```sql
CREATE TABLE file_lessons_map (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES file_history(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES knowledge_extracts(id) ON DELETE CASCADE,
    UNIQUE(file_id, lesson_id)
);
CREATE INDEX idx_file_lessons_file ON file_lessons_map(file_id);
CREATE INDEX idx_file_lessons_lesson ON file_lessons_map(lesson_id);
```

**errors_log**
```sql
CREATE TABLE errors_log (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT,
    line_number INTEGER,
    error_type TEXT,
    error_message TEXT,
    lesson_created INTEGER,   -- FK to knowledge_extracts
    resolved INTEGER DEFAULT 0,
    file_id INTEGER,          -- NEW v2: FK to file_history
    FOREIGN KEY (file_id) REFERENCES file_history(id)
);
CREATE INDEX idx_errors_log_file ON errors_log(file_path);
```

**injections**
```sql
CREATE TABLE injections (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    marker TEXT,
    start_line INTEGER,
    end_line INTEGER,
    backup_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_injections_file ON injections(file_path);
```

**schema_version**
```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6.2 Markdown Format

**Knowledge Entry Example:**
```markdown
# Error: NameError

**File:** test_error.py:6
**Type:** NameError
**Language:** python

## Error Message
```
name 'naam' is not defined
```

## Explanation
Variable name mismatch. Used 'naam' instead of 'name' in function parameter.

## How to Fix
1. Check variable names match between definition and usage
2. Use IDE autocomplete to avoid typos

## Pattern to Remember
Always validate variable names before running.

---
*Auto-generated: 2025-12-26 15:41:48*
```

### 6.3 Config Format

**config.json**
```json
{
  "version": "1.0.0",
  "privacy": {
    "send_code_to_api": false,
    "send_error_messages": true,
    "allow_remote_analysis": true
  },
  "injection": {
    "auto_inject": false,
    "require_confirmation": true,
    "strip_on_commit": true
  },
  "file_tracking": {
    "enabled": true,
    "ignore_patterns": ["*.pyc", "__pycache__", ".git", "node_modules"]
  }
}
```

---

## 7. User Interface Requirements

### 7.1 CLI Interface

**Primary Interface:** Command-line tools

**Commands:**
```bash
# Error teaching
python Scripts/ai_teach.py error
python Scripts/ai_teach.py concept "topic"
python Scripts/ai_teach.py insights file.py

# Sidecar lessons (v2 - replaces comment injection)
python Scripts/lesson_sidecar.py create --file file.py --line 45 --lesson "lesson"
python Scripts/lesson_sidecar.py show --file file.py
python Scripts/lesson_sidecar.py list --dir .

# File tracking
python Scripts/file_tracker.py track --file file.py --event open
python Scripts/file_tracker.py insights --file file.py
python Scripts/file_tracker.py problems --limit 10

# Vault watcher (v2 - Markdown-first sync)
python Scripts/vault_watcher.py sync   # One-time sync
python Scripts/vault_watcher.py watch  # Continuous monitoring

# Migrations
python Scripts/run_migration.py      # v1
python Scripts/run_migration_v2.py   # v2
```

**Output Format:**
- Emoji icons for visual clarity (✅, ❌, ⚠️, 📝, etc.)
- Structured output (headers, bullets, tables)
- Color coding (if terminal supports)

### 7.2 Dashboard Interface (Streamlit)

**Launch:** `START_LEARNING.bat`

**Pages:**
1. **Knowledge Vault** - Browse all lessons, filter by topic
2. **Progress** - Charts by subject/topic
3. **Profile** - User learning profile and preferences
4. **Settings** - Config management

**Design:**
- Sidebar navigation
- Search/filter controls
- Responsive layout
- Read-only (no editing)

### 7.3 Workflow Integration

**AI Agent Workflows:**
- `/teaching_mode` - Teaching principles
- `/resume_learning` - Resume workspace
- `/teach` - Command documentation

**Location:** `.agent/workflows/*.md`

---

## 8. Integration Points

### 8.1 AI Agent Integration

**Current:** AI Agent calls scripts after teaching

**Commands:**
- `teaching_helper.py save_knowledge`
- `teaching_helper.py update_profile`
- `teaching_helper.py log_interaction`
- `teaching_helper.py update_progress`

**Future:** Direct API integration for real-time explanations

### 8.2 IDE Integration

**Current:** CLI tools (IDE-agnostic)

**Future (Optional):**
- VSCode extension
  - Command palette: `/teach error`, `/teach concept`
  - Codelens: show lessons for current file
  - On-save error capture
- Other IDE plugins (JetBrains, Vim, etc.)

### 8.3 Git Integration

**Pre-Commit Hook:**
- Install: Copy `Scripts/pre_commit_hook.py` to `.git/hooks/pre-commit`
- Behavior: Strip AI comments before commit
- Config: Respect `strip_on_commit` setting

### 8.4 Terminal Integration

**Error Piping:**
```bash
python script.py 2>&1 | python Scripts/error_listener.py
pytest 2>&1 | python Scripts/error_listener.py
npm test 2>&1 | python Scripts/error_listener.py
```

**File-Based:**
```bash
python script.py 2> error.log
python Scripts/error_listener.py --file error.log
```

---

## 9. Constraints & Assumptions

### 9.1 Technical Constraints
- Python 3.11+ required
- SQLite 3.8+ (for WAL mode)
- File system access required
- Terminal/shell access for error piping

### 9.2 Assumptions
- User has basic CLI knowledge
- IDE supports terminal integration
- User wants local-first solution
- Multi-subject learning is desired

### 9.3 Out of Scope (V1)
- Cloud sync
- Mobile app
- Real-time collaboration
- AST-based code analysis (future enhancement)
- Spaced repetition scheduler (future enhancement)

---

## 10. Success Criteria

### 10.1 Functional Success
- ✅ Error capture working for 3 languages (Python, C#, JS)
- ✅ Comment injection with backup/undo working
- ✅ File tracking with insights working
- ✅ IDE commands (`/teach error`, etc.) working
- ✅ Migration idempotency verified
- ✅ Multi-subject topic tagging working

### 10.2 Non-Functional Success
- ✅ Zero data loss in 100 injection/undo cycles
- ✅ Error parsing < 100ms
- ✅ Database queries < 500ms
- ✅ User productive in < 5 minutes
- ✅ Cross-platform compatibility (Windows, macOS, Linux)

### 10.3 User Experience Success
- ✅ User reports "feels like natural part of workflow"
- ✅ Zero context switching required
- ✅ File-specific insights useful for debugging
- ✅ Inline comments helpful for learning

---

## 11. Risks & Mitigations

### 11.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Comment injection breaks syntax | HIGH | AST-based parsing (future), thorough testing |
| Database corruption | HIGH | WAL mode, backups, migration tests |
| Error regex false positives | MEDIUM | Comprehensive test suite, user feedback |
| Performance degradation | LOW | Indexes, query optimization |

### 11.2 User Experience Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Too many AI comments clutter code | MEDIUM | Require confirmation, easy undo |
| Confusing CLI | MEDIUM | Clear help text, good defaults |
| Overwhelming for beginners | MEDIUM | Simple quick start, progressive disclosure |

### 11.3 Privacy Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Unintended code upload to API | HIGH | Opt-in controls, local-first default |
| Sensitive data in error messages | MEDIUM | Privacy settings, user education |

---

## 12. Future Enhancements

### 12.1 Short-Term (Next 3 Months)
- AST-based code analysis (safer comment injection)
- More language error parsers (Go, Rust, etc.)
- Better AI explanation prompts
- Dashboard improvements (charts, graphs)

### 12.2 Medium-Term (3-6 Months)
- VSCode extension with native UI
- Spaced repetition scheduler
- Cross-file dependency tracking
- Export to Anki/PDF

### 12.3 Long-Term (6+ Months)
- JetBrains plugin
- Real-time collaboration features
- Cloud sync (optional, opt-in)
- Machine learning for error prediction

---

## 13. Appendix

### 13.1 Glossary

| Term | Definition |
|------|------------|
| **WAL** | Write-Ahead Logging (SQLite optimization) |
| **UPSERT** | Update or Insert (SQL operation) |
| **Obsidian** | Markdown note-taking app with linking |
| **Spatial Memory** | Remembering location context (file/line) |
| **Idempotent** | Operation safe to run multiple times |

### 13.2 References
- SQLite WAL Mode: https://www.sqlite.org/wal.html
- Obsidian Format: https://obsidian.md/
- Python AST: https://docs.python.org/3/library/ast.html

### 13.3 Change History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-25 | Initial SRS (ASP.NET-focused) |
| 2.0 | 2025-12-26 | Multi-subject rewrite, IDE-native features |
| 2.1 | 2025-12-26 | **Technical Refinement:** Sidecar files (replaces inline injection), Vault watcher (Markdown-first), DB schema v2 (junction table, FKs), deprecated comment_injector.py |

---

**END OF DOCUMENT**
