#!/usr/bin/env python3
"""
Daily AI Coach for gym-tracker.
Runs via GitHub Actions every night.

Reads: logs.json, health-data.json, daily-notes.json, workout.json
Writes: workout.json (updated program), coach-log.md (daily analysis)

Logic:
1. Double progression: hit top of rep range in all sets → +weight, reset reps
2. Health-aware: poor sleep/mood/nutrition → reduce intensity
3. Skip tracking: missed sessions affect periodization
4. Trend analysis: weight, body fat, steps
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import copy

ROOT = Path(__file__).parent.parent
TODAY = datetime.now().strftime('%Y-%m-%d')
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# ─── Load data ────────────────────────────────────────────────────────────────

def load_json(name):
    path = ROOT / name
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(name, data):
    path = ROOT / name
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved {name}")

logs_data = load_json('logs.json') or {'sessions': []}
health_raw = load_json('health-data.json')
notes_data = load_json('daily-notes.json') or {'notes': []}
workout = load_json('workout.json')

if not workout:
    print("ERROR: No workout.json found")
    sys.exit(1)

sessions = logs_data.get('sessions', [])
notes = notes_data if isinstance(notes_data, list) else notes_data.get('notes', [])

# ─── Parse health data ────────────────────────────────────────────────────────

def parse_health():
    if not health_raw or 'samples' not in health_raw:
        return {}
    steps_by_day = defaultdict(float)
    weight_by_day = {}
    fat_by_day = {}
    bmi_by_day = {}
    for s in health_raw['samples']:
        date = s['startDate'][:10]
        if s['type'] == 'stepCount':
            steps_by_day[date] += s['value']
        elif s['type'] == 'bodyMass':
            weight_by_day[date] = s['value']
        elif s['type'] == 'bodyFatPercentage':
            fat_by_day[date] = s['value']
        elif s['type'] == 'bodyMassIndex':
            bmi_by_day[date] = s['value']
    return {
        'steps': dict(steps_by_day),
        'weight': weight_by_day,
        'fat': fat_by_day,
        'bmi': bmi_by_day,
    }

health = parse_health()

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_session(date):
    """Get workout session for a date."""
    for s in sessions:
        if s['date'] == date and not s.get('skipped'):
            return s
    return None

def get_skipped(date):
    """Check if workout was skipped on date."""
    for s in sessions:
        if s['date'] == date and s.get('skipped'):
            return s
    return None

def get_note(date):
    """Get daily note for a date."""
    for n in notes:
        if n.get('date') == date:
            return n
    return None

def get_exercise_history(exercise_id, limit=10):
    """Get last N sessions that include this exercise."""
    history = []
    for s in sessions:
        if s.get('skipped'):
            continue
        for ex in s.get('exercises', []):
            if ex['exercise_id'] == exercise_id and ex.get('sets'):
                best = max(ex['sets'], key=lambda x: x['weight'] * x['reps'])
                history.append({
                    'date': s['date'],
                    'weight': best['weight'],
                    'reps': best['reps'],
                    'sets': ex['sets'],
                    'all_sets_count': len(ex['sets']),
                })
                break
    return history[:limit]

def linear_trend(values):
    """Calculate slope of linear trend."""
    n = len(values)
    if n < 3:
        return 0
    xs = list(range(n))
    mx = sum(xs) / n
    my = sum(values) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, values))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den != 0 else 0

def recent_values(data_dict, days=14):
    """Get recent values from a date->value dict."""
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    items = sorted([(d, v) for d, v in data_dict.items() if d >= cutoff])
    return items

# ─── Double Progression Engine ────────────────────────────────────────────────

# Rep ranges for each exercise type
PROGRESSION = {
    'compound': {'rep_range': (6, 10), 'increment_upper': 2.5, 'increment_lower': 5.0},
    'isolation': {'rep_range': (10, 15), 'increment': 1.0},
    'superset': {'rep_range': (10, 15), 'increment': 1.0},
}

def is_lower_body(exercise_id):
    """Check if exercise targets lower body."""
    lower_ids = {'squat', 'leg_press', 'leg_extension', 'leg_curl_a', 'leg_curl_b',
                 'leg_press_b', 'leg_press_glutes', 'hyperextension_a', 'hyperextension_weighted',
                 'calf_raise_a', 'calf_raise_b', 'romanian_deadlift', 'bulgarian_split_squat'}
    return exercise_id in lower_ids

def check_progression(exercise, workout_type='upper'):
    """
    Check if exercise should progress.
    Returns (action, details) where action is: 'increase_weight', 'increase_reps', 'hold', 'deload'
    """
    ex_id = exercise['id']
    history = get_exercise_history(ex_id, limit=5)

    if not history:
        return ('hold', 'No history yet')

    last = history[0]
    ex_type = exercise.get('type', 'isolation')
    prog = PROGRESSION.get(ex_type, PROGRESSION['isolation'])
    rep_min, rep_max = prog['rep_range']

    current_weight = exercise.get('weight_kg', 0)
    current_reps = exercise.get('reps', '8')
    try:
        target_reps = int(str(current_reps).split('-')[0])
    except ValueError:
        target_reps = 8

    # Check if all sets in last session hit top of rep range
    sets = last['sets']
    all_hit_top = all(s['reps'] >= rep_max for s in sets)
    all_hit_target = all(s['reps'] >= target_reps for s in sets)

    # Check for 2 consecutive sessions at same weight with target reps
    consecutive_at_target = 0
    for h in history:
        if h['weight'] == current_weight and all(s['reps'] >= target_reps for s in h['sets']):
            consecutive_at_target += 1
        else:
            break

    # Check for stall (3+ sessions with no rep progress)
    if len(history) >= 3:
        last3_max_reps = [max(s['reps'] for s in h['sets']) for h in history[:3]]
        if all(r == last3_max_reps[0] for r in last3_max_reps) and last3_max_reps[0] < rep_max:
            # Stalled for 3 sessions
            if len(history) >= 5 and all(max(s['reps'] for s in h['sets']) <= last3_max_reps[0] for h in history[:5]):
                return ('deload', f'Stalled at {current_weight}kg for 5+ sessions. Try -10% deload.')

    if all_hit_top:
        # Hit top of rep range in all sets → increase weight
        # But only if last session was AT the current programmed weight (avoid double-bumping)
        last_weight = last['weight']
        if last_weight < current_weight:
            # Already bumped since last session — wait for a session at new weight
            return ('hold', f'Already bumped to {current_weight}kg — waiting for session data at new weight')
        if ex_type == 'compound':
            inc = prog['increment_lower'] if is_lower_body(ex_id) else prog['increment_upper']
        else:
            inc = prog.get('increment', 1.0)
        return ('increase_weight', f'All sets hit {rep_max} reps → +{inc}kg, reset to {rep_min} reps')

    if consecutive_at_target >= 2:
        # 2+ sessions at target → try adding 1 rep
        return ('increase_reps', f'Stable at {target_reps} reps for {consecutive_at_target} sessions → try {target_reps + 1}')

    return ('hold', f'Keep at {current_weight}kg × {current_reps}')

# ─── Recovery Assessment ──────────────────────────────────────────────────────

def assess_recovery():
    """
    Assess recovery status based on daily notes and health data.
    Returns (score: 0-100, adjustments: list[str], details: str)
    """
    score = 80  # baseline
    adjustments = []
    details = []

    note_yesterday = get_note(YESTERDAY)
    note_today = get_note(TODAY)
    note = note_today or note_yesterday

    if note:
        # Sleep assessment
        sleep = note.get('sleep_h', 0)
        if sleep > 0:
            if sleep < 6:
                score -= 25
                adjustments.append('reduce_volume')
                details.append(f'Сон {sleep}h — критично мало. Зменшуємо об\'єм.')
            elif sleep < 7:
                score -= 10
                adjustments.append('reduce_intensity')
                details.append(f'Сон {sleep}h — замало для повного відновлення.')
            elif sleep >= 8:
                score += 5
                details.append(f'Сон {sleep}h — відмінно.')

        # Mood assessment
        mood = note.get('mood', 0)
        if mood == 1:
            score -= 15
            adjustments.append('reduce_intensity')
            details.append('Настрій 1/5 — зменшуємо інтенсивність.')
        elif mood == 2:
            score -= 5
            details.append('Настрій 2/5 — помірна обережність.')
        elif mood >= 4:
            score += 5

        # Energy assessment
        energy = note.get('energy', 0)
        if energy == 1:
            score -= 20
            adjustments.append('reduce_volume')
            details.append('Енергія 1/5 — тренування в полегшеному режимі.')
        elif energy == 2:
            score -= 10
            adjustments.append('reduce_intensity')
            details.append('Енергія 2/5 — обережно з вагами.')
        elif energy >= 4:
            score += 5

        # Nutrition assessment
        nutrition = note.get('nutrition', 0)
        if nutrition == 1:
            score -= 15
            adjustments.append('reduce_intensity')
            details.append('Харчування погане — не час для рекордів.')
        elif nutrition == 2:
            score -= 5
        elif nutrition >= 4:
            score += 5

        # Tags
        tags = note.get('tags', [])
        for tag in tags:
            if '🤒' in tag:
                score -= 30
                adjustments.append('skip_recommended')
                details.append('Хворієш — краще пропустити або легке тренування.')
            if '🍺' in tag:
                score -= 15
                adjustments.append('reduce_intensity')
                details.append('Алкоголь — зменшуємо навантаження.')
            if '😴' in tag:
                score -= 10
                adjustments.append('reduce_volume')
                details.append('Втомлений.')
            if '🧘' in tag:
                score -= 5
                details.append('Стрес — зосередься на техніці, не на вагах.')

    # Steps trend (low NEAT = worse recovery context)
    if health.get('steps'):
        recent_steps = recent_values(health['steps'], days=3)
        if recent_steps:
            avg_steps = sum(v for _, v in recent_steps) / len(recent_steps)
            if avg_steps < 3000:
                score -= 5
                details.append(f'Мало кроків ({int(avg_steps)}/день) — додай прогулянку для відновлення.')

    # Check days since last workout
    workout_dates = sorted([s['date'] for s in sessions if not s.get('skipped')], reverse=True)
    if workout_dates:
        days_since = (datetime.now() - datetime.strptime(workout_dates[0], '%Y-%m-%d')).days
        if days_since >= 5:
            adjustments.append('reduce_intensity')
            details.append(f'{days_since} днів без тренувань — перший сет розминковий.')
        elif days_since >= 7:
            adjustments.append('deload')
            details.append(f'{days_since} днів перерва — деload -10% на першому тренуванні.')

    return (max(0, min(100, score)), list(set(adjustments)), details)

# ─── Apply Changes ────────────────────────────────────────────────────────────

def apply_progression(workout_data):
    """Apply double progression to all exercises in workout.json."""
    changes = []
    original = copy.deepcopy(workout_data)

    for wk in workout_data['workouts']:
        for ex in wk['exercises']:
            if ex.get('type') == 'superset':
                for sub in ex.get('exercises', []):
                    action, detail = check_progression_simple(sub, wk['id'])
                    if action != 'hold':
                        changes.append(f"  {sub['name']}: {detail}")
                        apply_action(sub, action, detail, wk['id'])
            else:
                action, detail = check_progression(ex, wk['id'])
                if action != 'hold':
                    changes.append(f"  {ex['name']}: {detail}")
                    apply_action_ex(ex, action, wk['id'])

    return changes

def check_progression_simple(sub_ex, workout_id):
    """Simplified progression check for superset sub-exercises."""
    ex_id = sub_ex.get('id', '')
    history = get_exercise_history(ex_id, limit=5)
    if not history:
        return ('hold', 'No data')

    last = history[0]
    current_reps = int(str(sub_ex.get('reps', '12')).split('-')[0])
    rep_max = 15
    sets = last['sets']
    all_hit_top = all(s['reps'] >= rep_max for s in sets)

    if all_hit_top:
        last_weight = last['weight']
        current_weight = sub_ex.get('weight_kg', 0)
        if last_weight < current_weight:
            return ('hold', f'Already bumped to {current_weight}kg — waiting for session data')
        inc = 1.0
        return ('increase_weight', f'All sets hit {rep_max} reps → +{inc}kg')
    return ('hold', f'Keep current')

def apply_action(sub_ex, action, detail, workout_id):
    """Apply progression action to a superset sub-exercise."""
    if action == 'increase_weight':
        inc = 1.0
        sub_ex['weight_kg'] = round(sub_ex.get('weight_kg', 0) + inc, 1)
        try:
            sub_ex['reps'] = str(max(8, int(str(sub_ex['reps']).split('-')[0]) - 2))
        except ValueError:
            pass

def apply_action_ex(ex, action, workout_id):
    """Apply progression action to an exercise."""
    ex_type = ex.get('type', 'isolation')
    prog = PROGRESSION.get(ex_type, PROGRESSION['isolation'])
    rep_min, rep_max = prog['rep_range']

    if action == 'increase_weight':
        if ex_type == 'compound':
            inc = prog['increment_lower'] if is_lower_body(ex['id']) else prog['increment_upper']
        else:
            inc = prog.get('increment', 1.0)
        ex['weight_kg'] = round(ex.get('weight_kg', 0) + inc, 1)
        ex['reps'] = str(rep_min)

    elif action == 'increase_reps':
        try:
            current = int(str(ex['reps']).split('-')[0])
            ex['reps'] = str(min(rep_max, current + 1))
        except ValueError:
            pass

    elif action == 'deload':
        ex['weight_kg'] = round(ex.get('weight_kg', 0) * 0.9, 1)
        ex['reps'] = str(rep_min)
        ex['note'] = f"Деload після застою. Старт з меншої ваги, фокус на техніці. | {ex.get('note', '')}"

def apply_recovery_adjustments(workout_data, adjustments, recovery_score):
    """Modify today's workout based on recovery assessment."""
    adj_notes = []
    today_dow = datetime.now().weekday()  # 0=Mon
    # Find today's workout
    dow_map = {0: 'upper_a', 1: 'lower_a', 3: 'upper_b', 4: 'lower_b'}
    today_wid = dow_map.get(today_dow)

    # Check override
    override = workout_data.get('override_today')
    if override and override.get('date') == TODAY:
        today_wid = override['workout_id']

    if not today_wid:
        return adj_notes

    wk = None
    for w in workout_data['workouts']:
        if w['id'] == today_wid:
            wk = w
            break
    if not wk:
        return adj_notes

    if 'skip_recommended' in adjustments:
        adj_notes.append(f"Рекомендую пропустити тренування (recovery: {recovery_score}/100)")
        return adj_notes

    if 'deload' in adjustments:
        for ex in wk['exercises']:
            if ex.get('type') == 'superset':
                for sub in ex.get('exercises', []):
                    sub['weight_kg'] = round(sub.get('weight_kg', 0) * 0.9, 1)
            else:
                ex['weight_kg'] = round(ex.get('weight_kg', 0) * 0.9, 1)
        adj_notes.append(f"Деload -10% на всіх вправах (recovery: {recovery_score}/100)")

    elif 'reduce_volume' in adjustments:
        for ex in wk['exercises']:
            if ex.get('type') == 'superset':
                for sub in ex.get('exercises', []):
                    if sub.get('sets', 3) > 2:
                        sub['sets'] = sub['sets'] - 1
            else:
                if ex.get('sets', 3) > 2:
                    ex['sets'] = ex['sets'] - 1
        adj_notes.append(f"-1 підхід на кожній вправі (recovery: {recovery_score}/100)")

    elif 'reduce_intensity' in adjustments:
        adj_notes.append(f"Зменшено інтенсивність — не штурмуй ваги сьогодні (recovery: {recovery_score}/100)")

    return adj_notes

