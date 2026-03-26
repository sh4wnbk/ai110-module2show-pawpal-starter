"""
PawPal+ — Smart Pet Care Management System
Phase 2, Step 1: Full class implementation
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal


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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

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
            f"{self.time.strftime('%H:%M')} - {self.description} "
            f"({self.duration_minutes}m, {self.priority}, {self.frequency}, {status})"
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
        for i in range(len(tasks) - 1):
            current = tasks[i]
            nxt = tasks[i + 1]
            current_end = current.time.timestamp() + (current.duration_minutes * 60)
            if current_end > nxt.time.timestamp():
                conflicts.append(
                    f"Conflict: '{current.description}' overlaps with "
                    f"'{nxt.description}' at {nxt.time.strftime('%H:%M')}"
                )
        return conflicts

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