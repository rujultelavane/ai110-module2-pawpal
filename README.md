# PawPal+ (Module 2 Project)

This is **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## 🖥️ Sample Output

============================================
        PAWPAL — Today's Schedule
============================================

  [07:00 AM – 10:00 AM]
    07:00 AM → 07:30 AM  Morning walk (Buddy)  [P1]
    08:00 AM → 08:10 AM  Feed Whiskers (small meal) (Whiskers)  [P1]
    08:10 AM → 08:20 AM  Feed Buddy (Buddy)  [P2]
    08:20 AM → 08:40 AM  Playtime with Whiskers (Whiskers)  [P3]

  [05:00 PM – 07:30 PM]
    05:00 PM → 05:45 PM  Evening walk (Buddy)  [P2]

============================================
  Total tasks scheduled: 5
============================================

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.generate_daily_plan()` | Tasks with a preferred time window are sorted before open tasks; within each group, lower priority number wins. Ties in start time inside `resolve_conflicts` are broken the same way. |
| Filter by pet | `Owner.get_tasks_by_pet(pet_name)` | Returns every unscheduled task for a single pet (case-insensitive). Pass the result directly to `generate_daily_plan(tasks=...)` to plan for one pet at a time. |
| Filter by status or pet | `Scheduler.filter_schedule(items, status, pet_name)` | Filters an existing plan by `ScheduleStatus` (PENDING / COMPLETE / SKIPPED) and/or pet name. Both parameters are optional and compose — e.g., Buddy's pending tasks only. |
| Conflict detection | `Scheduler.detect_conflicts(items)` | Returns a list of `Conflict` objects for every overlapping pair, covering same-pet and cross-pet overlaps. Each `Conflict` carries `same_pet: bool` and a `describe()` string. |
| Conflict warnings | `Scheduler.warn_on_conflicts(items)` | Lightweight alternative to `detect_conflicts` — returns `List[str]` warnings and never raises. Malformed items (e.g., `None` start time) produce a `"could not check pair"` warning instead of crashing. |
| Conflict resolution | `Scheduler.resolve_conflicts(items)` | Keeps the higher-priority item when two items overlap; the loser is marked `SKIPPED`. Pre-existing skipped items bypass placement and are appended at the end. `_find_overlap` exits early once sorted order guarantees no further overlap. |
| Recurring tasks | `Task.next_occurrence(new_id)` | Returns an identical copy of the task with a fresh id and `pet=None`. Only callable when `task.recurrence` is `"daily"` or `"weekly"`; raises `ValueError` otherwise. |
| Complete + auto-requeue | `Scheduler.complete_item(item, new_task_id)` | Marks a schedule item complete and, if the task is recurring, calls `next_occurrence` and re-registers the new copy with the pet via `pet.add_task`. Returns the new task, or `None` for one-off tasks. |

## 📸 Demo Walkthrough

### UI Features

The Streamlit app is organized into four vertical sections:

| Section | What a user can do |
|---|---|
| **Owner** | Enter a name and email, then click Save to persist them for the session |
| **Add a Pet** | Choose a species, enter age and optional notes; the pet appears in a live list below |
| **Add a Task** | Pick a pet, set a title, duration, and priority (High/Medium/Low); optionally pin the task to a preferred time window or mark it as a daily recurring task |
| **Generate Schedule** | Click **Generate schedule** to build today's plan; click **Resolve conflicts** to automatically drop lower-priority overlaps; use the pet and status dropdowns to filter the displayed results |

---

### Example Workflow

1. **Create the owner** — enter name and email, click *Save owner info*.
2. **Add pets** — add Buddy (Dog, age 3) and Whiskers (Cat, age 5, special notes: "Sensitive stomach").
3. **Add tasks** — for Buddy: *Morning walk* (30 min, High priority, 7–9 AM, daily recurring); for Whiskers: *Feed Whiskers* (10 min, High priority, 8–9 AM, daily recurring). Add a few lower-priority tasks with no preferred window.
4. **Generate the schedule** — click *Generate schedule*. The app calls `Scheduler.generate_daily_plan()`, which sorts windowed tasks before open tasks and packs them into the morning, lunch, and evening blocks chronologically.
5. **Read the conflict banner** — if any tasks overlap, each pair surfaces as a yellow `st.warning` with a plain-English description. A green `st.success` confirms a clean plan.
6. **Filter the results** — select *Buddy* in the pet dropdown to see only his tasks; select *Pending* to hide anything already completed.
7. **Resolve conflicts** — if warnings appeared, click *Resolve conflicts*. `Scheduler.resolve_conflicts()` marks lower-priority items *Skipped* and re-renders the table with `⏭️ skipped` rows. A caption at the bottom counts how many were dropped.

---

### Key Scheduler Behaviors

- **Priority-aware sorting** — `generate_daily_plan()` schedules tasks that have a `preferred_window` before open tasks, then breaks ties by priority number (1 = highest). Tasks added in any order come out chronologically.
- **Preferred-window enforcement** — a task's slot is clamped to the intersection of its preferred window and the available block. A task whose window falls entirely outside available hours is silently dropped rather than placed at the wrong time.
- **Conflict detection** — `detect_conflicts()` and `warn_on_conflicts()` check every non-skipped pair for time overlap, covering both same-pet and cross-pet collisions. `warn_on_conflicts` never raises — malformed items produce a safe warning string instead of crashing the UI.
- **Conflict resolution** — `resolve_conflicts()` keeps the higher-priority item and marks the loser `SKIPPED`. Pre-skipped items are preserved and appended unchanged.
- **Recurring task requeue** — `complete_item()` marks a schedule item complete and, for daily/weekly tasks, calls `next_occurrence()` to register a fresh copy with the pet automatically.

---

### Sample CLI Output (`python3 main.py`)

```
================================================
  1. Full schedule — sorted by start time
