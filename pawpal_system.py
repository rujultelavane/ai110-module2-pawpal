from __future__ import annotations
from dataclasses import dataclass
from typing import List


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
    preferred_window: str = ""
    is_recurring: bool = False

    def update_task_details(
        self,
        title: str,
        duration_minutes: int,
        priority: int,
        preferred_window: str,
        is_recurring: bool,
    ) -> None:
        pass


@dataclass
class ScheduleItem:
    task: Task
    start_time: str
    end_time: str
    status: str = "pending"

    def mark_complete(self) -> None:
        pass

    def mark_skipped(self) -> None:
        pass


class Owner:
    def __init__(self, id: str, name: str, email: str) -> None:
        self.id = id
        self.name = name
        self.email = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_id: str) -> None:
        pass


class Scheduler:
    def __init__(self, available_hours: List[str]) -> None:
        self.available_hours = available_hours

    def generate_daily_plan(self, tasks: List[Task]) -> List[ScheduleItem]:
        pass

    def resolve_conflicts(self, items: List[ScheduleItem]) -> List[ScheduleItem]:
        pass
