# Gym Tracker — Format Guide for AI Agents

This document describes the data formats used in this gym tracking system.

## Files

- `workout.json` — current training program (AI updates this)
- `logs.json` — all training sessions (app writes this automatically)

---

## workout.json Schema

```json
{
  "meta": {
    "version": "1.0",
    "created": "YYYY-MM-DD",
    "profile": "Description of the athlete",
    "goal": "Training goal"
  },
  "schedule": [
    { "day": "Понеділок", "workout_id": "upper_a" }
  ],
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
          "type": "compound | isolation | superset",
          "warmup": "40 кг × 8 | null",
          "sets": 4,
          "reps": "6",
          "weight_kg": 70,
          "rir": "1-2",
          "rest_sec": 180,
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
      "cues": ["Cue 1"]
    }
  ]
}
```

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
      "date": "2026-03-27",
      "workout_id": "upper_a",
      "workout_name": "Upper A",
      "finished_at": "2026-03-27T10:45:00.000Z",
      "exercises": [
        {
          "exercise_id": "bench_press",
          "sets": [
            { "set": 1, "weight": 70, "reps": 6 },
            { "set": 2, "weight": 70, "reps": 6 },
            { "set": 3, "weight": 70, "reps": 5 },
            { "set": 4, "weight": 70, "reps": 5 }
          ]
        }
      ]
    }
  ]
}
```

---

## How to Update the Program (AI Agent Instructions)

1. Read `logs.json` from: `https://raw.githubusercontent.com/TheKrips/gym-tracker/main/logs.json`
2. Analyze recent sessions: identify which exercises are progressing (hitting top of rep range in all sets)
3. Apply **double progression**: if athlete hit the top of rep range in ALL sets → increase weight by 2.5kg (upper) or 5kg (lower)
4. Update `workout.json` with new weights/reps while keeping all other fields intact
5. Push `workout.json` to the repo (commit message format: `update: program YYYY-MM-DD`)
6. Do NOT modify `logs.json`

### Double Progression Rule
- Rep range e.g. 6-12 means: start at 6, add 1 rep per session
- When athlete reaches 12 reps in ALL sets → add weight, reset to 6 reps
- Compound: +2.5 kg; Legs: +5 kg

### Reading Live Logs
Latest logs always available at:
```
https://raw.githubusercontent.com/TheKrips/gym-tracker/main/logs.json
```
(Use `?t=<timestamp>` to bypass cache)
