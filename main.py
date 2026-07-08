from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task, TimeWindow

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

owner = Owner(id="o1", name="Alex Rivera", email="alex@pawpal.com")

buddy = Pet(id="p1", name="Buddy", species="Dog", age=3)
whiskers = Pet(id="p2", name="Whiskers", species="Cat", age=5,
               special_notes="Sensitive stomach — small meals only")

owner.add_pet(buddy)
owner.add_pet(whiskers)

# Buddy's tasks
buddy.add_task(Task(
    id="t1", pet_id="p1",
    title="Morning walk",
    duration_minutes=30,
    priority=1,
    preferred_window=TimeWindow(time(7, 0), time(9, 0)),
))
buddy.add_task(Task(
    id="t2", pet_id="p1",
    title="Feed Buddy",
    duration_minutes=10,
    priority=2,
    preferred_window=TimeWindow(time(7, 30), time(8, 30)),
))
buddy.add_task(Task(
    id="t3", pet_id="p1",
    title="Evening walk",
    duration_minutes=45,
    priority=2,
    preferred_window=TimeWindow(time(17, 0), time(19, 0)),
))

# Whiskers' tasks
whiskers.add_task(Task(
    id="t4", pet_id="p2",
    title="Feed Whiskers (small meal)",
    duration_minutes=10,
    priority=1,
    preferred_window=TimeWindow(time(8, 0), time(9, 0)),
))
whiskers.add_task(Task(
    id="t5", pet_id="p2",
    title="Playtime with Whiskers",
    duration_minutes=20,
    priority=3,
))

# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

available_hours = [
    TimeWindow(time(7, 0), time(10, 0)),   # morning block
    TimeWindow(time(12, 0), time(13, 0)),  # lunch block
    TimeWindow(time(17, 0), time(19, 30)), # evening block
]

scheduler = Scheduler(owner=owner, available_hours=available_hours)
plan = scheduler.generate_daily_plan()

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

print("=" * 44)
print("        PAWPAL — Today's Schedule")
print("=" * 44)

if not plan:
    print("  No tasks could be scheduled today.")
else:
    current_window_label = None
    for item in sorted(plan, key=lambda s: s.start_time):
        # Print a section header when the block changes
        for window in available_hours:
            if window.start <= item.start_time < window.end:
                label = f"{window.start.strftime('%I:%M %p')} – {window.end.strftime('%I:%M %p')}"
                if label != current_window_label:
                    print(f"\n  [{label}]")
                    current_window_label = label
                break

        pet_name = item.task.pet.name if item.task.pet else "Unknown"
        start = item.start_time.strftime("%I:%M %p")
        end   = item.end_time.strftime("%I:%M %p")
        prio  = item.task.priority
        print(f"    {start} → {end}  {item.task.title} ({pet_name})  [P{prio}]")

print("\n" + "=" * 44)
print(f"  Total tasks scheduled: {len(plan)}")
print("=" * 44)
