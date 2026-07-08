from datetime import time

from pawpal_system import Conflict, Owner, Pet, Scheduler, ScheduleItem, ScheduleStatus, Task, TimeWindow

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

owner = Owner(id="o1", name="Alex Rivera", email="alex@pawpal.com")

buddy = Pet(id="p1", name="Buddy", species="Dog", age=3)
whiskers = Pet(id="p2", name="Whiskers", species="Cat", age=5,
               special_notes="Sensitive stomach — small meals only")

owner.add_pet(buddy)
owner.add_pet(whiskers)

# Tasks added deliberately out of order:
# low priority first, later windows before earlier ones, mixed pets

whiskers.add_task(Task(          # low priority, no window, non-recurring
    id="t5", pet_id="p2",
    title="Playtime with Whiskers",
    duration_minutes=20,
    priority=3,
))
buddy.add_task(Task(             # medium priority, evening window, weekly recurring
    id="t3", pet_id="p1",
    title="Evening walk",
    duration_minutes=45,
    priority=2,
    preferred_window=TimeWindow(time(17, 0), time(19, 0)),
    recurrence="weekly",
))
buddy.add_task(Task(             # medium priority, mid-morning window, non-recurring
    id="t2", pet_id="p1",
    title="Feed Buddy",
    duration_minutes=10,
    priority=2,
    preferred_window=TimeWindow(time(7, 30), time(8, 30)),
))
whiskers.add_task(Task(          # high priority, morning window, daily recurring
    id="t4", pet_id="p2",
    title="Feed Whiskers (small meal)",
    duration_minutes=10,
    priority=1,
    preferred_window=TimeWindow(time(8, 0), time(9, 0)),
    recurrence="daily",
))
buddy.add_task(Task(             # high priority, earliest window, daily recurring — added last
    id="t1", pet_id="p1",
    title="Morning walk",
    duration_minutes=30,
    priority=1,
    preferred_window=TimeWindow(time(7, 0), time(9, 0)),
    recurrence="daily",
))

# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

available_hours = [
    TimeWindow(time(7, 0), time(10, 0)),    # morning block
    TimeWindow(time(12, 0), time(13, 0)),   # lunch block
    TimeWindow(time(17, 0), time(19, 30)),  # evening block
]

scheduler = Scheduler(owner=owner, available_hours=available_hours)
plan = scheduler.generate_daily_plan()

# ---------------------------------------------------------------------------
# 1. Full schedule — sorted by start time
# ---------------------------------------------------------------------------

def _print_items(items, label):
    print(f"\n{'=' * 48}")
    print(f"  {label}")
    print(f"{'=' * 48}")
    if not items:
        print("  (none)")
        return
    for item in sorted(items, key=lambda s: s.start_time):
        pet_name = item.task.pet.name if item.task.pet else "Unknown"
        start = item.start_time.strftime("%I:%M %p")
        end   = item.end_time.strftime("%I:%M %p")
        prio  = item.task.priority
        status = item.status.value
        print(f"  {start} → {end}  {item.task.title} ({pet_name})  [P{prio}] [{status}]")


_print_items(plan, "1. Full schedule — sorted by start time")

# ---------------------------------------------------------------------------
# 2. Complete recurring tasks via complete_item; check next occurrence created
# ---------------------------------------------------------------------------

def _print_pet_tasks(pet, label):
    print(f"\n{'=' * 48}")
    print(f"  {label}")
    print(f"{'=' * 48}")
    for t in pet.tasks:
        recur = f"[{t.recurrence}]" if t.recurrence else "[one-off]"
        window = (
            f"{t.preferred_window.start.strftime('%I:%M %p')} – "
            f"{t.preferred_window.end.strftime('%I:%M %p')}"
            if t.preferred_window else "Any time"
        )
        print(f"  [{t.id}]  {t.title}  {t.duration_minutes} min  P{t.priority}  {window}  {recur}")


sorted_plan = sorted(plan, key=lambda s: s.start_time)

