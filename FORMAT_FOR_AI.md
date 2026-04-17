# Gym Tracker — Format Guide for AI Agents

This document describes the data formats used in this gym tracking system.

## Files

| File | Written by | Purpose |
|------|-----------|---------|
| `workout.json` | AI Coach / manual | Current training program |
| `logs.json` | App (via GitHub API) | All training sessions (DO NOT overwrite) |
| `health-data.json` | Apple Health sync | Raw health samples (DO NOT overwrite) |
| `daily-notes.json` | App (via GitHub API) | Daily mood/sleep/energy/nutrition notes |
| `coach-log.md` | AI Coach (GitHub Actions) | Daily analysis report |
| `scripts/daily_coach.py` | — | Daily coach automation script |

---

## workout.json Schema

```json
{
  "meta": {
    "version": "3.0",
    "created": "YYYY-MM-DD",
    "updated": "YYYY-MM-DD",
    "profile": "Чоловік, 35р, 177см, ~65кг, стаж ~3 місяці.",
    "goal": "Training goal",
    "progression": "Double progression rules description"
  },
  "schedule": [
    { "day": "Понеділок", "workout_id": "upper_a" },
    { "day": "Вівторок", "workout_id": "lower_a" },
    { "day": "Четвер", "workout_id": "upper_b" },
    { "day": "Пʼятниця", "workout_id": "lower_b" }
  ],
  "override_today": {
    "date": "2026-04-16",
    "workout_id": "lower_a"
  },
  "workouts": [
    {
      "id": "upper_a",
      "name": "Upper A",
      "day": "Понеділок",
      "focus": "Short description of focus",
      "exercises": [
        {
          "id": "bench_press",
          "name": "Exercise name (Ukrainian)",
          "type": "compound | isolation",
          "primary_muscles": ["chest", "triceps"],
          "secondary_muscles": ["anterior_deltoid"],
          "warmup": "40 кг × 8 | null",
          "sets": 4,
          "reps": "8",
          "weight_kg": 70,
          "rir": "1-2",
          "rest_sec": 180,
          "jefit_url": "https://www.jefit.com/exercises/...",
          "cues": ["Cue 1", "Cue 2"],
          "note": "Optional coaching note | null"
        }
      ]
    }
  ]
}
```

### Muscle Group IDs
`chest`, `triceps`, `biceps`, `brachialis`, `anterior_deltoid`, `lateral_deltoid`, `posterior_deltoid`, `back_lat`, `back_mid`, `traps`, `rhomboids`, `erectors`, `quadriceps`, `hamstrings`, `glutes`, `calves`, `hip_flexors`, `abs`

### Superset Exercise Type

```json
{
  "id": "superset_bicep_tricep_a",
  "name": "Суперсет: Біцепс + Тріцепс",
  "type": "superset",
  "warmup": null,
  "rest_sec": 90,
  "note": "3 кола, відпочинок між колами 1.5 хв",
  "exercises": [
    {
      "id": "bicep_curl_a",
      "name": "Exercise name",
      "sets": 3,
      "reps": "12",
      "weight_kg": 9,
      "jefit_url": "https://www.jefit.com/exercises/...",
      "cues": ["Cue 1"]
    }
  ]
}
```

### override_today

Optional field. When set, the app shows this workout as today's workout regardless of schedule. The daily coach script removes it once the date has passed.

### rest_sec Guidelines
- Compound (squat, bench, deadlift): 150-180
- Compound (rows, pulldowns): 120-150
- Isolation: 60-90
- Superset rest between rounds: 90

---

## logs.json Schema

This file is written by the app. **Do not overwrite it** — only read it.

```json
{
  "sessions": [
    {
      "date": "2026-04-16",
      "workout_id": "lower_a",
      "workout_name": "Lower A",
      "finished_at": "2026-04-16T18:30:00.000Z",
      "duration_min": 58,
      "rpe": 7,
      "load_au": 406,
      "exercises": [
        {
          "exercise_id": "squat",
          "sets": [
            { "set": 1, "weight": 62.5, "reps": 7 },
            { "set": 2, "weight": 62.5, "reps": 10 }
          ]
        }
      ]
    }
  ]
}
```

Session fields (Phase 1, app will collect post-workout):
- `duration_min`: workout duration in minutes
- `rpe`: session RPE on CR-10 scale (0-10), collected after workout
- `load_au`: training load = duration_min × rpe (arbitrary units)

**Acute:Chronic ratio** = mean(7-day load AU) / mean(28-day load AU). Sweet spot: 0.8–1.3. Above 1.5 = overreach risk.

