# DEPRECATED - Use lesson_sidecar.py Instead

This file has been deprecated in favor of the safer **Sidecar File Approach**.

## Why Deprecated?

1. **Syntax Risk** - Regex injection can break code syntax
2. **Linter Conflicts** - AI comments trigger ESLint/Prettier warnings
3. **Git Noise** - Pollutes git diff during development

## New Approach: Sidecar Files

Use `lesson_sidecar.py` instead:

```bash
# Create lesson sidecar
python Scripts/lesson_sidecar.py create --file myfile.py --line 45 --lesson "Your lesson"

# Show lessons
python Scripts/lesson_sidecar.py show --file myfile.py

# List all files with sidecars
python Scripts/lesson_sidecar.py list
```

## Benefits

- ✅ **No code modification** - Source files stay clean
- ✅ **No linter conflicts** - Lessons in separate .lessons.md file
- ✅ **Git-friendly** - Can gitignore .lessons.md
- ✅ **Spatial memory preserved** - Sidecar next to code file

## Migration

No migration needed. Simply start using sidecar approach for new lessons.

Old inline comments (if any) can stay or be manually removed.

---

**This file kept for reference only. Do not use.**
