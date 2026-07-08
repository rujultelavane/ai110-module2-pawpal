from datetime import time

from pawpal_system import Pet, ScheduleItem, ScheduleStatus, Task, TimeWindow


def make_task(id="t1", pet_id="p1", duration=30, priority=1):
    return Task(id=id, pet_id=pet_id, title="Test task",
                duration_minutes=duration, priority=priority)


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
