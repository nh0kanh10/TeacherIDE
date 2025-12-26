# Languages - Foreign Language Learning

Folder for learning foreign languages (English, Japanese, Chinese, etc.)

## Recommended Structure

```
02_Languages/
├── English/
│   ├── Vocabulary/
│   ├── Grammar/
│   └── Business_English/
├── Japanese/
│   ├── JLPT_N5/
│   ├── JLPT_N3/
│   └── Kanji/
└── README.md (this file)
```

## Integration with AI Coach

- Use topic tags: `English`, `Japanese`, etc.
- Error-driven learning works for writing practice
- File tracking can monitor vocabulary files

## Example Usage

```bash
# Learn English vocabulary
python Scripts/ai_teach.py concept "Business English idioms"
# Saved to 05_Extracted_Knowledge/ with topic: English

# Track vocabulary file
python Scripts/file_tracker.py track --file 02_Languages/English/vocab.txt --event open
```
