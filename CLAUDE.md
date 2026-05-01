# CLAUDE.md — Token-Efficient Project Map

**For Claude only.** This file is the navigation index. **Do not read whole files** — jump to specific line ranges.

---

## Read-budget rules (важливо для економії токенів)

1. **NEVER** read `index.html` фуллом — це 5091 рядків. Завжди використовуй `Read` з `offset/limit` за картою нижче, або `Grep` з конкретним патерном.
2. **NEVER** read `health-data.json` (1.2 MB) — використовуй `Grep` для пошуку конкретних дат/полів. Структура описана у `FORMAT_FOR_AI.md`.
3. **NEVER** read `logs.json` фуллом без потреби (51 KB) — `Grep` за датою чи `workout_id`.
4. Перед запуском будь-якого редагування файлу — спочатку `Grep` для точного `old_string`, не читай файл цілком "щоб подивитись".
5. Не дублюй пошук через subagent, якщо вже маєш точну ціль — `Edit` напряму.
6. Для безконтекстних запитань (схема даних, користувач, цілі) — читай цей файл і `FORMAT_FOR_AI.md`, не `AGENTS.md` (він довший і дублює).

---

## Project shape (запам'ятай — не сканувати знову)

- Single-file PWA: `index.html` (HTML + CSS + JS, all inline). Hosted on GitHub Pages.
- Repo: `TheKrips/gym-tracker` (public). Live URL: `https://thekrips.github.io/gym-tracker/`.
- Data: JSON files at repo root, written via GitHub API from the app, by Apple Health sync, or by a daily Python coach (`scripts/daily_coach.py`, cron 04:00 UTC).
- User: Roman, 35yo, UA-speaker. 4-day upper/lower split (Mon=upper_a, Tue=lower_a, Thu=upper_b, Fri=lower_b).
- Today's workout id resolution: `workout.json:override_today` > `nextWorkoutId()` (cycle through last completed in logs).

---

## index.html — line map (5091 lines)

**HTML skeleton:**
| Range | Section |
|---|---|
| 1–2 | `<!doctype>`, `<html>` |
| 3–887 | `<head>` (meta, manifest, CSS — see CSS map) |
| 888–973 | `<body>`, `<header>`, top nav, primary pages (home/workout/history) |
| 974–1187 | Overlay shells (see overlay map below) |
| 1188–5081 | `<script>` (all JS — see JS map below) |
| 5082–5091 | Closing tags + service worker registration |

**CSS map (inside `<head>`):**
| Range | Section |
|---|---|
| ~3–170 | `:root` vars, base resets, layout |
| ~175–250 | Animations (`@keyframes card-in`, `border-pulse`, `dot-pulse`) |
| ~250–550 | Cards, day-grid, day-card, week-row, body-cards |
| ~550–700 | Coach overlay specifics (`.coach-sec`, `.perf-tri`, `.vital-chip`, `.ai-rec`) |
| ~700–887 | Forms, picker bottom-sheet, info-modal, toasts, picker |

(Use `Grep` for exact CSS class — selectors are unique enough.)

**Overlay shells (HTML):**
| Line | Overlay id | Purpose |
|---|---|---|
| 974 | `ov-session` | Active workout |
| 986 | `ov-settings` | Settings page |
| 1056 | `ov-metric` | Weight/fat/steps detail chart |
| 1068 | `ov-note` | Daily note editor (sleep, Hooper, HRV, RHR, BP, …) |
| 1080 | `ov-cardio` | Cardio session entry |
| 1092 | `ov-edit-session` | Edit a logged session from journal |
| 1104 | `ov-rpe` | Post-workout RPE/duration prompt |
| 1116 | `ov-coach-log` | AI Coach page |
| 1128 | `ov-pmc` | Performance Manager Chart page |
| 1140 | `ov-weekly-report` | Weekly narrative report |
| 1152 | `ov-ldl` | LDL/health markers |
| 1164 | `ov-funtest` | Functional longevity tests |

