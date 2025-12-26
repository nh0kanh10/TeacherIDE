# PRE-COMMIT HOOK - DEPRECATED for Sidecar Approach

**Status:** No longer needed with v2.1 sidecar approach

## Why Deprecated?

With the new sidecar file system (v2.1):
- AI lessons are in `.lessons.md` files, NOT in source code
- Source code files are never modified by AI
- No need to strip AI comments before commit

## Migration

If you installed the pre-commit hook:
```bash
rm .git/hooks/pre-commit
```

## Gitignore Sidecars (Optional)

If you want to keep lessons private:
```bash
# Add to .gitignore
*.lessons.md
```

## For Reference Only

The old pre-commit hook stripped `AI-COACH-START/END` markers from inline comments.
This was necessary for v2.0 inline injection approach but is obsolete now.

---

**This file kept for reference only. Do not use with v2.1.**