# ─── Health Analysis ──────────────────────────────────────────────────────────

def analyze_health():
    """Generate health insights."""
    insights = []

    # Weight trend
    if health.get('weight'):
        recent = recent_values(health['weight'], days=14)
        if len(recent) >= 5:
            vals = [v for _, v in recent]
            slope = linear_trend(vals) * 7  # per week
            latest = vals[-1]
            change = vals[-1] - vals[0]
            if abs(change) >= 0.3:
                direction = '↑' if change > 0 else '↓'
                insights.append(f"Вага {direction} {abs(change):.1f}кг за {len(vals)} днів ({slope:+.2f}кг/тижд). "
                              f"Зараз: {latest:.1f}кг.")
            else:
                insights.append(f"Вага стабільна (~{latest:.1f}кг).")

    # Fat trend
    if health.get('fat'):
        recent = recent_values(health['fat'], days=14)
        if len(recent) >= 5:
            vals = [v for _, v in recent]
            change = vals[-1] - vals[0]
            if abs(change) >= 0.3:
                direction = '↑' if change > 0 else '↓'
                status = 'покращується' if change < 0 else 'зростає — перевір калорії'
                insights.append(f"Жир {direction} {abs(change):.1f}% — композиція {status}.")

    # Steps
    if health.get('steps'):
        recent = recent_values(health['steps'], days=7)
        if recent:
            avg = sum(v for _, v in recent) / len(recent)
            if avg < 5000:
                insights.append(f"Кроки {int(avg)}/день — нижче 5k. Додай прогулянки.")
            elif avg >= 8000:
                insights.append(f"Кроки {int(avg)}/день — чудова активність.")
            else:
                insights.append(f"Кроки {int(avg)}/день. Ціль: 8k+.")

    return insights