**JS map (script body, 1188–5081):**
| Range | Module |
|---|---|
| 1191–1214 | Top-level state: `workoutData`, `healthData`, `currentSession`, `editingSession`, `editingNote`, `editingCardio`, etc. |
| 1215–1308 | Page swiping (`swipeTo`, `pageWidth`, drag/touch handlers) |
| 1309–1359 | Overlay open/close (`openOverlay`, `closeOverlay`, swipe-to-dismiss) |
| 1360–1419 | Rest timer (`startTimer`, `timerHTML`, `beep`) |
| 1420–1537 | Settings page (`getSetting`, `setSetting`, `loadSettingsPage`) |
| 1538–1568 | Logs storage (`getLogs`, `saveLogs`, `addSession`) |
| 1569–1640 | Health rendering (`sparklineSVG`, `renderHealthSection`) |
| 1641–1769 | Home hero + week row (`renderTodayHero`, `renderWeekRow`, `openDayAt`) |
| 1770–1855 | Daily notes storage + card (`getDailyNote`, `upsertDailyNote`, `calcHooperScore`, `renderDailyNoteCard`) |
| **1856–2028** | **Daily note editor** (`openDailyNote`, `renderNoteEditor`, `setNoteField`, `setHooper`, `adjSleepH`, `noteNavDate`, `notePickDate`, `deleteDailyNote`) — **BP fields here ~1932** |
| 2029–2186 | Insights, muscle groups, weekly volume, A:C ratio (`renderInsights`, `MUSCLE_UA`, `computeWeeklyVolume`, `computeACRatio`) |
| 2187–2263 | Metrics section (`renderMetricsSection`) |
| **2264–2293** | **`GLOSSARY`** (info-tip dictionary) + `showInfo`/`closeInfo`/`infoBtn` |
| 2294–2481 | Body metric chart (`METRICS`, `openMetric`, `setMetricRange`, `renderMetric`, `drawMetricChart`) |
| 2482–2525 | `ABS_EXERCISES` constant + `buildPickerList` |
| **2526–2583** | **Exercise picker bottom-sheet** (`pickerContext`, `openExercisePicker`, `closeExercisePicker`, `filterExercises`, `addExerciseToSession`) — supports both `'active'` and `'edit'` contexts |
| 2584–2620 | Workout cycle resolution (`nextWorkoutId`, `renderDayGrid`) |
| 2621–2755 | Active workout (`startWorkout`, `renderExercises`, `renderEx`, `renderSS`, `markSet`, `addSet`, `removeSet`, `updateProg`, `finishWorkout`) |
| 2756–2913 | History/journal (`renderHistory`, `renderHistoryLog`, `renderProgressView`, `showSession`) |
| 2914–2923 | CSV export, local data wipe |
| 2924–3027 | Cardio entry (`openCardio`, `renderCardioContent`, `cardioNavDate`, `setCardioType`, `adjCardio`) |
| **3028–3166** | **Edit session** (`editSession`, `renderEditSessionContent`, `editSessNavDate`, `setEditSessRPE`, `adjEditSess`) — has "+ Додати вправу" button using `pickerContext='edit'` |
| 3167–3218 | Post-workout RPE prompt (`renderRPEContent`, `setRPE`, `adjDur`) |
| 3219–3451 | Functional tests (sit-to-stand, balance) — `getFuncTests`, `renderFuncTestBanner`, `renderFuncTestContent`, `toggleStsTimer`, `toggleBalance` |
| 3452–3603 | AI/private repo settings, Weekly Report (`saveAISettings`, `openWeeklyReport`, `reportHTML`, `renderWeeklyReportBanner`) |
| 3605–3681 | LDL/health markers (`getHealthMarkers`, `openLDL`, `renderLDLContent`) |
| **3682–4367** | **AI Coach page** (`coachLogText`, `renderCoachLogBanner`, `openCoachLog`, `parseCoachData`, `liveCoachMetrics`, `renderCoachLogContent`) — biggest function in the file. BP wired in at `liveCoachMetrics` ~3858 and merge `~3925`. Vitals chips ~4054. Missing-data prompts ~4324. |
| **4368–4484** | **PMC page** (`pmcRange`, `openPMC`, `setPMCRange`, `renderPMC`) |
| **4485–4733** | **Coach engine** (formulas): `personalSleepNeed`, `sleepDebt14d`, `cardioTRIMP`, `dailyLoad`, `pmcMetrics` (CTL/ATL/TSB EWMA), `acwrEWMA`, `hrvBaseline`, `rhrBaseline`, `recoveryV2`, `strainScore`, `hooperTrend`, `overreachingFlag`, `fosterMetrics` |
| 4734–4948 | `MUSCLE_TARGETS`, `aiRecommendations(d)` — generates ranked rec cards |
| 4949–4980 | Misc helpers (`_computeRecoveryFromNote`, `computeFTScore`, `saveNutrTargets`) |
| 4981–5081 | Toast, app init (`showToast`, `init`, fetch loops, service worker hookup) |

