# Gym Tracker — Agent Documentation

A personal fitness/health/longevity PWA for a single user. This document gives any AI agent everything needed to understand and work with this project.

## Architecture Overview

| Layer | What | Where |
|---|---|---|
| Frontend | Single-file PWA (HTML/CSS/JS) | `index.html` |
| Data storage | JSON files in this GitHub repo | root directory |
| Automation | Python script via GitHub Actions | `scripts/daily_coach.py` |
| CI/CD | GitHub Actions cron | `.github/workflows/daily-coach.yml` |
| Hosting | GitHub Pages | `https://thekrips.github.io/gym-tracker/` |

**Repo:** `https://github.com/TheKrips/gym-tracker` (public)

## User Profile

- **Roman**, 35yo male, 177cm, ~65kg, ~15% body fat
- **Training:** 3 months gym experience (post-years-break), 4x/week strength training
- **Goals:** Muscle gain (priority), longevity, quality health in old age
- **Diet:** Eats clean (fish, chicken, shrimp, rice, buckwheat). Hard gainer. Minimal alcohol (2-3 drinks/month).
- **Health notes:** Elevated LDL: Apr 2025=188 mg/dL → Aug 2025=130 mg/dL after diet changes. Target <100.
- **Lifestyle:** Sedentary work (home computer), adding 1-2x cardio/week

## Data Files

| File | Written by | Purpose | Safe to overwrite? |
|---|---|---|---|
| `workout.json` | AI Coach / manual | Current training program | ✅ Yes |
| `logs.json` | App (GitHub API) | All training sessions | ❌ Never |
| `health-data.json` | Apple Health sync (~12:00 UTC daily) | Raw health samples | ❌ Never |
| `daily-notes.json` | App (GitHub API) | Daily Hooper + nutrition notes | ❌ Never |
| `coach-log.md` | AI Coach (Actions) | Daily analysis report | ✅ Yes |
| `FORMAT_FOR_AI.md` | Manual | Complete schema docs | ✅ Yes |

See `FORMAT_FOR_AI.md` for full JSON schemas.

## Training Program (v3.x)

4-day upper/lower split:
- **Monday** — Upper A (horizontal press + vertical pull)
- **Tuesday** — Lower A (quads + hamstrings)
- **Thursday** — Upper B (horizontal pull + vertical pull + press)
- **Friday** — Lower B + Abs (hamstrings, RDL, core)

**Progression:** Double progression — hit top of rep range in ALL sets → increase weight, reset to bottom of range.
- Compound upper: +2.5 kg | Compound lower: +5 kg | Isolation: +1 kg
- Stalled 5+ sessions → deload -10%

**Muscle groups** tracked per exercise via `primary_muscles` and `secondary_muscles` arrays.

## Daily Coach (GitHub Actions)

Runs at **04:00 UTC daily** via `.github/workflows/daily-coach.yml`. Entry point: `scripts/daily_coach.py`.

### What it does:
1. Reads `logs.json`, `health-data.json`, `daily-notes.json`, `workout.json`
2. Analyzes training: session frequency, PRs, progression eligibility
3. Analyzes health: weight/fat trends, step count
4. Assesses recovery via **Hooper Index** (sleep quality, stress, fatigue, soreness — each 1-5)
5. Applies double progression to exercises
6. Applies recovery adjustments to today's workout
7. Removes expired `override_today`
8. Increments `workout.json` version (patch bump)
9. Writes `coach-log.md` + commits both files

### Recovery assessment (Hooper-based):
`hooper_score = (6 - sleep_quality) + stress + fatigue + soreness` → 4 (optimal) to 20 (poor)

| Score | Status | Action |
|---|---|---|
| ≤7 | Optimal | +10 pts bonus |
| 8-11 | Good | No change |
| 12-15 | Moderate | `reduce_intensity` |
| ≥16 | Poor | `reduce_volume` |

Additional signals: `illness=true` → `skip_recommended`; `alcohol_units >= 3` → `reduce_intensity`; `sleep_hours < 6` → `reduce_volume`

## Recovery Adjustments Applied:

| Adjustment | Effect |
|---|---|
| `skip_recommended` | Log recommendation only (no weight change) |
| `deload` | All weights ×0.9 |
| `reduce_volume` | -1 set per exercise |
| `reduce_intensity` | Note only — no PR attempts today |

## Scientific Frameworks

| Framework | Implementation | Status |
|---|---|---|
| **Double progression** | `daily_coach.py:check_progression()` | ✅ Live |
| **Hooper Index** | `daily_coach.py:assess_recovery()` + app | ✅ Live |
| **sessionRPE** | `logs.json` fields `rpe`, `load_au` | 🔄 Phase 1 |
| **Acute:Chronic ratio** | `coach_log.md` analysis | 🔄 Phase 1 |
| **Volume per muscle group** | via `primary_muscles` in `workout.json` | 🔄 Phase 1 |
| **VO2max proxy** | Monthly functional tests | 🔄 Phase 4 |
| **Functional longevity tests** | Monthly check section | 🔄 Phase 4 |

## Key Technical Decisions

- **No paid AI APIs** in automation — pure deterministic Python logic
- **PWA**: safe-area-inset-top for iPhone notch, iOS swipe-back gesture on overlays
- **Cache invalidation**: workout.json has version; app uses localStorage key `workout_v{version}`
- **Leg press weights**: All logged values are the actual loaded weight (machine base 20kg already deducted since April 16, 2026)
- **override_today** in `workout.json`: overrides today's scheduled workout. Cleared by coach after the date passes.
- **Skipped sessions** stored in `logs.json` with `"skipped": true`

## Common Tasks for Agents

### Update the training program
Edit `workout.json`. Bump `meta.version` manually (e.g. 3.1 → 3.2). The daily coach will continue incrementing from there. Always preserve `primary_muscles` and `secondary_muscles` on each exercise.

### Add a one-off workout override
Set `override_today` in `workout.json`:
```json
"override_today": { "date": "YYYY-MM-DD", "workout_id": "upper_a" }
```

### Read live data from GitHub
Use the raw URLs with a timestamp to bypass cache:
```
https://raw.githubusercontent.com/TheKrips/gym-tracker/main/logs.json?t=TIMESTAMP
https://raw.githubusercontent.com/TheKrips/gym-tracker/main/health-data.json?t=TIMESTAMP
https://raw.githubusercontent.com/TheKrips/gym-tracker/main/daily-notes.json?t=TIMESTAMP
```

### Check training volume per muscle group
Read `workout.json`, loop workouts, sum `primary_muscles` counts per week. Target: 6-20 working sets/muscle/week for hypertrophy.

### Interpret a session's training load
`load_au = rpe × duration_min` (once Phase 1 app collects sessionRPE).
Acute:Chronic ratio = mean(last 7d load AU) / mean(last 28d load AU).

## Planned Phases

| Phase | Description | Status |
|---|---|---|
| 0 | Schema migration (Hooper, muscle_groups, nutrition) | ✅ Done |
| 1 | UI: sessionRPE post-workout, monthly longevity tests as persistent banner, kcal/protein tracking | 🔄 Next |
| 2 | Private profile repo, comprehensive user profile via chat onboarding | 🔄 Pending |
| 3 | Metrics engine: A:C ratio, weekly volume per muscle, VO2max estimate | 🔄 Pending |
| 4 | Longevity functional tests (sit-to-stand, balance, step test) | 🔄 Pending |
| 5 | Weekly AI narrative report (Claude API, weekly, aggregated) | 🔄 Pending |
| 6 | LDL tracking, nutrition targets | 🔄 Pending |
