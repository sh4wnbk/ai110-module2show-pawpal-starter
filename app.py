import streamlit as st
from datetime import date, datetime, time
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

for key in ("owner", "pet", "saved", "json_saved"):
    if key not in st.session_state:
        st.session_state[key] = None


# Load data from data.json on app startup if it exists
if st.session_state.owner is None:
    loaded_owner = Owner.load_from_json("data.json")
    if loaded_owner is not None:
        st.session_state.owner = loaded_owner
        if loaded_owner.pets:
            st.session_state.pet = loaded_owner.pets[0]
            st.session_state.saved = True

# ---------------------------------------------------------------------------
# Owner & Pet setup
# ---------------------------------------------------------------------------

st.subheader("Owner & Pet Info")

owner_name    = st.text_input("Owner name", value="Shawn")
pet_name      = st.text_input("Pet name", value="Mochi")
species       = st.selectbox("Species", ["dog", "cat", "other"])
energy_level  = st.selectbox("Energy level", ["low", "medium", "high"], index=1)
medical_notes = st.text_input("Medical notes", value="none")
care_prefs    = st.text_input("Care preferences", value="none")

if st.button("Save owner & pet"):
    pet = Pet(
        name=pet_name,
        species=species,
        age=0,
        energy_level=energy_level,
        medical_notes=medical_notes,
        care_preferences=care_prefs,
    )
    owner = Owner(name=owner_name)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet   = pet
    st.session_state.saved = True

if st.session_state.saved:
    st.success(
        f"Active profile — Owner: **{st.session_state.owner.name}** | "
        f"Pet: **{st.session_state.pet.name}** ({st.session_state.pet.species})"
    )

if st.session_state.json_saved:
    st.info("Profile saved to data.json — data will persist across sessions.")

st.divider()

# ---------------------------------------------------------------------------
# Add tasks
# ---------------------------------------------------------------------------

st.subheader("Tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
with col5:
    task_time = st.time_input("Time", value=time(8, 0))

if st.button("Add task"):
    if st.session_state.pet is None:
        st.warning("Save an owner and pet first.")
    else:
        task = Task(
            description=task_title,
            time=datetime.combine(date.today(), task_time),
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
        )
        st.session_state.pet.add_task(task)
        st.session_state.owner.save_to_json("data.json")
        st.success(f"Added: **{task_title}** at {task_time.strftime("%I:%M %p")}")

# Task list with filter
if st.session_state.pet and st.session_state.pet.tasks:
    show_filter = st.radio(
        "Show tasks",
        ["All", "Pending only", "Completed only"],
        horizontal=True,
    )

    tasks = st.session_state.pet.tasks
    if show_filter == "Pending only":
        tasks = [t for t in tasks if not t.is_completed]
    elif show_filter == "Completed only":
        tasks = [t for t in tasks if t.is_completed]

    if tasks:
        st.dataframe(
            [
                {
                    "Task": t.description,
                    "Time": t.time.strftime("%I:%M %p"),
                    "Duration (min)": t.duration_minutes,
                    "Priority": {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}.get(t.priority, t.priority),
                    "Frequency": t.frequency,
                    "Status": "✓ done" if t.is_completed else "⏳ pending",
                }
                for t in tasks
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No tasks match the current filter.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()


st.divider()

# ---------------------------------------------------------------------------
# Find next available slot
# ---------------------------------------------------------------------------

st.subheader("Find Next Available Slot")

slot_duration = st.number_input(
    "Task duration to fit (minutes)", min_value=1, max_value=720, value=30
)
slot_date = st.date_input("Date to search", value=date.today(), key="slot_date")

if st.button("Find slot"):
    if st.session_state.owner is None:
        st.warning("Save an owner and pet first.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        slot = scheduler.find_next_slot(int(slot_duration), slot_date)
        if slot:
            st.success(
                f"Next available slot: **{slot.strftime('%I:%M %p')}** "
                f"on {slot_date.strftime('%A, %B %d')}"
            )
        else:
            st.warning(
                f"No available slot found for {int(slot_duration)} minutes "
                f"between 8:00 AM and 8:00 PM."
            )

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------

st.subheader("Build Schedule")

target_date = st.date_input("Schedule date", value=date.today())

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Save an owner and pet first.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        daily_tasks = scheduler.handle_recurring_tasks(target_date)
        daily_tasks.sort(key=lambda t: t.time)
        conflicts = scheduler.check_conflicts()
        explanation = scheduler.explain_plan(target_date)

        # Daily plan as a table
        st.markdown("### Daily Plan")
        if daily_tasks:
            st.dataframe(
                [
                    {
                        "Time": t.time.strftime("%I:%M %p"),
                        "Task": t.description,
                        "Duration (min)": t.duration_minutes,
                        "Priority": {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}.get(t.priority, t.priority),
                        "Frequency": t.frequency,
                        "Status": "✓ done" if t.is_completed else "⏳ pending",
                    }
                    for t in daily_tasks
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No tasks scheduled for this date.")

        # Conflicts
        if conflicts:
            st.markdown("### ⚠️ Scheduling Conflicts")
            for c in conflicts:
                st.warning(c)
            st.caption(
                "Tip: adjust task times or durations above to resolve conflicts."
            )
        else:
            st.success("No scheduling conflicts detected.")

        # Explanation
        st.markdown("### Plan Explanation")
        st.info(explanation)