================================================
  07:00 AM → 07:30 AM  Morning walk (Buddy)  [P1] [pending]
  08:00 AM → 08:10 AM  Feed Whiskers (small meal) (Whiskers)  [P1] [pending]
  08:10 AM → 08:20 AM  Feed Buddy (Buddy)  [P2] [pending]
  08:20 AM → 08:40 AM  Playtime with Whiskers (Whiskers)  [P3] [pending]
  05:00 PM → 05:45 PM  Evening walk (Buddy)  [P2] [pending]

================================================
  2. Completing tasks via complete_item()
================================================
  DONE  Morning walk (Buddy)  [daily]  → next occurrence queued as [t10]
  DONE  Feed Whiskers (small meal) (Whiskers)  [daily]  → next occurrence queued as [t11]
  DONE  Feed Buddy (Buddy)  [one-off]  → no next occurrence (one-off task)
  DONE  Playtime with Whiskers (Whiskers)  [one-off]  → no next occurrence (one-off task)
  DONE  Evening walk (Buddy)  [weekly]  → next occurrence queued as [t12]

================================================
  3. Filter: COMPLETE tasks only
================================================
  07:00 AM → 07:30 AM  Morning walk (Buddy)  [P1] [complete]
  08:00 AM → 08:10 AM  Feed Whiskers (small meal) (Whiskers)  [P1] [complete]
  08:10 AM → 08:20 AM  Feed Buddy (Buddy)  [P2] [complete]
  08:20 AM → 08:40 AM  Playtime with Whiskers (Whiskers)  [P3] [complete]
  05:00 PM → 05:45 PM  Evening walk (Buddy)  [P2] [complete]

================================================
  5. warn_on_conflicts on the generated plan
================================================
  No conflicts — scheduler placed all tasks without overlap.

================================================
  6. Two tasks at the same time — conflict warnings expected
================================================
  Schedule submitted:
    07:00 AM → 07:30 AM  Morning walk (Buddy)
    07:00 AM → 07:30 AM  Brush Buddy (Buddy)
    07:15 AM → 07:45 AM  Feed Whiskers (Whiskers)
    08:00 AM → 08:10 AM  Whiskers nap check (Whiskers)

  WARNING (same pet): 'Morning walk' and 'Brush Buddy' overlap
  WARNING (different pets): 'Morning walk' and 'Feed Whiskers' overlap
  WARNING (different pets): 'Brush Buddy' and 'Feed Whiskers' overlap
```

## Testing PawPal+
The command to run tests is `python -m pytest`.

The tests cover these behaviors:
- Sorting
- Recurrence
- Conflict detection
- Preferred window
- Deduplication

Successful test run should output:
```
============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0 -- /Library/Frameworks/Python.framework/Versions/3.13/bin/python3
cachedir: .pytest_cache
rootdir: /Users/rujultelavane/Documents/AI110/ai110-module2-pawpal
plugins: anyio-4.13.0
collecting ... collected 13 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  7%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 15%]
tests/test_pawpal.py::test_schedule_items_are_chronological PASSED       [ 23%]
tests/test_pawpal.py::test_complete_recurring_task_adds_next_occurrence PASSED [ 30%]
tests/test_pawpal.py::test_complete_nonrecurring_task_returns_none PASSED [ 38%]
tests/test_pawpal.py::test_next_occurrence_raises_for_nonrecurring_task PASSED [ 46%]
tests/test_pawpal.py::test_detect_conflict_for_overlapping_items PASSED  [ 53%]
tests/test_pawpal.py::test_detect_no_conflict_for_sequential_items PASSED [ 61%]
tests/test_pawpal.py::test_skipped_items_excluded_from_conflict_detection PASSED [ 69%]
tests/test_pawpal.py::test_task_placed_within_preferred_window PASSED    [ 76%]
tests/test_pawpal.py::test_task_dropped_when_preferred_window_outside_available PASSED [ 84%]
tests/test_pawpal.py::test_add_task_ignores_duplicate_id PASSED          [ 92%]
tests/test_pawpal.py::test_add_pet_ignores_duplicate_id PASSED           [100%]

============================== 13 passed in 0.02s ==============================
```

Confidence level: 4