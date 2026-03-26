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