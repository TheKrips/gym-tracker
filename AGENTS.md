# Gym Tracker — Agent Documentation

Single-user fitness/health PWA. **For Claude Code: read [`CLAUDE.md`](CLAUDE.md) first** — it has the index.html line map and conventions. **For data schemas:** [`FORMAT_FOR_AI.md`](FORMAT_FOR_AI.md). This file is high-level only.

## Stack

- Frontend: single-file PWA in `index.html` (HTML+CSS+JS inline). Hosted on GitHub Pages (`https://thekrips.github.io/gym-tracker/`).
- Repo: `TheKrips/gym-tracker` (public).
- Data: JSON files at repo root. Storage: localStorage on device, persisted to GitHub via the user's PAT.
- Automation: `scripts/daily_coach.py` runs daily 04:00 UTC via `.github/workflows/daily-coach.yml`. Writes `coach-log.md` and bumps `workout.json:meta.version`.

## User

Roman, 35yo, ~177cm/65kg, 4×/week strength training, muscle-gain priority + longevity. Elevated LDL history (188→130 after diet). UA-speaker. Eats clean, minimal alcohol, sedentary work.

## Training program

4-day upper/lower split. Day map: Mon=upper_a, Tue=lower_a, Thu=upper_b, Fri=lower_b. Progression: double progression — top of rep range in ALL sets → +weight (compound upper +2.5kg, compound lower +5kg, isolation +1kg). Stalled 5+ sessions → deload −10%.

## Recovery scoring

Live in-app: `recoveryV2()` — composite 0–100 from Hooper, sleep, sleep-debt, A:C ratio, HRV/RHR z-scores, illness, alcohol. Daily coach Python uses simpler Hooper-only scoring (legacy). When formulas differ, in-app `recoveryV2` is the source of truth.

`hooper_score = (6 − sleep_quality) + stress + fatigue + soreness` → 4 (best) – 20 (worst).

| Hooper | Adjustment |
|---|---|
| ≤7 | +10 bonus |
| 8–11 | none |
| 12–15 | reduce_intensity |
| ≥16 | reduce_volume |

Plus: `illness=true` → skip; `alcohol_units≥3` → reduce_intensity; `sleep_hours<6` → reduce_volume.

## `override_today`

`workout.json:override_today = { date, workout_id }` forces today's workout. Coach clears it after the date passes.

## Live data URLs (cache-bypass)

```
https://raw.githubusercontent.com/TheKrips/gym-tracker/main/<file>?t=<timestamp>
```

Files: `logs.json`, `health-data.json`, `daily-notes.json`, `workout.json`, `coach-log.md`.

## Frameworks tracked

Double progression, Hooper, sessionRPE, A:C ratio (EWMA), Foster sRPE (load × monotony × strain), TRIMP for cardio, PMC (CTL/ATL/TSB EWMA, k=7/k=42), HRV/RHR baselines (60d ln-z), personal sleep need (top 25% of 90d), 14d sleep debt.
