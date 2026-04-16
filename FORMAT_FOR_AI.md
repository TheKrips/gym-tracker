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

```json
{
  "notes": [
    {
      "date": "2026-04-16",
      "mood": 4,
      "energy": 3,
      "sleep_h": 7.5,
      "nutrition": 3,
      "tags": ["💪 Сила", "🚶 Активний"],
      "text": "Free-form note from the user",
      "updated_at": "2026-04-16T20:00:00Z"
    }
  ]
}
```

Fields:
- `mood`: 1-5 (1=😞, 2=😕, 3=😐, 4=🙂, 5=😄)
- `energy`: 1-5
- `sleep_h`: hours of sleep (0-14)
- `nutrition`: 1-4 (1=🥤 Погано, 2=🍔 Фастфуд, 3=🥗 Норм, 4=💎 Чисто)
- `tags`: from predefined list (💪 Сила, 🔥 Енергія, 😴 Втомлений, 🤒 Хворію, 💊 Кофеїн, 🚶 Активний, 🧘 Стрес, 🍺 Алкоголь, 🥩 Високо білка, 🚰 Вода +)

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
