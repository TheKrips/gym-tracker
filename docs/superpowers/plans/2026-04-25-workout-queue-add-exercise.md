# Workout Queue + Add Exercise Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace day-of-week workout scheduling with a sequential queue (next highlighted) and add a bottom-sheet exercise picker to active workouts.

**Architecture:** Single-file PWA (`index.html`) — all CSS, HTML templates, and JS in one file. No build step, no framework. Changes are CSS additions, new JS functions, and modifications to `renderDayGrid()` and `startWorkout()`. Bottom sheet is injected into `<body>` once on init.

**Tech Stack:** Vanilla JS, CSS custom properties (`var(--p)`, `var(--s1)`, `var(--bd2)`, etc.), localStorage for logs.

---

## Task 1: CSS — Queue layout + animations

**Files:**
- Modify: `index.html` (CSS block, around line 155–167)

- [ ] **Step 1: Add queue CSS after the existing `.day-grid` block (line ~156)**

Find the block:
```css
.day-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px}
```

Add after it:
```css
    /* ── Workout Queue ───────────────────────────────────────── */
    .queue-hero{margin-bottom:8px}
    .queue-rest{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px}
    .day-card{
      background:var(--s1);border:var(--bh) solid var(--bd2);border-radius:var(--rad);padding:13px 11px;
      cursor:pointer;-webkit-tap-highlight-color:transparent;
      transition:transform 140ms var(--eo3),box-shadow 200ms ease,border-color 200ms ease;
      animation:card-in .28s ease-out both;
    }
    .day-card:active{transform:scale(0.96)}
    .queue-hero .day-card{padding:16px 14px}
    .queue-hero .day-card-name{font-size:16px}
    .queue-rest .day-card{padding:10px 9px}
    .queue-rest .day-card-name{font-size:12px}
    .queue-rest .day-card-focus{font-size:10px}
    .day-card.next-up{
      border-color:rgba(139,92,246,.5);
      background:rgba(139,92,246,.05);
      animation:card-in .28s ease-out both, border-pulse 2.5s ease-in-out 0.3s infinite;
    }
    @keyframes card-in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
    @keyframes border-pulse{
      0%,100%{border-color:rgba(139,92,246,.35);box-shadow:0 0 0 0 rgba(139,92,246,0)}
      50%{border-color:rgba(139,92,246,.65);box-shadow:0 0 12px rgba(139,92,246,.15)}
    }
    .queue-rest .day-card:nth-child(1){animation-delay:.07s}
    .queue-rest .day-card:nth-child(2){animation-delay:.13s}
    .queue-rest .day-card:nth-child(3){animation-delay:.19s}
    .seq-num{font-size:9px;color:var(--t3);margin-bottom:2px;letter-spacing:.04em;text-transform:uppercase}
    @media(prefers-reduced-motion:reduce){
      .day-card,.day-card.next-up{animation:none}
      @keyframes border-pulse{}
    }
```

- [ ] **Step 2: Remove the old `.day-grid`, `.day-card`, `.day-card:active`, `.day-card.today`, `.day-card-day`, `.day-card-name`, `.day-card-focus`, `.today-pill` lines** (lines 155–167)

The old block to remove:
```css
    /* ── Day grid ───────────────────────────────────────────── */
    .day-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px}
    .day-card{
      background:var(--s1);border:var(--bh) solid var(--bd2);border-radius:var(--rad);padding:13px 11px;
      cursor:pointer;-webkit-tap-highlight-color:transparent;
      transition:transform 140ms var(--eo3),box-shadow 200ms ease,border-color 200ms ease;
    }
    .day-card:active{transform:scale(0.96)}
    .day-card.today{border-color:rgba(139,92,246,.35);box-shadow:0 0 14px var(--pg)}
    .day-card-day{font-size:10px;color:var(--t3);margin-bottom:2px}
    .day-card-name{font-size:14px;font-weight:700;margin-bottom:2px;letter-spacing:-.01em}
    .day-card-focus{font-size:11px;color:var(--t3);line-height:1.35}
    .today-pill{font-size:9px;background:var(--p);color:#fff;padding:1px 6px;border-radius:20px;margin-left:4px;font-weight:600;vertical-align:middle}
```

