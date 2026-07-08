# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

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