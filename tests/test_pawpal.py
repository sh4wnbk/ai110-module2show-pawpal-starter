"""
PawPal+ — Unit tests
Phase 2, Step 3: Verify core scheduling behaviors with pytest.
"""

from datetime import date, datetime
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_task():
    return Task(
        description="Morning walk",
        time=datetime(2026, 3, 26, 8, 0),
        duration_minutes=30,
        priority="high",
        frequency="daily",
    )

@pytest.fixture
def sample_pet():
    return Pet(
        name="Max",
        species="dog",
        age=3,
        energy_level="high",
        medical_notes="none",
        care_preferences="prefers morning walks",
    )

@pytest.fixture
def sample_owner(sample_pet):
    owner = Owner(name="Alex")
    owner.add_pet(sample_pet)
    return owner


# ---------------------------------------------------------------------------
# Required: Task completion
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status(sample_task):
    assert sample_task.is_completed is False
    sample_task.mark_complete()
    assert sample_task.is_completed is True


# ---------------------------------------------------------------------------
# Required: Task addition
# ---------------------------------------------------------------------------

def test_add_task_increases_count(sample_pet, sample_task):
    assert len(sample_pet.tasks) == 0
    sample_pet.add_task(sample_task)
    assert len(sample_pet.tasks) == 1


# ---------------------------------------------------------------------------
# Extra: get_pending_tasks filters completed tasks
# ---------------------------------------------------------------------------

def test_get_pending_tasks_excludes_completed(sample_pet, sample_task):
    sample_pet.add_task(sample_task)
    sample_task.mark_complete()
    assert len(sample_pet.get_pending_tasks()) == 0


# ---------------------------------------------------------------------------
# Extra: clone_for_date produces a fresh incomplete task on the right date
# ---------------------------------------------------------------------------

def test_clone_for_date(sample_task):
    target = date(2026, 3, 27)
    clone = sample_task.clone_for_date(target)
    assert clone.time.date() == target
    assert clone.is_completed is False
    assert clone.description == sample_task.description


# ---------------------------------------------------------------------------
# Extra: Scheduler detects overlapping tasks
# ---------------------------------------------------------------------------

def test_check_conflicts_detects_overlap(sample_owner, sample_pet):
    sample_pet.add_task(Task(
        description="Walk",
        time=datetime(2026, 3, 26, 8, 0),
        duration_minutes=30,
        priority="high",
        frequency="once",
    ))
    sample_pet.add_task(Task(
        description="Feeding",
        time=datetime(2026, 3, 26, 8, 15),
        duration_minutes=10,
        priority="medium",
        frequency="once",
    ))
    scheduler = Scheduler(sample_owner)
    conflicts = scheduler.check_conflicts()
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]


# ---------------------------------------------------------------------------
# Added tests: sorting, recurring completion, and conflict detection
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order(sample_owner, sample_pet):
    later_task = Task(
        description="Evening play",
        time=datetime(2026, 3, 26, 18, 0),
        duration_minutes=20,
        priority="low",
        frequency="once",
    )
    earlier_task = Task(
        description="Breakfast",
        time=datetime(2026, 3, 26, 7, 30),
        duration_minutes=10,
        priority="high",
        frequency="once",
    )
    middle_task = Task(
        description="Noon walk",
        time=datetime(2026, 3, 26, 12, 0),
        duration_minutes=25,
        priority="medium",
        frequency="once",
    )

    sample_pet.add_task(later_task)
    sample_pet.add_task(earlier_task)
    sample_pet.add_task(middle_task)

    scheduler = Scheduler(sample_owner)
    sorted_tasks = scheduler.sort_by_time()

    assert [t.description for t in sorted_tasks] == [
        "Breakfast",
        "Noon walk",
        "Evening play",
    ]


def test_mark_complete_daily_returns_next_day():
    daily_task = Task(
        description="Daily medication",
        time=datetime(2026, 3, 26, 9, 0),
        duration_minutes=5,
        priority="high",
        frequency="daily",
    )
    target = date(2026, 3, 26)

    next_task = daily_task.mark_complete(target_date=target)

    assert daily_task.is_completed is True
    assert next_task is not None
    assert next_task.time.date() == date(2026, 3, 27)
    assert next_task.frequency == "daily"
    assert next_task.is_completed is False


def test_check_conflicts_flags_overlapping_tasks(sample_owner, sample_pet):
    sample_pet.add_task(Task(
        description="Long walk",
        time=datetime(2026, 3, 26, 10, 0),
        duration_minutes=45,
        priority="medium",
        frequency="once",
    ))
    sample_pet.add_task(Task(
        description="Vet call",
        time=datetime(2026, 3, 26, 10, 30),
        duration_minutes=15,
        priority="high",
        frequency="once",
    ))

    scheduler = Scheduler(sample_owner)
    conflicts = scheduler.check_conflicts()

    assert len(conflicts) >= 1