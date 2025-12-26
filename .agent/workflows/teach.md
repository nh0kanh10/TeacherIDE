---
description: /teach - Explain code, concept, or last error
---

# /teach Command

AI explains concepts, code, or errors directly in IDE.

## Usage

```bash
# Explain last error
python Scripts/ai_teach.py error

# Explain a concept
python Scripts/ai_teach.py concept "LINQ query syntax"

# Explain code in current file
python Scripts/ai_teach.py file path/to/file.cs --line 45

# Show file insights
python Scripts/ai_teach.py insights path/to/file.py
```

## Examples

**After getting an error:**
```bash
python Scripts/ai_teach.py error
# Shows last error from errors_log with AI explanation
```

**Learning new concept:**
```bash
python Scripts/ai_teach.py concept "C# async/await"
# AI teaches the concept and saves to vault
```

**Code review:**
```bash
python Scripts/ai_teach.py file BookingService.cs --line 67
# AI explains code at specific line
```
