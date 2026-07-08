from datetime import time

import pytest

from pawpal_system import (
    Owner, Pet, Scheduler, ScheduleItem, ScheduleStatus, Task, TimeWindow
)


def make_task(id="t1", pet_id="p1", title="Test task", duration=30, priority=1,
              window=None, recurring=False, recurrence=None):
    return Task(
        id=id, pet_id=pet_id, title=title,
        duration_minutes=duration, priority=priority,
        preferred_window=window,
        is_recurring=recurring, recurrence=recurrence,
    )


def make_owner_with_pets(*pets):
    owner = Owner(id="o1", name="Alice", email="alice@example.com")
    for pet in pets:
        owner.add_pet(pet)
    return owner


def make_scheduler(owner, windows=None):
    if windows is None:
        windows = [TimeWindow(time(8, 0), time(18, 0))]
    return Scheduler(owner, windows)


def test_mark_complete_changes_status():
    item = ScheduleItem(
        task=make_task(),
        start_time=time(9, 0),
        end_time=time(9, 30),
    )
    assert item.status == ScheduleStatus.PENDING
    item.mark_complete()
    assert item.status == ScheduleStatus.COMPLETE


def test_add_task_increases_pet_task_count():
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(make_task(id="t1"))
    pet.add_task(make_task(id="t2"))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# 1. Sorting correctness — schedule items come back in chronological order
# ---------------------------------------------------------------------------

def test_schedule_items_are_chronological():
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    # Three tasks with explicit preferred windows that are disjoint
    pet.add_task(make_task(id="t1", title="Lunch meds", priority=2,
                           window=TimeWindow(time(12, 0), time(13, 0))))
    pet.add_task(make_task(id="t2", title="Morning walk", priority=1,
                           window=TimeWindow(time(8, 0), time(9, 0))))
    pet.add_task(make_task(id="t3", title="Evening walk", priority=1,
                           window=TimeWindow(time(17, 0), time(18, 0))))

    owner = make_owner_with_pets(pet)
    scheduler = make_scheduler(owner)
    plan = scheduler.generate_daily_plan()

    start_minutes = [t.hour * 60 + t.minute for item in plan
                     for t in [item.start_time]]
    assert start_minutes == sorted(start_minutes), (
        f"Schedule not chronological: {[item.task.title for item in plan]}"
    )


# ---------------------------------------------------------------------------
# 2. Recurrence logic — completing a daily task registers the next occurrence
# ---------------------------------------------------------------------------

def test_complete_recurring_task_adds_next_occurrence():
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    task = make_task(id="t1", title="Daily walk", recurring=True, recurrence="daily")
    task.pet = pet
    pet.add_task(task)

    item = ScheduleItem(task=task, start_time=time(8, 0), end_time=time(8, 30))
    owner = make_owner_with_pets(pet)
    scheduler = make_scheduler(owner)

    next_task = scheduler.complete_item(item, new_task_id="t1_next")

    assert item.status == ScheduleStatus.COMPLETE
    assert next_task is not None
    assert next_task.id == "t1_next"
    assert next_task.recurrence == "daily"
    assert any(t.id == "t1_next" for t in pet.tasks)


def test_complete_nonrecurring_task_returns_none():
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    task = make_task(id="t1", title="One-off bath")
    task.pet = pet
    pet.add_task(task)

    item = ScheduleItem(task=task, start_time=time(10, 0), end_time=time(10, 30))
    owner = make_owner_with_pets(pet)
    scheduler = make_scheduler(owner)

    result = scheduler.complete_item(item, new_task_id="t1_next")

    assert item.status == ScheduleStatus.COMPLETE
    assert result is None
    assert len(pet.tasks) == 1  # no new task added


def test_next_occurrence_raises_for_nonrecurring_task():
    task = make_task(id="t1", title="One-off bath")
    with pytest.raises(ValueError, match="not a recurring task"):
        task.next_occurrence("t1_next")


