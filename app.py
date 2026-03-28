import streamlit as st
from datetime import date, datetime, time
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Step 2: Session state — initialize Owner once, persist across reruns
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None

if "pet" not in st.session_state:
    st.session_state.pet = None

# ---------------------------------------------------------------------------
# Step 1: Owner + Pet setup
# ---------------------------------------------------------------------------

st.subheader("Owner & Pet Info")

owner_name = st.text_input("Owner name", value="Shawn")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"], index=0)
energy_level = st.selectbox("Energy level", ["low", "medium", "high"], index=1)
medical_notes = st.text_input("Medical notes", value="none")
care_preferences = st.text_input("Care preferences", value="none")

if st.button("Save owner & pet"):
    pet = Pet(
        name=pet_name,
        species=species,
        age=0,
        energy_level=energy_level,
        medical_notes=medical_notes,
        care_preferences=care_preferences,
    )
    owner = Owner(name=owner_name)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.success(f"Saved {owner_name} and {pet_name}.")

st.divider()

# ---------------------------------------------------------------------------
# Step 3: Add tasks — wired to Pet.add_task()
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
        st.success(f"Added task: {task_title}")

if st.session_state.pet and st.session_state.pet.tasks:
    st.write("Current tasks:")
    st.table([
        {
            "Task": t.description,
            "Time": t.time.strftime("%H:%M"),
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority,
            "Frequency": t.frequency,
            "Status": "done" if t.is_completed else "pending",
        }
        for t in st.session_state.pet.tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Step 3: Generate schedule — wired to Scheduler
# ---------------------------------------------------------------------------

st.subheader("Build Schedule")

target_date = st.date_input("Schedule date", value=date.today())

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Save an owner and pet first.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        plan = scheduler.show_daily_plan(target_date)
        explanation = scheduler.explain_plan(target_date)
        conflicts = scheduler.check_conflicts()

        st.markdown("### Daily Plan")
        st.code(plan)

        st.markdown("### Plan Explanation")
        st.info(explanation)

        if conflicts:
            st.markdown("### Conflicts")
            for c in conflicts:
                st.warning(c)