from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import time
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_minutes(t: time) -> int:
    """Convert a time object to minutes since midnight."""
    return t.hour * 60 + t.minute


def _to_time(minutes: int) -> time:
    """Convert minutes since midnight back to a time object."""
    return time(minutes // 60, minutes % 60)


# ---------------------------------------------------------------------------
# Value types
# ---------------------------------------------------------------------------

@dataclass
class TimeWindow:
    start: time
    end: time

    def duration_minutes(self) -> int:
        """Return the length of this window in minutes."""
        return _to_minutes(self.end) - _to_minutes(self.start)

    def overlaps(self, other: TimeWindow) -> bool:
        """Return True if this window shares any time with other."""
        return _to_minutes(self.start) < _to_minutes(other.end) and \
               _to_minutes(other.start) < _to_minutes(self.end)


class ScheduleStatus(Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    SKIPPED = "skipped"


# ---------------------------------------------------------------------------
# Core domain classes
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    id: str
    name: str
    species: str
    age: int
    special_notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def update_profile(
        self,
        name: str,
        species: str,
        age: int,
        special_notes: str,
    ) -> None:
        """Replace all mutable profile fields in one call."""
        self.name = name
        self.species = species
        self.age = age
        self.special_notes = special_notes

    def add_task(self, task: Task) -> None:
        """Append task to this pet, ignoring duplicates by id."""
        if not any(t.id == task.id for t in self.tasks):
            self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id from this pet."""
        self.tasks = [t for t in self.tasks if t.id != task_id]


@dataclass
class Task:
    id: str
    pet_id: str
    title: str
    duration_minutes: int
    priority: int               # 1 = highest priority
    preferred_window: Optional[TimeWindow] = None
    is_recurring: bool = False
    recurrence: Optional[str] = None   # "daily", "weekly", or None
    pet: Optional[Pet] = None          # attached at scheduling time

    def update_task_details(
        self,
        title: str,
        duration_minutes: int,
        priority: int,
        preferred_window: Optional[TimeWindow],
        is_recurring: bool,
        recurrence: Optional[str] = None,
    ) -> None:
        """Overwrite all editable task fields in one call."""
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.preferred_window = preferred_window
        self.is_recurring = is_recurring
        self.recurrence = recurrence

    def next_occurrence(self, new_id: str) -> "Task":
        """Return a fresh, unscheduled copy of this task for its next recurrence cycle.

        Raises ValueError if this task has no recurrence set.
        """
        if self.recurrence is None:
            raise ValueError(f"Task '{self.title}' is not a recurring task.")
        return replace(self, id=new_id, pet=None)


@dataclass
class ScheduleItem:
    task: Task
    start_time: time
    end_time: time
    status: ScheduleStatus = ScheduleStatus.PENDING

    def mark_complete(self) -> None:
        """Mark this item as successfully completed."""
        self.status = ScheduleStatus.COMPLETE

    def mark_skipped(self) -> None:
        """Mark this item as intentionally skipped."""
        self.status = ScheduleStatus.SKIPPED


@dataclass
class Conflict:
    item_a: ScheduleItem
    item_b: ScheduleItem
    same_pet: bool   # True when both tasks belong to the same pet

    def describe(self) -> str:
        """Return a human-readable summary of the conflict."""
        a, b = self.item_a, self.item_b
        who = "same pet" if self.same_pet else "different pets"
        return (
            f"CONFLICT ({who}): "
            f"'{a.task.title}' ({a.start_time.strftime('%I:%M %p')}–{a.end_time.strftime('%I:%M %p')}) "
            f"overlaps "
            f"'{b.task.title}' ({b.start_time.strftime('%I:%M %p')}–{b.end_time.strftime('%I:%M %p')})"
        )


@dataclass
class Owner:
    id: str
    name: str
    email: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, ignoring duplicates by id."""
        if not any(p.id == pet.id for p in self.pets):
            self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove the pet with the given id from this owner."""
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of every task across all pets, with pet references attached."""
        tasks: List[Task] = []
        for pet in self.pets:
            for task in pet.tasks:
                task.pet = pet
            tasks.extend(pet.tasks)
        return tasks

    def get_tasks_by_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks for the pet matching pet_name (case-insensitive); empty list if not found."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                for task in pet.tasks:
                    task.pet = pet
                return list(pet.tasks)
        return []


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner, available_hours: List[TimeWindow]) -> None:
        self.owner = owner
        self.available_hours = available_hours

    def generate_daily_plan(
        self, tasks: Optional[List[Task]] = None
    ) -> List[ScheduleItem]:
        """Build a conflict-free schedule from tasks, defaulting to all owner tasks."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()

        pet_lookup: Dict[str, Pet] = {p.id: p for p in self.owner.pets}
        for task in tasks:
            if task.pet is None:
                task.pet = pet_lookup.get(task.pet_id)

        # Tasks with a preferred_window are scheduled first; ties broken by priority
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (t.preferred_window is None, t.priority),
        )

        # Each window tracks its current fill cursor (minutes from midnight)
        cursors: List[int] = [_to_minutes(w.start) for w in self.available_hours]

        schedule: List[ScheduleItem] = []
        for task in sorted_tasks:
            item = self._place_task(task, cursors)
            if item is not None:
                schedule.append(item)

        return schedule

    def _place_task(
        self, task: Task, cursors: List[int]
    ) -> Optional[ScheduleItem]:
        """Find the first available slot for task; mutate cursors on success."""
        for i, window in enumerate(self.available_hours):
            win_end = _to_minutes(window.end)
            start = max(cursors[i], _to_minutes(window.start))

            if task.preferred_window is not None:
                pref_start = _to_minutes(task.preferred_window.start)
                pref_end = _to_minutes(task.preferred_window.end)
                start = max(start, pref_start)
                slot_end = min(win_end, pref_end)
            else:
                slot_end = win_end

            if start + task.duration_minutes > slot_end:
                continue

            end = start + task.duration_minutes
            cursors[i] = end
            return ScheduleItem(
                task=task,
                start_time=_to_time(start),
                end_time=_to_time(end),
            )

        return None  # no slot found across any window

    def filter_schedule(
        self,
        items: List[ScheduleItem],
        status: Optional[ScheduleStatus] = None,
        pet_name: Optional[str] = None,
    ) -> List[ScheduleItem]:
        """Return schedule items matching status and/or pet_name; both filters are optional and combinable."""
        result = items
        if status is not None:
            result = [item for item in result if item.status == status]
        if pet_name is not None:
            result = [
                item for item in result
                if item.task.pet is not None
                and item.task.pet.name.lower() == pet_name.lower()
            ]
        return result

    def detect_conflicts(self, items: List[ScheduleItem]) -> List[Conflict]:
        """Return every pair of non-skipped items whose time windows overlap.

        Checks both same-pet and cross-pet overlaps — an owner cannot perform
        two tasks simultaneously regardless of which pet they belong to.
        """
        active = [i for i in items if i.status != ScheduleStatus.SKIPPED]
        conflicts: List[Conflict] = []
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                a, b = active[i], active[j]
                if _to_minutes(a.start_time) < _to_minutes(b.end_time) and \
                   _to_minutes(b.start_time) < _to_minutes(a.end_time):
                    conflicts.append(Conflict(
                        item_a=a,
                        item_b=b,
                        same_pet=a.task.pet_id == b.task.pet_id,
                    ))
        return conflicts

    def warn_on_conflicts(self, items: List[ScheduleItem]) -> List[str]:
        """Return human-readable warning strings for every detected conflict.

        Never raises — malformed items produce a 'could not check' warning
        instead of crashing the caller.
        """
        warnings: List[str] = []
        active = [i for i in items if i.status != ScheduleStatus.SKIPPED]
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                a, b = active[i], active[j]
                try:
                    if _to_minutes(a.start_time) < _to_minutes(b.end_time) and \
                       _to_minutes(b.start_time) < _to_minutes(a.end_time):
                        same_pet = a.task.pet_id == b.task.pet_id
                        who = "same pet" if same_pet else "different pets"
                        warnings.append(
                            f"WARNING ({who}): '{a.task.title}' and '{b.task.title}' overlap"
                        )
                except Exception as exc:
                    warnings.append(
                        f"WARNING: could not check pair "
                        f"(item {i}, item {j}) — {exc}"
                    )
        return warnings

    def complete_item(self, item: ScheduleItem, new_task_id: str) -> Optional[Task]:
        """Mark item complete and, if recurring, register the next occurrence with the pet.

        Returns the newly created Task for daily/weekly tasks, or None for one-off tasks.
        """
        item.mark_complete()
        task = item.task
        if task.recurrence is None:
            return None
        next_task = task.next_occurrence(new_task_id)
        if task.pet is not None:
            task.pet.add_task(next_task)
        return next_task

    def resolve_conflicts(self, items: List[ScheduleItem]) -> List[ScheduleItem]:
        """Keep the higher-priority item when two items overlap; losers are marked SKIPPED."""
        # Pre-skipped items bypass placement logic and are reunited at the end.
        pending = [i for i in items if i.status != ScheduleStatus.SKIPPED]
        already_skipped = [i for i in items if i.status == ScheduleStatus.SKIPPED]

        ordered = sorted(
            pending,
            key=lambda s: (_to_minutes(s.start_time), s.task.priority),
        )

        accepted: List[ScheduleItem] = []
        for candidate in ordered:
            overlap = self._find_overlap(candidate, accepted)
            if overlap is not None:
                if candidate.task.priority < overlap.task.priority:
                    overlap.mark_skipped()   # incoming wins
                else:
                    candidate.mark_skipped() # existing wins
            accepted.append(candidate)

        return accepted + already_skipped

    def _find_overlap(
        self, candidate: ScheduleItem, scheduled: List[ScheduleItem]
    ) -> Optional[ScheduleItem]:
        """Return the first non-skipped item in scheduled that overlaps candidate, or None."""
        c_start = _to_minutes(candidate.start_time)
        c_end = _to_minutes(candidate.end_time)
        for existing in scheduled:
            if existing.status == ScheduleStatus.SKIPPED:
                continue
            if _to_minutes(existing.start_time) >= c_end:
                break  # accepted is start-time sorted; nothing later can overlap
            if c_start < _to_minutes(existing.end_time):
                return existing
        return None