Replace with just the `.day-card-day`, `.day-card-name`, `.day-card-focus`, `.today-pill` lines kept (they're still used in card HTML):
```css
    .day-card-day{font-size:10px;color:var(--t3);margin-bottom:2px}
    .day-card-name{font-size:14px;font-weight:700;margin-bottom:2px;letter-spacing:-.01em}
    .day-card-focus{font-size:11px;color:var(--t3);line-height:1.35}
    .today-pill{font-size:9px;background:var(--p);color:#fff;padding:1px 6px;border-radius:20px;margin-left:4px;font-weight:600;vertical-align:middle}
```

- [ ] **Step 3: Commit**
```bash
git add index.html
git commit -m "style: add workout queue CSS with hero card and stagger animations"
```

---

## Task 2: CSS — Bottom sheet exercise picker

**Files:**
- Modify: `index.html` (CSS block, after `.fin` styles around line 492)

- [ ] **Step 1: Find `.fin` style block (~line 492) and add bottom sheet CSS after it**

Find:
```css
    .fin{margin-top:14px;padding-top:13px;border-top:var(--bh) solid var(--bd)}
```

Add after:
```css
    /* ── Add Exercise button ────────────────────────────────── */
    .add-ex-btn{
      width:100%;margin:12px 0 0;padding:12px;
      background:transparent;border:1.5px dashed var(--bd2);
      border-radius:var(--rad);color:var(--t3);font-size:13px;font-weight:500;
      cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;
      transition:border-color 150ms ease,color 150ms ease;
      min-height:44px;
    }
    .add-ex-btn:active{transform:scale(0.97);border-color:var(--p);color:var(--p)}
    @media(hover:hover){.add-ex-btn:hover{border-color:var(--p);color:var(--p)}}
    /* ── Exercise picker bottom sheet ──────────────────────── */
    #ex-picker-backdrop{
      position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:90;
      opacity:0;pointer-events:none;transition:opacity 250ms ease;
    }
    #ex-picker-backdrop.open{opacity:1;pointer-events:all}
    #ex-picker-sheet{
      position:fixed;bottom:0;left:0;right:0;
      background:var(--s1);border-radius:18px 18px 0 0;
      padding:0 0 env(safe-area-inset-bottom,16px);
      max-height:82vh;display:flex;flex-direction:column;
      z-index:91;
      transform:translateY(100%);
      transition:transform 0.32s cubic-bezier(0.16,1,0.3,1);
    }
    #ex-picker-sheet.open{transform:translateY(0)}
    .sheet-handle{width:36px;height:4px;background:var(--bd2);border-radius:2px;margin:10px auto 0;flex-shrink:0}
    .sheet-title{font-size:13px;font-weight:700;padding:10px 16px 6px;flex-shrink:0;color:var(--t2)}
    #ex-search{
      margin:0 16px 8px;padding:9px 12px;border-radius:8px;
      background:var(--s2);border:var(--bh) solid var(--bd2);
      color:var(--t1);font-size:16px;outline:none;flex-shrink:0;
    }
    #ex-picker-list{overflow-y:auto;padding:0 8px 16px;-webkit-overflow-scrolling:touch}
    .picker-group-lbl{
      font-size:10px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;
      color:var(--t3);padding:10px 8px 4px;
    }
    .picker-item{
      padding:11px 10px;border-radius:8px;cursor:pointer;display:flex;flex-direction:column;
      transition:background 120ms ease;min-height:44px;justify-content:center;
    }
    .picker-item:active{background:rgba(139,92,246,.1)}
    @media(hover:hover){.picker-item:hover{background:var(--s2)}}
    .picker-item-name{font-size:13px;font-weight:600;color:var(--t1)}
    .picker-item-meta{font-size:11px;color:var(--t3);margin-top:1px}
    .picker-item.hidden{display:none}
```

- [ ] **Step 2: Commit**
```bash
git add index.html
git commit -m "style: add bottom sheet CSS for exercise picker"
```

---

## Task 3: HTML — day-grid div update + bottom sheet injection

**Files:**
- Modify: `index.html` (~line 624 for grid div, ~line 3250 area for init injection)

- [ ] **Step 1: Replace `<div class="day-grid" id="day-grid"></div>` with queue wrapper**

Find (line ~624):
```html
      <div class="day-grid" id="day-grid"></div>
```

Replace with:
```html
      <div class="queue-hero" id="queue-hero"></div>
      <div class="queue-rest" id="queue-rest"></div>
```

- [ ] **Step 2: Add bottom sheet HTML at end of `<body>` (just before closing `</body>` tag)**

Find the last `</div>` before `</body>` or find the closing body tag and insert before it:
```html
  <!-- Exercise picker bottom sheet -->
  <div id="ex-picker-backdrop" onclick="closeExercisePicker()"></div>
  <div id="ex-picker-sheet" role="dialog" aria-modal="true" aria-label="Вибір вправи">
    <div class="sheet-handle"></div>
    <div class="sheet-title">Додати вправу</div>
    <input id="ex-search" type="search" placeholder="Пошук..." oninput="filterExercises(this.value)" autocomplete="off">
    <div id="ex-picker-list"></div>
  </div>
```

- [ ] **Step 3: Commit**
```bash
git add index.html
git commit -m "markup: add queue HTML containers and exercise picker sheet to DOM"
```

---

## Task 4: JS — `nextWorkoutId()` and rewrite `renderDayGrid()`

**Files:**
- Modify: `index.html` (JS section, around line 2097–2130)

- [ ] **Step 1: Replace `getDayId()` with `nextWorkoutId()`**

Find and replace the entire `getDayId()` function:
```js
function getDayId() {
  const today = new Date().toISOString().split('T')[0];
  if (workoutData?.override_today?.date===today) return workoutData.override_today.workout_id;
  // New schedule: Mon=upper_a, Tue=lower_a, Thu=upper_b, Fri=lower_b
  return ({1:'upper_a',2:'lower_a',4:'upper_b',5:'lower_b'})[new Date().getDay()]||null;
}
```

Replace with:
```js
function nextWorkoutId() {
  const cycle=['upper_a','lower_a','upper_b','lower_b'];
  // override_today for today → respect it
  const today=new Date().toISOString().split('T')[0];
  if(workoutData?.override_today?.date===today) return workoutData.override_today.workout_id;
  // find last non-skipped session
  const sessions=(getLogs().sessions||[]).filter(s=>!s.skipped);
  if(!sessions.length) return cycle[0];
  const last=sessions[0]; // sessions are sorted newest-first
  const idx=cycle.indexOf(last.workout_id);
  return cycle[(idx+1)%cycle.length];
}
```

- [ ] **Step 2: Rewrite `renderDayGrid()` entirely**

Find the entire `renderDayGrid()` function (lines 2103–2130) and replace with:

```js
function renderDayGrid() {
  const hero=document.getElementById('queue-hero');
  const rest=document.getElementById('queue-rest');
  if(!hero||!rest) return;
  if(!workoutData){hero.innerHTML='<p style="font-size:12px;color:var(--t3)">Завантаження…</p>';rest.innerHTML='';return;}
  const nextId=nextWorkoutId();
  const cycle=['upper_a','lower_a','upper_b','lower_b'];
  const nextIdx=cycle.indexOf(nextId);
  // Ordered: next first, then the rest in cycle order
  const ordered=[...cycle.slice(nextIdx),...cycle.slice(0,nextIdx)];
  const [first,...others]=ordered;
  const wFirst=workoutData.workouts.find(x=>x.id===first);
  if(!wFirst){hero.innerHTML='';rest.innerHTML='';return;}
  hero.innerHTML=`
    <div class="day-card next-up" onclick="startWorkout('${wFirst.id}')">
      <div class="day-card-day"><span class="today-pill">Наступне</span></div>
      <div class="day-card-name">${wFirst.name}</div>
      <div class="day-card-focus">${wFirst.focus}</div>
    </div>`;
  const seqLabels={upper_a:'1 · Upper A',lower_a:'2 · Lower A',upper_b:'3 · Upper B',lower_b:'4 · Lower B'};
  rest.innerHTML=others.map(id=>{
    const w=workoutData.workouts.find(x=>x.id===id); if(!w) return '';
    return `<div class="day-card" onclick="startWorkout('${w.id}')">
      <div class="seq-num">${seqLabels[id]||id}</div>
      <div class="day-card-name">${w.name}</div>
      <div class="day-card-focus">${w.focus}</div>
    </div>`;
  }).join('');
}
```

- [ ] **Step 3: Fix all `getDayId()` call-sites — replace with `nextWorkoutId()`**

Search for remaining `getDayId` references:
```bash
grep -n "getDayId" /Users/r.melnyk/gym-tracker/index.html
```

Replace any remaining `getDayId()` calls with `nextWorkoutId()`.

Also update `renderTodayHero()` — it uses `getDayId()` internally. Find it (~line 1308) and update similarly.

- [ ] **Step 4: Verify in browser — open app, check home page shows hero card + 3 compact cards**

- [ ] **Step 5: Commit**
```bash
git add index.html
git commit -m "feat: replace day-of-week scheduling with sequential workout queue"
```

---

## Task 5: JS — Abs exercises constant + picker population

**Files:**
- Modify: `index.html` (JS section, add before the `// ─── Home: day grid` block ~line 2095)

- [ ] **Step 1: Add `ABS_EXERCISES` constant before the home section**

Find the comment line:
```js
// ─── Home: day grid + stats ───────────────────────────────────────────────────
```

Insert before it:
```js
// ─── Abs exercises (for picker) ───────────────────────────────────────────────
const ABS_EXERCISES=[
  {id:'abs_crunch',name:'Скручування (Crunches)',type:'isolation',primary_muscles:['abs'],secondary_muscles:[],
   sets:3,reps:'15',weight_kg:0,rir:'1-2',rest_sec:60,warmup:null,jefit_url:null,
   cues:['Лягай на спину, руки за голову — не тягни шию','Скорочуй прес, підводь лопатки від підлоги','Видих при підйомі, вдих при опусканні']},
  {id:'abs_hollow',name:'Берізка (Hollow Body Hold)',type:'isolation',primary_muscles:['abs'],secondary_muscles:['hip_flexors'],
   sets:3,reps:'30с',weight_kg:0,rir:'1-2',rest_sec:60,warmup:null,jefit_url:null,
   cues:['Лягай, підніми ноги і лопатки від підлоги','Поперек ПРИТИСНУТИЙ до підлоги — це ключ','Утримуй позицію, дихай рівномірно']},
  {id:'abs_leg_raise_lying',name:'Підйом ніг лежачи',type:'isolation',primary_muscles:['abs'],secondary_muscles:['hip_flexors'],
   sets:3,reps:'12',weight_kg:0,rir:'1-2',rest_sec:60,warmup:null,jefit_url:null,
   cues:['Руки під сідницями, поперек притиснутий','Підніми прямі ноги до 90° — не відривай поперек','Повільно опускай, не торкаючись підлоги']},
  {id:'abs_leg_raise_hang',name:'Підйом ніг у висі',type:'isolation',primary_muscles:['abs'],secondary_muscles:['hip_flexors'],
   sets:3,reps:'10',weight_kg:0,rir:'1-2',rest_sec:90,warmup:null,jefit_url:null,
   cues:['Вис на перекладині, плечі активні — не провисай','Підніми ноги до прямого кута або вище','Контрольно опускай — не розгойдуйся']},
  {id:'abs_plank',name:'Планка',type:'isolation',primary_muscles:['abs'],secondary_muscles:['erectors','glutes'],
   sets:3,reps:'45с',weight_kg:0,rir:'1-2',rest_sec:60,warmup:null,jefit_url:null,
   cues:['Лікті під плечима, тіло — пряма лінія','Стискай прес і сідниці — не прогинай поперек','Дихай рівномірно, не затримуй дихання']},
];

```

- [ ] **Step 2: Add `buildPickerList()` function right after `ABS_EXERCISES`**

```js
function buildPickerList(query='') {
  const q=query.toLowerCase().trim();
  // Collect all workout exercises (flat, skip supersets sub-items already included via parent)
  const allEx=[];
  if(workoutData) for(const w of workoutData.workouts){
    for(const ex of w.exercises){
      if(ex.type==='superset') for(const sub of ex.exercises) allEx.push({...sub,_from:w.name});
      else allEx.push({...ex,_from:w.name});
    }
  }
  function rowHtml(ex){
    const meta=ex._from?ex._from:(ex.primary_muscles||[]).join(', ');
    const hidden=q&&!ex.name.toLowerCase().includes(q)?'hidden':'';
    return `<div class="picker-item ${hidden}" onclick="addExerciseToSession(${JSON.stringify(JSON.stringify(ex))})">
      <div class="picker-item-name">${ex.name}</div>
      <div class="picker-item-meta">${meta}</div>
    </div>`;
  }
  const absRows=ABS_EXERCISES.filter(e=>!q||e.name.toLowerCase().includes(q));
  const allRows=allEx.filter(e=>!q||e.name.toLowerCase().includes(q));
  let html='';
  if(absRows.length) html+=`<div class="picker-group-lbl">Прес</div>`+ABS_EXERCISES.map(rowHtml).join('');
  if(allRows.length) html+=`<div class="picker-group-lbl">Усі вправи</div>`+allEx.map(rowHtml).join('');
  if(!absRows.length&&!allRows.length) html=`<div style="padding:24px;text-align:center;color:var(--t3);font-size:13px">Нічого не знайдено</div>`;
  document.getElementById('ex-picker-list').innerHTML=html;
}
```

Note: `JSON.stringify(JSON.stringify(ex))` double-encodes so the onclick attribute receives a valid JSON string literal. The inner parse happens in `addExerciseToSession`.

- [ ] **Step 3: Commit**
```bash
git add index.html
git commit -m "feat: add ABS_EXERCISES constant and buildPickerList() for exercise picker"
```

---

## Task 6: JS — Picker open/close/filter + addExerciseToSession

**Files:**
- Modify: `index.html` (JS section, after `buildPickerList`)

- [ ] **Step 1: Add picker control functions after `buildPickerList()`**

```js
function openExercisePicker(){
  const sheet=document.getElementById('ex-picker-sheet');
  const bd=document.getElementById('ex-picker-backdrop');
  const inp=document.getElementById('ex-search');
  if(!sheet||!bd) return;
  buildPickerList();
  if(inp) inp.value='';
  bd.classList.add('open');
  // Next frame so transition fires
  requestAnimationFrame(()=>sheet.classList.add('open'));
}
function closeExercisePicker(){
  document.getElementById('ex-picker-sheet')?.classList.remove('open');
  document.getElementById('ex-picker-backdrop')?.classList.remove('open');
}
function filterExercises(q){
  buildPickerList(q);
}
function addExerciseToSession(exJson){
  closeExercisePicker();
  let ex; try{ex=JSON.parse(exJson);}catch(e){return;}
  if(!ex||!ex.id) return;
  const list=document.getElementById('ex-list'); if(!list) return;
  const n=list.querySelectorAll('.ex-card').length+1;
  const html=renderEx(ex,n);
  // Append and animate in
  const tmp=document.createElement('div');
  tmp.innerHTML=html;
  const card=tmp.firstElementChild;
  card.style.cssText='opacity:0;transform:translateY(10px);transition:opacity .25s ease,transform .25s ease';
  list.appendChild(card);
  requestAnimationFrame(()=>{card.style.opacity='1';card.style.transform='translateY(0)';});
  card.scrollIntoView({behavior:'smooth',block:'nearest'});
  // Update progress bar
  if(currentSession&&workoutData){
    const wk=workoutData.workouts.find(x=>x.id===currentSession.workout_id);
    if(wk) updateProg(wk);
  }
}
```

- [ ] **Step 2: Commit**
```bash
git add index.html
git commit -m "feat: add exercise picker open/close/filter and addExerciseToSession()"
```

---

## Task 7: JS — Add "+" button to startWorkout() template

**Files:**
- Modify: `index.html` (~line 2141–2152 inside `startWorkout()`)

- [ ] **Step 1: Update the `startWorkout()` HTML template to add the button before `.fin`**

Find inside `startWorkout()`:
```js
    <div id="ex-list"></div>
    <div class="fin">
```

Replace with:
```js
    <div id="ex-list"></div>
    <button class="add-ex-btn" onclick="openExercisePicker()" aria-label="Додати вправу">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 1v12M1 7h12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      Додати вправу
    </button>
    <div class="fin">
```

- [ ] **Step 2: Verify in browser — start a workout, confirm "Додати вправу" button appears, tap it, bottom sheet slides up, can pick exercise, it appends to list**

- [ ] **Step 3: Commit**
```bash
git add index.html
git commit -m "feat: add exercise picker button to workout session"
```

---

## Task 8: Final polish + push

**Files:**
- Modify: `index.html` (any remaining `getDayId` references, `renderTodayHero` fix)

- [ ] **Step 1: Find and fix `renderTodayHero()` — it calls `getDayId()` which no longer exists**

Find `renderTodayHero` (~line 1308):
```bash
grep -n "getDayId\|todayWorkout\|day-grid\|queue-hero\|queue-rest" /Users/r.melnyk/gym-tracker/index.html
```

Replace all remaining `getDayId()` calls with `nextWorkoutId()`.

- [ ] **Step 2: Remove `override_today` from `workout.json` since the queue no longer needs a future override for Saturday**

The override was added to show Saturday's Upper B — now the queue handles this automatically. Remove the `override_today` block from `workout.json`:
```json
"override_today": {
  "date": "2026-04-25",
  "workout_id": "upper_b"
},
```

- [ ] **Step 3: Push everything**
```bash
git push
```

- [ ] **Step 4: Verify live app at `thekrips.github.io/gym-tracker`**
  - Home page shows hero card + 3 compact cards
  - Next in sequence is highlighted with pulse
  - Starting any workout shows "+ Додати вправу" button
  - Picker opens/closes smoothly, exercises can be added

---

## Self-Review

**Spec coverage:**
- [x] Sequential queue without day-of-week — Task 4
- [x] Next workout highlighted (hero card + pulse) — Tasks 1, 4
- [x] Date assigned on tap = today — `startWorkout()` already does this, unchanged
- [x] Stagger animations — Task 1 CSS
- [x] Add exercise button at end of workout — Task 7
- [x] Bottom sheet with all exercises + abs — Tasks 2, 5, 6
- [x] Search filter — Task 6 `filterExercises()`
- [x] prefers-reduced-motion — Task 1 CSS
- [x] 44px touch targets — Task 2 CSS (`min-height:44px`)

**Gaps identified and addressed:**
- `renderTodayHero()` still calls `getDayId()` → explicitly covered in Task 8
- `override_today` in workout.json still present → cleanup in Task 8
- `buildPickerList` double-JSON stringify is a workaround for inline onclick — acceptable for this codebase pattern
