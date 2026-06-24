from __future__ import annotations
from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import List, Optional


@dataclass
class TimeWindow:
    start: time
    end: time


class ScheduleStatus(Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    SKIPPED = "skipped"


@dataclass
class Pet:
    id: str
    name: str
    species: str
    age: int
    special_notes: str = ""

    def update_profile(
        self,
        name: str,
        species: str,
        age: int,
        special_notes: str,
    ) -> None:
        pass


@dataclass
class Task:
    id: str
    pet_id: str
    title: str
    duration_minutes: int
    priority: int
    preferred_window: Optional[TimeWindow] = None
    is_recurring: bool = False
    pet: Optional[Pet] = None

    def update_task_details(
        self,
        title: str,
        duration_minutes: int,
        priority: int,
        preferred_window: Optional[TimeWindow],
        is_recurring: bool,
    ) -> None:
        pass


@dataclass
class ScheduleItem:
    task: Task
    start_time: time
    end_time: time
    status: ScheduleStatus = ScheduleStatus.PENDING

    def mark_complete(self) -> None:
        pass

    def mark_skipped(self) -> None:
        pass


@dataclass
class Owner:
    id: str
    name: str
    email: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_id: str) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner, available_hours: List[TimeWindow]) -> None:
        self.owner = owner
        self.available_hours = available_hours

    def generate_daily_plan(self, tasks: List[Task]) -> List[ScheduleItem]:
        pass

    def resolve_conflicts(self, items: List[ScheduleItem]) -> List[ScheduleItem]:
        pass