# ---------------------------------------------------------------------------
# 3. Conflict detection — overlapping times are flagged
# ---------------------------------------------------------------------------

def test_detect_conflict_for_overlapping_items():
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    task_a = make_task(id="t1", title="Walk", pet_id="p1")
    task_b = make_task(id="t2", title="Bath", pet_id="p1")
    task_a.pet = task_b.pet = pet

    item_a = ScheduleItem(task=task_a, start_time=time(9, 0), end_time=time(9, 30))
    item_b = ScheduleItem(task=task_b, start_time=time(9, 15), end_time=time(9, 45))

    owner = make_owner_with_pets(pet)
    scheduler = make_scheduler(owner)
    conflicts = scheduler.detect_conflicts([item_a, item_b])

    assert len(conflicts) == 1
    assert conflicts[0].same_pet is True


def test_detect_no_conflict_for_sequential_items():
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    task_a = make_task(id="t1", title="Walk", pet_id="p1")
    task_b = make_task(id="t2", title="Bath", pet_id="p1")
    task_a.pet = task_b.pet = pet

    item_a = ScheduleItem(task=task_a, start_time=time(9, 0), end_time=time(9, 30))
    item_b = ScheduleItem(task=task_b, start_time=time(9, 30), end_time=time(10, 0))

    owner = make_owner_with_pets(pet)
    scheduler = make_scheduler(owner)
    conflicts = scheduler.detect_conflicts([item_a, item_b])

    assert conflicts == []


def test_skipped_items_excluded_from_conflict_detection():
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    task_a = make_task(id="t1", title="Walk", pet_id="p1")
    task_b = make_task(id="t2", title="Bath", pet_id="p1")
    task_a.pet = task_b.pet = pet

    item_a = ScheduleItem(task=task_a, start_time=time(9, 0), end_time=time(9, 30))
    item_b = ScheduleItem(task=task_b, start_time=time(9, 15), end_time=time(9, 45))
    item_b.mark_skipped()

    owner = make_owner_with_pets(pet)
    scheduler = make_scheduler(owner)
    conflicts = scheduler.detect_conflicts([item_a, item_b])

    assert conflicts == []


# ---------------------------------------------------------------------------
# 4. Preferred-window enforcement — task placed only within its window
# ---------------------------------------------------------------------------

def test_task_placed_within_preferred_window():
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    window = TimeWindow(time(10, 0), time(11, 0))
    pet.add_task(make_task(id="t1", title="Vet visit", duration=30, window=window))

    owner = make_owner_with_pets(pet)
    scheduler = make_scheduler(owner, windows=[TimeWindow(time(8, 0), time(18, 0))])
    plan = scheduler.generate_daily_plan()

    assert len(plan) == 1
    item = plan[0]
    assert item.start_time >= time(10, 0)
    assert item.end_time <= time(11, 0)


def test_task_dropped_when_preferred_window_outside_available():
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    # preferred window is midnight-1am, available window is 8am-6pm — no overlap
    window = TimeWindow(time(0, 0), time(1, 0))
    pet.add_task(make_task(id="t1", title="Ghost walk", duration=30, window=window))

    owner = make_owner_with_pets(pet)
    scheduler = make_scheduler(owner, windows=[TimeWindow(time(8, 0), time(18, 0))])
    plan = scheduler.generate_daily_plan()

    assert plan == []


# ---------------------------------------------------------------------------
# 5. Duplicate deduplication — add_task and add_pet ignore repeated ids
# ---------------------------------------------------------------------------

def test_add_task_ignores_duplicate_id():
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    task = make_task(id="t1")
    pet.add_task(task)
    pet.add_task(task)  # same id — should be ignored
    assert len(pet.tasks) == 1


def test_add_pet_ignores_duplicate_id():
    owner = Owner(id="o1", name="Alice", email="alice@example.com")
    pet = Pet(id="p1", name="Buddy", species="Dog", age=3)
    owner.add_pet(pet)
    owner.add_pet(pet)  # same id — should be ignored
    assert len(owner.pets) == 1