---

## Common task → location (look here first)

| Task | File:Line |
|---|---|
| Add a new field to daily note editor | `index.html:1870` (`renderNoteEditor`) — pattern: add to `<div class="num-inputs-row">`, wire `oninput="editingNote.X=…"` |
| Wire that field into coach analysis | `index.html:3851` (`liveCoachMetrics`) — add `m.X=noteToday.X` |
| Then merge into render data | `index.html:3911` (`parseCoachData` end / `renderCoachLogContent` data merge) — add `X:live.X` |
| Then add a Vitals chip | `index.html:4054` — push to `chips[]` array, classify with `cls` |
| Then add to "missing data" prompt | `index.html:4324` |
| Add an info-tip term | `index.html:2264` (`GLOSSARY`) — key + `{t,b}` then `infoBtn('key')` in markup |
| Add a new abs/extra exercise to picker | `index.html:2482` (`ABS_EXERCISES`) |
| Add a new overlay page | shell at `index.html:1116`-area + render fn near coach (~3909) + open fn |
| Modify recovery formula | `index.html:4585` (`recoveryV2`) |
| Modify training-load formula | `index.html:4528` (`dailyLoad`) + `4716` (`fosterMetrics`) |
| Override today's workout | edit `workout.json` → `override_today: {date, workout_id}` |
| Force a specific workout for the user today | edit `workout.json` `override_today` AND optionally rewrite `coach-log.md` |

---

## Conventions (don't ask, just follow)

- **UI copy: Ukrainian.** Labels, buttons, prompts, toast messages — all UA. Code identifiers stay English.
- **No comments unless the WHY is non-obvious.** No banners, no section headers. Existing code does not have them.
- **No emojis in code or JSON.** Emoji icons in UI strings (e.g. `'❤️'`, `'🩺'`) are OK because they already exist in the GLOSSARY and `aiRecommendations` patterns — match the existing style.
- **Inline-everything style.** Don't propose splitting `index.html`. Don't create new build steps. Don't introduce frameworks/bundlers.
- **No try/catch around localStorage reads beyond the existing pattern** (`try{return JSON.parse(localStorage.getItem(k)||'…')}catch(e){return …}`) — copy the pattern, don't expand it.
- **Date strings: `YYYY-MM-DD`** everywhere (`new Date().toISOString().slice(0,10)`).
- **State mutation pattern for editors:** assign to `editingNote` / `editingSession` / `editingCardio`, then call the matching `render…Content()` to repaint.
- **Picker reuse:** the bottom-sheet picker takes a `pickerContext` flag (`'active'` | `'edit'`). Don't duplicate the picker; route via this flag.
- **Charts are inline SVG**, no chart library. ViewBox + `preserveAspectRatio='none'` for stretchable area charts.
- **Cache-busting fetch:** raw GitHub URLs use `?t=${Date.now()}`.
- **Leg press weights** in logs are *actual loaded weight* (machine base 20 kg already deducted from April 16 2026 onwards).

---

## Git workflow

- Default branch: `main`. Push directly. No PR workflow for this solo repo.
- Commit messages: lowercase prefix style (`feat:`, `fix:`, `coach:`, `log:`, `chore:`). One-line subject + optional body.
- Co-author trailer is fine but not required.
- The user has authorised autonomous commits and pushes — do not ask for confirmation on routine work in this repo.
- If push is rejected: `git pull --rebase`, resolve in-place (the daily-coach Action often pushes between local commits), then push.

---

## What is in `docs/superpowers/`

Specs and plans for features (one Markdown file per feature, dated). Reference but rarely needed for new tasks.

---

## What NOT to do

- Don't touch `logs.json`, `health-data.json`, `daily-notes.json` directly unless explicitly asked. They are user-data.
- Don't add new dependencies / npm / bundlers / frameworks.
- Don't restructure folders.
- Don't write README/docs unless asked.
- Don't run dev servers — there is no build, just open `index.html`.
- Don't read `AGENTS.md` and this file both — this file supersedes for navigation; `FORMAT_FOR_AI.md` for schemas.
