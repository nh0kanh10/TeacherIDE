---
description: Workflow for maintaining and updating the IDE-native learning workspace
---

# /update_workspace - Maintain & Update Workspace

Use this workflow when making changes to the workspace architecture, adding features, or fixing issues.

## 🎯 When to Use

- Adding new IDE-native features
- Updating database schema
- Refactoring existing tools
- Fixing bugs or improving performance
- Responding to technical feedback

---

## 📋 Pre-Update Checklist

Before making changes:

1. **Read current status**
   ```bash
   cat 00_Meta/PROJECT_STATUS.md
   cat 00_Meta/SRS.md  # Version & change history
   ```

2. **Check task tracking**
   ```bash
   cat 00_Meta/REFINEMENT_PLAN.md  # Active refinements
   ```

3. **Understand scope**
   - [ ] What am I changing? (database / scripts / docs)
   - [ ] Why? (user request / bug / refinement)
   - [ ] Impact? (breaking / non-breaking)

---

## 🔄 Update Workflow

### Step 1: Plan Changes

1. **Create/Update plan document**
   - If major change: Create new plan in `00_Meta/`
   - If minor: Update `REFINEMENT_PLAN.md`

2. **Identify affected files**
   ```bash
   # Check references
   grep -r "feature_name" 00_Meta/
   grep -r "old_function" Scripts/
   ```

3. **Document breaking changes**
   - List in plan document
   - Note migration requirements

### Step 2: Implement Changes

**For Database Changes:**
```bash
# 1. Create new migration SQL
# File: Scripts/migrate_vX.sql

# 2. Create migration runner
# File: Scripts/run_migration_vX.py

# 3. Test migration
python Scripts/run_migration_vX.py

# 4. Verify schema
sqlite3 .ai_coach/progress.db ".schema"
```

**For Script Changes:**
```bash
# 1. Modify/create script in Scripts/

# 2. Test functionality
python Scripts/new_feature.py --help
python Scripts/new_feature.py [test command]

# 3. Update requirements.txt if needed
```

**For Deprecated Features:**
```bash
# 1. Rename old file
mv Scripts/old_tool.py Scripts/old_tool.py.DEPRECATED

# 2. Create deprecation notice
# File: Scripts/old_tool.DEPRECATED.md

# 3. Document replacement in notice
```

### Step 3: Update Documentation (CRITICAL)

**Must update ALL of these:**

1. **SRS.md**
   - Version number (e.g., v2.1 → v2.2)
   - Affected functional requirements (FR-XX)
   - Use cases if changed
   - Change history table (v2.2 entry)

2. **PROJECT_STATUS.md**
   - Teaching Mode section (if tools changed)
   - IDE Commands (if commands changed)
   - Safety Features (if safety impacted)
   - Status checklist

3. **Workflows (.agent/workflows/)**
   - `teaching_mode.md` (if teaching features changed)
   - `resume_learning.md` (if AI Agent guide changed)
   - Any custom workflows affected

4. **README files**
   - Root `README.md` (if major feature)
   - `00_Meta/README.md` (if meta docs changed)
   - Subject folder READMEs (if structure changed)
   - `05_Extracted_Knowledge/README.md` (if vault format changed)

5. **REFINEMENT_PLAN.md**
   - Mark completed tasks as [x]
   - Document what was done

### Step 4: Consistency Check

Run thorough grep searches:

```bash
# Check for old references
grep -r "old_feature_name" 00_Meta/
grep -r "deprecated_tool" .agent/workflows/

# Check for inconsistent terminology
grep -r "inline injection" 00_Meta/  # Should be "sidecar"
grep -r "comment_injector" 00_Meta/  # Should be deprecated

# Verify version consistency
grep -r "Version:" 00_Meta/SRS.md
grep -r "v2\." 00_Meta/
```

### Step 5: Testing

**Smoke Tests:**
```bash
# 1. Database migration
python Scripts/run_migration_vX.py

# 2. Core features
python Scripts/error_listener.py --help
python Scripts/lesson_sidecar.py list
python Scripts/vault_watcher.py sync

# 3. Dashboard
START_LEARNING.bat  # Verify UI loads
```

