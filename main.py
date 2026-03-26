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
print("=" * 50)