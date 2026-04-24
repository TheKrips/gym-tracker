# Design Spec: Workout Queue + Add Exercise
**Date:** 2026-04-25  
**Status:** Approved (implicit — user said "proceed")

---

## 1. Problem

The app schedules workouts by day-of-week (Mon=Upper A etc.), but the user rarely follows the day schedule. The queue should be day-agnostic: show workouts in a fixed cycle, highlight the next one automatically, let the user tap to start at any time → today's date gets assigned.

Additionally, users need to add extra exercises (especially abs) to an in-progress workout session.

---

## 2. Feature A — Sequential Workout Queue

### 2.1 Logic: `nextWorkoutId()`

Replaces `todayWorkout()`. Algorithm:
1. Read training log sessions from localStorage.
2. Find the most recent session's `workout_id`.
3. The queue cycle is `['upper_a', 'lower_a', 'upper_b', 'lower_b']`.
4. Return the next id after the last one. If history is empty → return `'upper_a'`.
5. If `override_today` has today's date → return that workout_id (preserve existing override logic).

### 2.2 Layout: Hero + Compact Row

```
┌─────────────────────────────────┐
│  [НАСТУПНЕ]  Upper A            │  ← Hero card, full width
│  Горизонтальний жим + тяга      │    pulse animation on border
└─────────────────────────────────┘
┌───────────┐┌───────────┐┌───────┐
│  Lower A  ││  Upper B  ││LowerB │  ← compact 3-col row, smaller text
└───────────┘└───────────┘└───────┘
```

All 4 cards tap → `startWorkout(id)` (assigns today's date as before).

### 2.3 Animations

- Hero card entrance: `opacity 0→1, translateY 8px→0`, `ease-out 250ms`
- Compact cards: stagger `60ms` delay per card, same animation
- Hero border: CSS `@keyframes border-pulse` — border color + faint box-shadow oscillates every 2.5s (infinite). Respects `prefers-reduced-motion`.
- "НАСТУПНЕ" pill: existing `.today-pill` style, text "Наступне"

### 2.4 Day labels

- Hero card: no day name — only "Наступне" pill
- Compact cards: show workout name + focus only (no day-of-week)
- Sequence order numbers (1–4) shown as small dimmed label on compact cards

### 2.5 CSS Changes

- Rename `.day-grid` → add `.queue-hero` + `.queue-rest` wrappers
- `.queue-hero .day-card` — full-width, larger padding, bigger name font
- `.queue-rest` — `grid-template-columns: repeat(3, 1fr)`, compact text
- `.day-card.next-up` — animated border pulse, subtle bg tint

---

## 3. Feature B — Add Exercise to Active Workout

### 3.1 Entry Point

Inside `startWorkout()` HTML template, after `<div id="ex-list">` and before `.fin`:
```html
<div id="add-ex-wrap">
  <button id="add-ex-btn" onclick="openExercisePicker()">
    + Додати вправу
  </button>
</div>
```

Style: ghost button, dashed border, full width, 44px+ height.

### 3.2 Bottom Sheet

Single instance injected once into `<body>` on app init (not recreated each render):

```
┌──────────────────────────────────────┐
│  ▬ (drag handle)                     │  ← sheet header
│  🔍 Пошук вправи...                  │  ← search input
├──────────────────────────────────────┤
│  ПРЕС                                │
│  • Скручування                       │
│  • Берізка (Hollow Body Hold)        │
│  • Підйом ніг лежачи                 │
│  • Підйом ніг у висі                 │
│  • Планка                            │
├──────────────────────────────────────┤
│  УСІ ВПРАВИ                          │
│  • Жим штанги лежачи (Upper A)       │
│  • Тяга верхнього блоку...           │
│  ...                                 │
└──────────────────────────────────────┘
```

**Open:** `transform: translateY(0)`, `transition: transform 0.3s cubic-bezier(0.16,1,0.3,1)`  
**Close:** `transform: translateY(100%)`  
**Backdrop:** `rgba(0,0,0,0.4)` overlay behind sheet, tap to dismiss

### 3.3 Abs Exercises (hardcoded constant `ABS_EXERCISES`)

```js
{ id:'abs_crunch', name:'Скручування', sets:3, reps:'15', weight_kg:0, rest_sec:60,
  cues:['Лягай на спину, руки за голову — НЕ тягни голову', 'Скорочуй прес, підводь лопатки від підлоги', 'Повільно опускайся (~2 сек)'], ... }
{ id:'abs_hollow', name:'Берізка (Hollow Body Hold)', sets:3, reps:'30с', weight_kg:0, rest_sec:60,
  cues:['Лягай, руки вздовж тіла або за голову', 'Підніми ноги і лопатки від підлоги, поперек притисни до підлоги', 'Утримуй позицію — не задержуй дихання'] }
{ id:'abs_leg_raise_lying', name:'Підйом ніг лежачи', sets:3, reps:'12', weight_kg:0, rest_sec:60,
  cues:['Руки під сідницями або вздовж тіла', 'Підніми прямі ноги до 90° — не відривай поперек', 'Повільно опускай, не торкаючись підлоги'] }
{ id:'abs_leg_raise_hang', name:'Підйом ніг у висі', sets:3, reps:'10', weight_kg:0, rest_sec:90,
  cues:['Вис на перекладині, плечі активні (не провисай)', 'Підніми ноги до прямого кута або вище', 'Контрольно опускай — не розгойдуйся'] }
{ id:'abs_plank', name:'Планка', sets:3, reps:'45с', weight_kg:0, rest_sec:60,
  cues:['Лікті під плечима, тіло пряма лінія', 'Стискай прес і сідниці — не прогинай поперек', 'Дихай рівномірно'] }
```

### 3.4 `addExerciseToSession(ex)`

1. Close bottom sheet.
2. Find current exercise count in `#ex-list` (for numbering).
3. Call `renderEx(ex, n+1)` to get HTML.
4. Append HTML to `#ex-list`.
5. Scroll new card into view with `scrollIntoView({behavior:'smooth'})`.
6. `updateProg()` to recalculate progress bar.

Added exercises work with existing `markSet()` / `addSet()` — no changes needed there.

### 3.5 Search filtering

`filterExercises(query)` — re-renders picker list items with `display:none` on non-matches. Case-insensitive, matches name substring.

---

## 4. Files Changed

- `index.html` — all changes (CSS + JS + HTML)
- `workout.json` — no changes needed (abs exercises hardcoded in JS)

---

## 5. Out of Scope

- Persisting added exercises back to `workout.json` (they exist in session log only)
- Editing/removing added exercises mid-workout
- Reordering exercises