**Integration Tests:**
```bash
# Test full workflow
# 1. Create test error
python Scripts/test_error.py 2>&1 | python Scripts/error_listener.py

# 2. Create sidecar
python Scripts/lesson_sidecar.py create --file Scripts/test_error.py --line 4 --lesson "Test"

# 3. Show lessons
python Scripts/lesson_sidecar.py show --file Scripts/test_error.py
```

### Step 6: Finalize

1. **Create summary document** (for major changes)
   ```
   File: 00_Meta/[FEATURE_NAME]_IMPROVEMENTS.md
   Contents: What changed, why, benefits, migration notes
   ```

2. **Update task.md artifact** (if in task mode)
   - Mark phases complete
   - Document outcomes

3. **Create walkthrough** (if user requested)
   - Show what was built
   - Include test results
   - Screenshots/examples

---

## 🎯 Specific Update Scenarios

### Adding New Script

1. **Create script:** `Scripts/new_feature.py`
2. **Update SRS:** Add functional requirement
3. **Update PROJECT_STATUS:** Add to IDE Commands section
4. **Update workflows:** Add usage examples
5. **Update requirements.txt:** If new dependencies
6. **Test:** Run script with various inputs

### Deprecating Feature

1. **Rename:** `old.py` → `old.py.DEPRECATED`
2. **Create notice:** `old.DEPRECATED.md`
3. **Update SRS:** Mark as deprecated in changelog
4. **Update all docs:** Replace references
5. **Grep check:** Ensure no lingering references

### Changing Database Schema

1. **Create migration:** `migrate_vX.sql`
2. **Create runner:** `run_migration_vX.py`
3. **Update SRS:** Database schema section
4. **Test:** Run migration twice (idempotency)
5. **Verify:** Check foreign keys, indexes

### Restructuring Folders

1. **Plan:** Document new structure
2. **Migrate:** Move folders, update paths
3. **Update:** All README files
4. **Update:** Absolute paths in scripts
5. **Grep check:** Find hardcoded paths
6. **Test:** Verify scripts still work

---

## ⚠️ Common Mistakes to Avoid

### ❌ Don't Do This:
- Update script without updating docs
- Change SRS without updating version
- Deprecate without creating notice
- Modify database without migration script
- Skip consistency grep checks

### ✅ Do This Instead:
- Update script + all related docs
- Increment version + add changelog entry
- Create deprecation notice with replacement info
- Create idempotent migration + test
- Always run grep checks before completing

---

## 📝 Documentation Template

When creating improvement documents:

```markdown
# [Feature Name] - v[Version]

**Date:** YYYY-MM-DD
**Status:** Implemented ✅

## Problem
[What issue was being solved]

## Solution
[How it was solved]

## Changes
- File X: [what changed]
- File Y: [what changed]

## Testing
- [x] Test case 1
- [x] Test case 2

## Migration Notes
[How users should update]
```

---

## 🔍 Final Checklist

Before completing update:

- [ ] All affected scripts updated
- [ ] SRS.md version incremented
- [ ] SRS.md changelog updated
- [ ] PROJECT_STATUS.md updated
- [ ] Workflows updated (.agent/workflows/)
- [ ] README files updated
- [ ] Grep checks passed (no old references)
- [ ] Tests passed (smoke + integration)
- [ ] Migration tested (if DB changed)
- [ ] Deprecation notices created (if applicable)
- [ ] Improvement doc created (if major)
- [ ] Consistency verified across all docs

---

## 💡 Pro Tips

1. **Version numbering:**
   - Major refactor: v2 → v3
   - New feature: v2.1 → v2.2
   - Bug fix: v2.1.0 → v2.1.1

2. **Grep is your friend:**
   - Always check for old references
   - Search case-insensitive
   - Check both .md and .py files

3. **Test before documenting:**
   - Ensure feature works
   - Then write docs
   - Don't document broken features

4. **Keep SRS.md as source of truth:**
   - All requirements there
   - Other docs reference it
   - Update SRS first, others second

5. **Atomic updates:**
   - One logical change at a time
   - Don't mix unrelated updates
   - Easier to review and rollback

---

**Remember: Consistency across all documentation is critical for maintainability!**