### Skipped sessions

When user skips a workout, it's logged as:
```json
{
  "date": "2026-04-15",
  "workout_id": "lower_a",
  "workout_name": "Lower A",
  "skipped": true,
  "exercises": [],
  "finished_at": "2026-04-15T10:00:00.000Z"
}
```

---

## health-data.json Schema

Raw Apple Health samples. **Do not overwrite** — synced automatically.

```json
{
  "generatedBy": "HealthGitSync",
  "lastSyncedAt": "2026-04-16T22:38:28Z",
  "samples": [
    {
      "type": "stepCount | bodyMass | bodyFatPercentage | bodyMassIndex",
      "value": 5432,
      "unit": "count | kg | percent",
      "startDate": "2026-04-16T10:00:00Z",
      "endDate": "2026-04-16T10:15:00Z",
      "sourceName": "iPhone (Roman)"
    }
  ]
}
```

Notes:
- `stepCount` must be summed per day (multiple samples per day)
- `bodyMass`, `bodyFatPercentage`, `bodyMassIndex` — take last value per day

---

## daily-notes.json Schema

Written by the app. **Do not overwrite.**

Uses **Hooper Index** framework for recovery assessment.

```json
{
  "notes": [
    {
      "date": "2026-04-16",
      "hooper": {
        "sleep_quality": 4,
        "stress": 2,
        "fatigue": 2,
        "soreness": 1
      },
      "hooper_score": 7,
      "sleep_hours": 7.5,
      "nutrition_adherence": 4,
      "kcal": 2300,
      "protein_g": 135,
      "alcohol_units": 0,
      "illness": false,
      "notes": "Free-form note from the user",
      "updated_at": "2026-04-16T20:00:00Z"
    }
  ]
}
```

Fields:
- `hooper.sleep_quality`: 1-5 (1=жахливо, 5=чудово) — **higher is better**
- `hooper.stress`: 1-5 (1=немає, 5=екстремальний) — lower is better
- `hooper.fatigue`: 1-5 (1=свіжий, 5=виснажений) — lower is better
- `hooper.soreness`: 1-5 (1=немає, 5=дуже боляче) — lower is better
- `hooper_score`: computed = (6 - sleep_quality) + stress + fatigue + soreness. Range 4-20, **lower = better recovery**
  - 4-7: optimal | 8-11: good | 12-15: moderate | 16-20: poor
- `sleep_hours`: objective sleep duration in hours (0-14)
- `nutrition_adherence`: 1-5 (1=дуже погано, 5=ідеально)
- `kcal`: daily calories (optional, approximate)
- `protein_g`: daily protein in grams (optional)
- `alcohol_units`: standard drink units (0 = none)
- `illness`: boolean — sick today
- `notes`: free-form text

### Backwards compatibility
Old records may have `mood`, `energy`, `sleep_h`, `nutrition`, `tags`, `text` fields. Coach script supports both formats.

---

## Daily Coach (GitHub Actions)

Runs at **04:00 UTC daily** via `.github/workflows/daily-coach.yml`.

### What it does:
1. Reads all data files
2. Analyzes yesterday's session performance
3. Checks health metrics trends (weight, fat, steps)
4. Reads daily notes (sleep, mood, energy, nutrition, tags)
5. Assesses recovery score (0-100)
6. Applies **double progression** to exercises
7. Adjusts today's workout if recovery is low
8. Updates `workout.json` (bumps version)
9. Generates `coach-log.md`
10. Commits and pushes

### Recovery adjustments:
| Condition | Action |
|-----------|--------|
| Sleep < 6h or energy 1/5 | -1 set on all exercises |
| Sleep < 7h or mood 1-2/5 | No weight PRs today |
| Tag: 🤒 Хворію | Skip recommended |
| Tag: 🍺 Алкоголь | Reduce intensity |
| 5+ days without training | First set is warmup |
| 7+ days without training | Deload -10% |

### Double Progression Rule
- Compound rep range: 6-10
- Isolation rep range: 10-15
- When athlete hits top of rep range in ALL sets → add weight, reset to bottom
- Compound upper: +2.5 kg; Compound lower: +5 kg; Isolation: +1 kg
- Stalled 5+ sessions → deload -10%

### Reading Live Data
```
https://raw.githubusercontent.com/TheKrips/gym-tracker/main/logs.json?t=<timestamp>
https://raw.githubusercontent.com/TheKrips/gym-tracker/main/health-data.json?t=<timestamp>
https://raw.githubusercontent.com/TheKrips/gym-tracker/main/daily-notes.json?t=<timestamp>
```
