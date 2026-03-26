"""
PawPal+ — Smart Pet Care Management System
Phase 1, Step 4: Class skeletons translated from UML
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal


Priority   = Literal["low", "medium", "high"]
Frequency  = Literal["once", "daily", "weekly"]
EnergyLevel = Literal["low", "medium", "high"]


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    description: str
    time: datetime
    duration_minutes: int
    priority: Priority
    frequency: Frequency
    is_completed: bool = False

    def mark_complete(self) -> None:
        raise NotImplementedError("TODO: implement mark_complete")

    def clone_for_date(self, target_date: date) -> "Task":
        raise NotImplementedError("TODO: implement clone_for_date")

    def __str__(self) -> str:
        raise NotImplementedError("TODO: implement __str__")


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    energy_level: EnergyLevel
    medical_notes: str
    care_preferences: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError("TODO: implement add_task")

    def get_pending_tasks(self) -> list[Task]:
        raise NotImplementedError("TODO: implement get_pending_tasks")


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, pets: list[Pet] | None = None) -> None:
        self.name = name
        self.pets: list[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError("TODO: implement add_pet")

    def get_all_tasks(self) -> list[Task]:
        raise NotImplementedError("TODO: implement get_all_tasks")


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def sort_by_time(self) -> list[Task]:
        raise NotImplementedError("TODO: implement sort_by_time")

    def check_conflicts(self) -> list[str]:
        raise NotImplementedError("TODO: implement check_conflicts")

    def handle_recurring_tasks(self, target_date: date) -> list[Task]:
        raise NotImplementedError("TODO: implement handle_recurring_tasks")

    def show_daily_plan(self, target_date: date) -> str:
        raise NotImplementedError("TODO: implement show_daily_plan")

    def explain_plan(self) -> str:
        raise NotImplementedError("TODO: implement explain_plan")