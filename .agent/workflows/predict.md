---
description: Predict struggle on new skills - Bayesian approach
---

# /predict - Statistical Prediction Engine

Predicts struggle probability before learning new skills.

## Usage

```bash
python Scripts/statistical_predictor.py
```

Or programmatic:

```python
from statistical_predictor import StatisticalPredictor, PredictionInput

predictor = StatisticalPredictor()

# Your performance data
input_data = PredictionInput(
    error_count_by_concept=3,      # Errors in similar concepts
    time_to_first_correct=180,     # Seconds to first success
    prior_difficulty=6,            # Skill difficulty (1-10)
    learning_velocity=2.0          # Topics/week pace
)

result = predictor.predict_struggle(input_data)

print(f"Struggle probability: {result.struggle_probability:.1%}")
print(f"Confidence: {result.confidence:.1%}")
print(f"Recommended action: {result.action}")
```

## Output

- **struggle_probability** (0-1): Bayesian posterior probability
- **confidence** (0-1): Based on data quality
- **action**: `'scaffold'` or `'normal'`
  - `scaffold` (≥65%): Add examples, simplify
  - `normal` (<65%): Teach normally

## Algorithm

**Bayesian Updating:**
1. **Prior** from skill difficulty
2. **Likelihood** from error rate, response time, velocity
3. **Posterior** = (Likelihood × Prior) / Normalization

**NOT ML** - uses statistics only!

## Example Output

```
Easy learner (1 error, 60s, diff 5, velocity 3.0):
  → 16% struggle, normal teaching

Struggling (5 errors, 400s, diff 8, velocity 0.5):
  → 99% struggle, scaffold needed!
```

## When to Use

- Before starting a new complex topic
- After seeing early struggles
- To decide scaffolding approach
