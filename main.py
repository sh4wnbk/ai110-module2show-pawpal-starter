"""
PawPal+ — CLI demo script
Phase 2, Step 2: Verify logic in the terminal before connecting to Streamlit.
"""

from datetime import date, datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Setup — owner and pets
# ---------------------------------------------------------------------------

owner = Owner(name="Alex")

max_ = Pet(
    name="Max",
    species="dog",
    age=3,
    energy_level="high",
    medical_notes="none",
    care_preferences="prefers morning walks",
)

luna = Pet(
    name="Luna",
    species="cat",
    age=5,
    energy_level="low",
    medical_notes="thyroid medication required",
    care_preferences="quiet environment",
)

owner.add_pet(max_)
owner.add_pet(luna)

# ---------------------------------------------------------------------------
# Tasks — mix of frequencies, priorities, and pets
# ---------------------------------------------------------------------------

today = date.today()

max_.add_task(Task(
    description="Morning walk",
    time=datetime.combine(today, datetime.strptime("08:00", "%H:%M").time()),
    duration_minutes=30,
    priority="high",
    frequency="daily",
))

max_.add_task(Task(
    description="Evening walk",
    time=datetime.combine(today, datetime.strptime("17:30", "%H:%M").time()),
    duration_minutes=30,
    priority="medium",
    frequency="daily",
))

max_.add_task(Task(
    description="Grooming session",
    time=datetime.combine(today, datetime.strptime("10:00", "%H:%M").time()),
    duration_minutes=45,
    priority="low",
    frequency="weekly",
))

luna.add_task(Task(
    description="Thyroid medication",
    time=datetime.combine(today, datetime.strptime("08:15", "%H:%M").time()),
    duration_minutes=5,
    priority="high",
    frequency="daily",
))

luna.add_task(Task(
    description="Feeding",
    time=datetime.combine(today, datetime.strptime("08:00", "%H:%M").time()),
    duration_minutes=10,
    priority="medium",
    frequency="daily",
))

# ---------------------------------------------------------------------------
# Run the scheduler
# ---------------------------------------------------------------------------

scheduler = Scheduler(owner)

print("=" * 50)
print(scheduler.show_daily_plan(today))
print()
print(scheduler.explain_plan(today))

conflicts = scheduler.check_conflicts()
if conflicts:
    print()
    print("Conflicts detected:")
    for c in conflicts:
        print(f"  {c}")

# ---------------------------------------------------------------------------
# Filter tasks — by pet name and completion status
# ---------------------------------------------------------------------------

print()
print("--- Filter: Max's tasks only ---")
for t in scheduler.filter_tasks(pet_name="Max"):
    print(f"  {t}")

print()
print("--- Filter: pending tasks only ---")
for t in scheduler.filter_tasks(is_completed=False):
    print(f"  {t}")

# ---------------------------------------------------------------------------
# Recurring task next-occurrence — mark complete and get next instance
# ---------------------------------------------------------------------------

print()
print("--- Recurring task: mark complete and get next occurrence ---")
walk = max_.tasks[0]
print(f"  Before: {walk}")
next_task = walk.mark_complete(today)
print(f"  After:  {walk}")
if next_task:
    print(f"  Next:   {next_task}")

print("=" * 50)