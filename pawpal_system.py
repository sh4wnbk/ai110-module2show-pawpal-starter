"""
PawPal+ — Smart Pet Care Management System
Phase 4: Full implementation with sorting, filtering, recurring tasks, and conflict detection
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Literal
import json
import os


Priority    = Literal["low", "medium", "high"]
Frequency   = Literal["once", "daily", "weekly"]
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

    def mark_complete(self, target_date: date | None = None) -> "Task | None":
        """Mark this task as completed.

        For recurring tasks, returns the next scheduled instance.
        For once tasks, marks as complete and returns None.
        """
        self.is_completed = True

        if self.frequency == "once":
            return None

        if target_date is None:
            target_date = self.time.date()

        if self.frequency == "daily":
            next_date = target_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = target_date + timedelta(weeks=1)
        else:
            return None

        return self.clone_for_date(next_date)

    def clone_for_date(self, target_date: date) -> "Task":
        """Return a copy of this task scheduled on the target date."""
        return Task(
            description=self.description,
            time=datetime.combine(target_date, self.time.time()),
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            is_completed=False,
        )

    def __str__(self) -> str:
        """Return a human-readable summary of the task."""
        status = "done" if self.is_completed else "pending"
        return (
            f"{self.time.strftime("%I:%M %p")} - {self.description} "
            f"({self.duration_minutes}m, {self.priority}, {self.frequency}, {status})"
        )

    def to_dict(self) -> dict:
        """Convert Task to a dictionary for JSON serialization."""
        return {
            "description": self.description,
            "time": self.time.isoformat(),
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "is_completed": self.is_completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Reconstruct a Task from a dictionary."""
        return cls(
            description=data["description"],
            time=datetime.fromisoformat(data["time"]),
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            frequency=data["frequency"],
            is_completed=data.get("is_completed", False),
        )


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
        """Add a care task to this pet."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks for this pet that are not completed."""
        return [t for t in self.tasks if not t.is_completed]

    def to_dict(self) -> dict:
        """Convert Pet to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "energy_level": self.energy_level,
            "medical_notes": self.medical_notes,
            "care_preferences": self.care_preferences,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Reconstruct a Pet from a dictionary."""
        pet = cls(
            name=data["name"],
            species=data["species"],
            age=data["age"],
            energy_level=data["energy_level"],
            medical_notes=data["medical_notes"],
            care_preferences=data["care_preferences"],
        )
        pet.tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
        return pet


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, pets: list[Pet] | None = None) -> None:
        """Initialize an owner with an optional list of pets."""
        self.name = name
        self.pets: list[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's care roster."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collect and return tasks from all of the owner's pets."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def to_dict(self) -> dict:
        """Convert Owner to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Reconstruct an Owner from a dictionary."""
        owner = cls(name=data["name"])
        owner.pets = [Pet.from_dict(pet_data) for pet_data in data.get("pets", [])]
        return owner

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Serialize the Owner object (including all pets and tasks) to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner | None":
        """Reconstruct an Owner object from JSON file. Returns None if file doesn't exist."""
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, KeyError, IOError) as e:
            print(f"Error loading data from {filepath}: {e}")
            return None


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the provided owner."""
        self.owner = owner

    def sort_by_time(self) -> list[Task]:
        """Return all owner tasks sorted by scheduled time."""
        return sorted(self.owner.get_all_tasks(), key=lambda t: t.time)

    def check_conflicts(self) -> list[str]:
        """Detect overlapping tasks and return conflict descriptions."""
        conflicts: list[str] = []
        tasks = self.sort_by_time()
        for current, nxt in zip(tasks, tasks[1:]):
            current_end = current.time + timedelta(minutes=current.duration_minutes)
            if current_end > nxt.time:
                conflicts.append(
                    f"Conflict: '{current.description}' overlaps with "
                    f"'{nxt.description}' at {nxt.time.strftime("%I:%M %p")}"
                )
        return conflicts

    def filter_tasks(self, pet_name: str | None = None, is_completed: bool | None = None) -> list[Task]:
        """Filter tasks by pet name and/or completion status."""
        filtered: list[Task] = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if is_completed is not None and task.is_completed != is_completed:
                    continue
                filtered.append(task)
        return filtered

    def handle_recurring_tasks(self, target_date: date) -> list[Task]:
        """Build the list of tasks that should occur on the target date."""
        scheduled: list[Task] = []
        for task in self.owner.get_all_tasks():
            if task.frequency == "once":
                if task.time.date() == target_date:
                    scheduled.append(task)
            elif task.frequency == "daily":
                scheduled.append(task.clone_for_date(target_date))
            elif task.frequency == "weekly":
                if task.time.weekday() == target_date.weekday():
                    scheduled.append(task.clone_for_date(target_date))
        return scheduled

    def find_next_slot(self, duration_minutes: int, target_date: date) -> datetime | None:
        """Return the earliest available slot in the 08:00-20:00 window for target_date."""
        window_start = datetime.combine(target_date, datetime.min.time()).replace(hour=8)
        window_end = datetime.combine(target_date, datetime.min.time()).replace(hour=20)

        tasks = sorted(self.handle_recurring_tasks(target_date), key=lambda t: t.time)

        current_start = window_start
        for task in tasks:
            task_start = task.time
            task_end = task_start + timedelta(minutes=task.duration_minutes)

            if task_end <= window_start or task_start >= window_end:
                continue

            if task_start < window_start:
                task_start = window_start
            if task_end > window_end:
                task_end = window_end

            gap_minutes = (task_start - current_start).total_seconds() / 60
            if gap_minutes >= duration_minutes:
                return current_start

            if task_end > current_start:
                current_start = task_end

        end_gap_minutes = (window_end - current_start).total_seconds() / 60
        if end_gap_minutes >= duration_minutes:
            return current_start

        return None

    def show_daily_plan(self, target_date: date) -> str:
        """Return a formatted daily plan for the given date."""
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        tasks = [t for t in self.handle_recurring_tasks(target_date) if not t.is_completed]
        tasks.sort(key=lambda t: (t.time, priority_rank[t.priority]))

        if not tasks:
            return f"Daily plan for {target_date.isoformat()}:\nNo tasks scheduled."

        lines = [f"Daily plan for {target_date.isoformat()}:"]
        for t in tasks:
            lines.append(f"  {t}")
        return "\n".join(lines)

    def explain_plan(self, target_date: date) -> str:
        """Explain how the plan for the target date was constructed."""
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        tasks = self.handle_recurring_tasks(target_date)
        tasks.sort(key=lambda t: (t.time, priority_rank[t.priority]))

        if not tasks:
            return f"No tasks scheduled for {target_date.isoformat()}."

        pending = sum(1 for t in tasks if not t.is_completed)
        high_pri = sum(1 for t in tasks if t.priority == "high")
        recurring = sum(1 for t in tasks if t.frequency != "once")
        conflicts = self.check_conflicts()

        return (
            f"Plan explanation for {target_date.isoformat()}:\n"
            f"  - {len(tasks)} task(s) scheduled, ordered by time "
            f"(priority used to break ties).\n"
            f"  - {high_pri} high-priority task(s) included.\n"
            f"  - {recurring} recurring task(s) generated for this date.\n"
            f"  - {pending} task(s) pending.\n"
            f"  - {len(conflicts)} conflict(s) detected."
        )