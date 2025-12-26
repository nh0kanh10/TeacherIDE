---
description: Create 6-week learning curriculum with dependencies
---

# /plan - Short Horizon Curriculum Planner

Generates 6-week learning plan using skill dependency graph.

## Usage

```bash
python Scripts/curriculum_planner.py
```

Or programmatic:

```python
from curriculum_planner import ShortHorizonPlanner

planner = ShortHorizonPlanner()

# Generate 6-week plan
plan = planner.plan_6_weeks(language='python')

print(f"Total skills: {plan['total_skills']}")
print(f"Estimated hours: {plan['estimated_hours']}")

for week_plan in plan['weeks']:
    print(f"\nWeeks {week_plan['week_range']}: {week_plan['focus']}")
    for skill in week_plan['skills']:
        print(f"  - {skill}")
```

## Output Structure

```python
{
    'weeks': [
        {
            'week_range': '1-2',
            'skills': ['variables', 'data_types', ...],
            'focus': 'Fundamentals'
        },
        ...
    ],
    'total_skills': 12,
    'estimated_hours': 60,
    'known_skills': 0,
    'horizon': '6 weeks'
}
```

## Algorithm

**DAG Topological Sort:**
1. Load skill dependency graph
2. Get current mastered skills (mastery > 0.7)
3. Find skills with prerequisites met
4. Sort topologically (dependencies first)
5. Plan ~2 skills/week for 6 weeks

**Scope:** 6-8 weeks ONLY (per expert feedback)
- NOT 12-month career roadmap (that's v5.0)
- Focus: short-term achievable goals

## Example Output

```
Weeks 1-2: Fundamentals
  - variables
  - data_types
  - conditionals
  - for_loops

Weeks 3-4: Data Structures
  - lists
  - dictionaries
  - list_comprehension
  - functions

Total: 12 skills, 60 hours
```

## When to Use

- Starting a new programming language
- Planning next 6 weeks of study
- After completing a major milestone
- When feeling directionless