# ─── Training Analysis ────────────────────────────────────────────────────────

def analyze_training():
    """Generate training insights."""
    insights = []

    # Session frequency
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    recent_sessions = [s for s in sessions if s['date'] >= week_ago and not s.get('skipped')]
    skipped = [s for s in sessions if s['date'] >= week_ago and s.get('skipped')]

    insights.append(f"Тренувань за тиждень: {len(recent_sessions)}/4. Пропущено: {len(skipped)}.")

    # Yesterday's session
    yesterday_session = get_session(YESTERDAY)
    if yesterday_session:
        ex_count = len(yesterday_session.get('exercises', []))
        set_count = sum(len(e.get('sets', [])) for e in yesterday_session.get('exercises', []))
        insights.append(f"Вчора: {yesterday_session.get('workout_name', '?')} — {ex_count} вправ, {set_count} підходів.")

        # Check PRs
        for ex in yesterday_session.get('exercises', []):
            history = get_exercise_history(ex['exercise_id'], limit=20)
            if len(history) >= 2:
                best_volume = max(s['weight'] * s['reps'] for h in history[1:] for s in h['sets'])
                yesterday_best = max(s['weight'] * s['reps'] for s in ex.get('sets', [{'weight': 0, 'reps': 0}]))
                if yesterday_best > best_volume:
                    insights.append(f"  🏆 PR: {ex['exercise_id']} — {yesterday_best:.0f} volume!")

    yesterday_skip = get_skipped(YESTERDAY)
    if yesterday_skip:
        insights.append(f"Вчора пропущено: {yesterday_skip.get('workout_name', '?')}.")

    return insights

