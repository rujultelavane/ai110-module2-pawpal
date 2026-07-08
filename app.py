import streamlit as st
from datetime import time
from pawpal_system import Conflict, Owner, Pet, Task, TimeWindow, Scheduler, ScheduleStatus

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Priority-aware daily scheduling for your pets.")

st.divider()

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner(id="o1", name="", email="")
if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1
if "plan" not in st.session_state:
    st.session_state.plan = []
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Owner info
# ---------------------------------------------------------------------------

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Name", value=owner.name)
with col2:
    owner_email = st.text_input("Email", value=owner.email)

if st.button("Save owner info"):
    owner.name = owner_name
    owner.email = owner_email
    st.success(f"Owner updated: {owner.name}")

st.divider()

# ---------------------------------------------------------------------------
# Add a pet  →  calls owner.add_pet()
# ---------------------------------------------------------------------------

st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name")
with col2:
    species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
with col3:
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
notes = st.text_input("Special notes (optional)")

if st.button("Add pet"):
    if pet_name.strip():
        new_pet = Pet(
            id=f"p{st.session_state.next_pet_id}",
            name=pet_name.strip(),
            species=species,
            age=int(age),
            special_notes=notes.strip(),
        )
        owner.add_pet(new_pet)
        st.session_state.next_pet_id += 1
        st.success(f"Added {new_pet.name} ({new_pet.species})")
    else:
        st.warning("Please enter a pet name.")

if owner.pets:
    st.write("**Your pets:**")
    for p in owner.pets:
        note_str = f" — {p.special_notes}" if p.special_notes else ""
        st.write(f"- {p.name} ({p.species}, age {p.age}){note_str}")

st.divider()

# ---------------------------------------------------------------------------
# Add a task  →  calls pet.add_task()
# ---------------------------------------------------------------------------

st.subheader("Add a Task")

if not owner.pets:
    st.info("Add at least one pet before adding tasks.")
else:
    pet_options = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_options)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority_label = st.selectbox("Priority", ["High (1)", "Medium (2)", "Low (3)"])

    priority_map = {"High (1)": 1, "Medium (2)": 2, "Low (3)": 3}

    use_window = st.checkbox("Set preferred time window")
    preferred_window = None
    if use_window:
        wcol1, wcol2 = st.columns(2)
        with wcol1:
            win_start = st.time_input("Window start", value=time(8, 0))
        with wcol2:
            win_end = st.time_input("Window end", value=time(10, 0))
        preferred_window = TimeWindow(start=win_start, end=win_end)

    is_recurring = st.checkbox("Recurring daily task")

    if st.button("Add task"):
        if task_title.strip():
            new_task = Task(
                id=f"t{st.session_state.next_task_id}",
                pet_id=selected_pet.id,
                title=task_title.strip(),
                duration_minutes=int(duration),
                priority=priority_map[priority_label],
                preferred_window=preferred_window,
                is_recurring=is_recurring,
            )
            selected_pet.add_task(new_task)
            st.session_state.next_task_id += 1
            st.success(f"Added '{new_task.title}' for {selected_pet.name}")
        else:
            st.warning("Please enter a task title.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**Current tasks:**")
        rows = []
        for t in all_tasks:
            window_str = (
                f"{t.preferred_window.start.strftime('%I:%M %p')} – "
                f"{t.preferred_window.end.strftime('%I:%M %p')}"
                if t.preferred_window else "Any time"
            )
            rows.append({
                "Pet": t.pet.name if t.pet else t.pet_id,
                "Task": t.title,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Window": window_str,
                "Recurring": "Yes" if t.is_recurring else "No",
            })
        st.table(rows)

st.divider()

# ---------------------------------------------------------------------------
# Generate schedule  →  calls scheduler.generate_daily_plan()
# ---------------------------------------------------------------------------

st.subheader("Generate Today's Schedule")

AVAILABLE_HOURS = [
    TimeWindow(time(7, 0), time(10, 0)),
    TimeWindow(time(12, 0), time(13, 0)),
    TimeWindow(time(17, 0), time(19, 30)),
]

if not owner.pets or not owner.get_all_tasks():
    st.info("Add at least one pet and one task before generating a schedule.")
else:
    st.caption("Available blocks: morning 7–10 AM · lunch 12–1 PM · evening 5–7:30 PM")

    col_gen, col_resolve = st.columns(2)

    with col_gen:
        if st.button("Generate schedule", use_container_width=True):
            sched = Scheduler(owner=owner, available_hours=AVAILABLE_HOURS)
            st.session_state.scheduler = sched
            st.session_state.plan = sched.generate_daily_plan()

    with col_resolve:
        resolve_disabled = not st.session_state.plan
        if st.button("Resolve conflicts", disabled=resolve_disabled,
                     use_container_width=True):
            sched = st.session_state.scheduler
            if sched:
                st.session_state.plan = sched.resolve_conflicts(
                    st.session_state.plan
                )

    plan: list = st.session_state.plan
    sched: Scheduler | None = st.session_state.scheduler

    if plan:
        # ── conflict warnings ────────────────────────────────────────────
        warnings = sched.warn_on_conflicts(plan) if sched else []
        if warnings:
            for msg in warnings:
                st.warning(msg, icon="⚠️")
        else:
            st.success(
                f"{len(plan)} task(s) scheduled with no conflicts.", icon="✅"
            )

        st.divider()

        # ── filter controls ──────────────────────────────────────────────
        st.markdown("**Filter schedule**")
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            pet_options = ["All pets"] + [p.name for p in owner.pets]
            filter_pet = st.selectbox("By pet", pet_options, key="filter_pet")
        with fcol2:
            status_options = {
                "All statuses": None,
                "Pending": ScheduleStatus.PENDING,
                "Complete": ScheduleStatus.COMPLETE,
                "Skipped": ScheduleStatus.SKIPPED,
            }
            filter_status_label = st.selectbox(
                "By status", list(status_options.keys()), key="filter_status"
            )

        filtered = sched.filter_schedule(
            plan,
            status=status_options[filter_status_label],
            pet_name=None if filter_pet == "All pets" else filter_pet,
        ) if sched else plan

        # ── schedule table ───────────────────────────────────────────────
        STATUS_ICON = {
            ScheduleStatus.PENDING: "🕐",
            ScheduleStatus.COMPLETE: "✅",
            ScheduleStatus.SKIPPED: "⏭️",
        }

        if not filtered:
            st.info("No items match the current filters.")
        else:
            rows = []
            for item in filtered:
                rows.append({
                    "Time": (
                        f"{item.start_time.strftime('%I:%M %p')} – "
                        f"{item.end_time.strftime('%I:%M %p')}"
                    ),
                    "Task": item.task.title,
                    "Pet": item.task.pet.name if item.task.pet else item.task.pet_id,
                    "Priority": f"{'★' * (4 - item.task.priority)}{'☆' * (item.task.priority - 1)}",
                    "Recurring": "↻" if item.task.is_recurring else "–",
                    "Status": f"{STATUS_ICON.get(item.status, '')} {item.status.value}",
                })
            st.table(rows)

            skipped = [r for r in rows if "⏭️" in r["Status"]]
            if skipped:
                st.caption(
                    f"{len(skipped)} task(s) skipped due to conflicts. "
                    "Click **Resolve conflicts** to automatically drop lower-priority overlaps."
                )