# Track an id counter so new task ids don't collide
next_id_counter = 10

print(f"\n{'=' * 48}")
print("  2. Completing tasks via complete_item()")
print(f"{'=' * 48}")

for item in sorted_plan:
    new_id = f"t{next_id_counter}"
    next_task = scheduler.complete_item(item, new_task_id=new_id)
    recur_label = f"[{item.task.recurrence}]" if item.task.recurrence else "[one-off]"
    if next_task:
        print(f"  DONE  {item.task.title} ({item.task.pet.name})  {recur_label}"
              f"  → next occurrence queued as [{next_task.id}]")
        next_id_counter += 1
    else:
        print(f"  DONE  {item.task.title} ({item.task.pet.name})  {recur_label}"
              f"  → no next occurrence (one-off task)")

# ---------------------------------------------------------------------------
# 3. Filter by status — all should now be COMPLETE
# ---------------------------------------------------------------------------

completed = scheduler.filter_schedule(plan, status=ScheduleStatus.COMPLETE)
_print_items(completed, "3. Filter: COMPLETE tasks only")

# ---------------------------------------------------------------------------
# 4. Show pet task lists — recurring tasks now have a queued next occurrence
# ---------------------------------------------------------------------------

_print_pet_tasks(buddy, "4. Buddy's task list after completion (new occurrences queued)")
_print_pet_tasks(whiskers, "4. Whiskers' task list after completion (new occurrences queued)")

print(f"\n{'=' * 48}")
print(f"  Total scheduled this run: {len(plan)} tasks")
print(f"{'=' * 48}\n")

# ---------------------------------------------------------------------------
# 5. detect_conflicts — conflict-free plan (scheduler never overlaps)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 5. Conflict detection — generated plan (should be clean)
# ---------------------------------------------------------------------------

print(f"\n{'=' * 48}")
print("  5. warn_on_conflicts on the generated plan")
print(f"{'=' * 48}")
warnings = scheduler.warn_on_conflicts(plan)
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts — scheduler placed all tasks without overlap.")

# ---------------------------------------------------------------------------
# 6. Conflict detection — two tasks manually placed at the same time
# ---------------------------------------------------------------------------
# The greedy scheduler prevents overlaps automatically, so we construct
# a pair of ScheduleItems at overlapping times to verify warn_on_conflicts
# catches them correctly.

print(f"\n{'=' * 48}")
print("  6. Two tasks at the same time — conflict warnings expected")
print(f"{'=' * 48}")

# Same pet, exact same slot (07:00–07:30)
walk  = ScheduleItem(
    task=Task(id="c1", pet_id="p1", title="Morning walk",  duration_minutes=30, priority=1, pet=buddy),
    start_time=time(7, 0), end_time=time(7, 30),
)
brush = ScheduleItem(
    task=Task(id="c2", pet_id="p1", title="Brush Buddy",   duration_minutes=30, priority=2, pet=buddy),
    start_time=time(7, 0), end_time=time(7, 30),
)
# Different pet, partially overlapping (07:15–07:45 cuts into the walk)
feed  = ScheduleItem(
    task=Task(id="c3", pet_id="p2", title="Feed Whiskers", duration_minutes=30, priority=1, pet=whiskers),
    start_time=time(7, 15), end_time=time(7, 45),
)
# No overlap — safe task after all the above
nap   = ScheduleItem(
    task=Task(id="c4", pet_id="p2", title="Whiskers nap check", duration_minutes=10, priority=3, pet=whiskers),
    start_time=time(8, 0), end_time=time(8, 10),
)

simultaneous = [walk, brush, feed, nap]

print("  Schedule submitted:")
for item in simultaneous:
    pet_name = item.task.pet.name if item.task.pet else "Unknown"
    print(f"    {item.start_time.strftime('%I:%M %p')} → {item.end_time.strftime('%I:%M %p')}"
          f"  {item.task.title} ({pet_name})")

print()
for w in scheduler.warn_on_conflicts(simultaneous):
    print(f"  {w}")