# ─── Generate Coach Log ──────────────────────────────────────────────────────

def generate_log(progression_changes, recovery_score, recovery_details, recovery_adjustments, health_insights, training_insights):
    """Generate markdown coach log."""
    lines = [
        f"# Coach Log — {TODAY}",
        "",
        f"## Recovery Score: {recovery_score}/100",
        "",
    ]

    if recovery_details:
        for d in recovery_details:
            lines.append(f"- {d}")
        lines.append("")

    if recovery_adjustments:
        lines.append("### Коригування на сьогодні")
        for a in recovery_adjustments:
            lines.append(f"- ⚡ {a}")
        lines.append("")

    lines.append("## Тренувальний аналіз")
    for i in training_insights:
        lines.append(f"- {i}")
    lines.append("")

    if progression_changes:
        lines.append("## Зміни в програмі (прогресія)")
        for c in progression_changes:
            lines.append(f"- {c}")
        lines.append("")

    if health_insights:
        lines.append("## Здоров'я")
        for i in health_insights:
            lines.append(f"- {i}")
        lines.append("")

    # Note for tomorrow
    note_y = get_note(YESTERDAY)
    if note_y and note_y.get('text'):
        lines.append("## Нотатка від юзера")
        lines.append(f"> {note_y['text']}")
        lines.append("")

    lines.append(f"---\n*Generated at {datetime.now().isoformat()}*\n")

    return '\n'.join(lines)

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"=== Daily Coach — {TODAY} ===")
    print()

    # 1. Analyze training
    print("1. Training analysis...")
    training_insights = analyze_training()
    for i in training_insights:
        print(f"   {i}")

    # 2. Analyze health
    print("2. Health analysis...")
    health_insights = analyze_health()
    for i in health_insights:
        print(f"   {i}")

    # 3. Recovery assessment
    print("3. Recovery assessment...")
    recovery_score, adjustments, recovery_details = assess_recovery()
    print(f"   Score: {recovery_score}/100")
    for d in recovery_details:
        print(f"   {d}")

    # 4. Apply double progression
    print("4. Checking progression...")
    progression_changes = apply_progression(workout)
    if progression_changes:
        for c in progression_changes:
            print(f"   {c}")
    else:
        print("   No changes needed")

    # 5. Apply recovery adjustments to today's workout
    print("5. Recovery adjustments...")
    recovery_adj = apply_recovery_adjustments(workout, adjustments, recovery_score)
    if recovery_adj:
        for a in recovery_adj:
            print(f"   {a}")
    else:
        print("   No adjustments needed")

    # 6. Clean up override_today if it's past
    if workout.get('override_today'):
        override_date = workout['override_today'].get('date', '')
        if override_date < TODAY:
            del workout['override_today']
            print(f"   Removed expired override for {override_date}")

    # 7. Update version
    workout['meta']['updated'] = TODAY
    old_version = workout['meta'].get('version', '3.0')
    # Bump patch version
    parts = old_version.split('.')
    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except (ValueError, IndexError):
        parts.append('1')
    workout['meta']['version'] = '.'.join(parts)
    print(f"   Version: {old_version} → {workout['meta']['version']}")

    # 8. Save workout.json
    save_json('workout.json', workout)

    # 9. Generate and save coach log
    log_md = generate_log(progression_changes, recovery_score, recovery_details,
                          recovery_adj, health_insights, training_insights)
    with open(ROOT / 'coach-log.md', 'w', encoding='utf-8') as f:
        f.write(log_md)
    print("  Saved coach-log.md")

    # 10. Summary
    print()
    print("=== Done ===")
    has_changes = bool(progression_changes or recovery_adj or workout.get('override_today') is None)
    if has_changes:
        print("Changes were made to workout.json")
    else:
        print("No changes to program")

    return 0


if __name__ == '__main__':
    sys.exit(main())
