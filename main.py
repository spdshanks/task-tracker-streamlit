import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- Page config ---
st.set_page_config(page_title="Lavori in corso", layout="centered")

# --- Auto-refresh every 60 seconds ---
st_autorefresh(interval=20 * 1000, key="datarefresh")

# --- Supabase config ---
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# --- Status options ---
status_options = ["Non pronto", "In corso", "Pronto"]
status_emojis = {
    "Non pronto": "🔴",
    "In corso": "🟡",
    "Pronto": "🟢"
}

# --- Helper Functions ---
def get_tasks():
    response = supabase.table("tasks").select("*").order("id", desc=True).execute()
    return response.data

def add_task(title, description):
    supabase.table("tasks").insert({
        "title": title,
        "description": description,
        "status": "Not Ready"
    }).execute()

def update_status(task_id, new_status):
    supabase.table("tasks").update({"status": new_status}).eq("id", str(task_id)).execute()

def delete_tasks(task_ids):
    for task_id in task_ids:
        supabase.table("tasks").delete().eq("id", str(task_id)).execute()

def update_task(task_id, new_title, new_description):
    supabase.table("tasks").update({
        "title": new_title,
        "description": new_description
    }).eq("id", str(task_id)).execute()

# --- UI ---
st.title("📋 Task Tracker")

# --- Add Task Form ---
with st.form("add_task_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([3, 5, 2])
    with col1:
        title = st.text_input("Task Title")
    with col2:
        description = st.text_input("Description")
    with col3:
        submitted = st.form_submit_button("Add Task")

    if submitted:
        if title.strip():
            add_task(title, description)
            st.success("Task added!")
            st.rerun()
        else:
            st.warning("Please enter a task title.")

# --- Display Tasks and Detail Panel ---
tasks = get_tasks()
st.markdown("---")

selected_task_id = st.session_state.get("selected_task_id", None)

left_col, right_col = st.columns([9999, 1])

with left_col:
    st.markdown("### Tasks")
    header = st.columns([1, 3, 3, 5])
    header[0].markdown("**Select**")
    header[1].markdown("**Title**")
    header[2].markdown("**Status**")
    header[3].markdown("**Description**")

    for task in tasks:
        row = st.columns([1, 3, 3, 5])
        task_id = str(task["id"])
        is_selected = selected_task_id == task_id

        with row[0]:
            clicked = st.button("🔘", key=f"radio_{task_id}")
            if clicked:
                st.session_state.selected_task_id = task_id
                selected_task_id = task_id

        row[1].markdown(f"**{task['title']}**")
        row[2].markdown(f"{status_emojis.get(task['status'], '🔴')} {task['status']}")
        row[3].markdown(task['description'])

with right_col:
    if selected_task_id:
        task = next(t for t in tasks if str(t["id"]) == selected_task_id)

        st.sidebar.markdown("### 🎯 Dettagli del compito")
        st.sidebar.markdown(f"**Titolo:** `{task['title']}`")
        st.sidebar.markdown(f"**Stato:** `{task['status']}`")
        st.sidebar.markdown(f"**Descrizione:** `{task['description']}`")

        st.sidebar.markdown("---")
        st.sidebar.subheader("🔁 Cambia Stato")
        current_status = task.get("status", "")
        default_index = status_options.index(current_status) if current_status in status_options else 0
        new_status = st.sidebar.selectbox("Nuovo stato:", status_options, index=default_index, key="one_status")
        if st.sidebar.button("✅ Aggiorna Stato"):
            update_status(task["id"], new_status)
            st.success("Stato aggiornato.")
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.subheader("✏️ Modifica Compito")
        new_title = st.sidebar.text_input("Nuovo Titolo", value=task["title"], key="edit_title")
        new_description = st.sidebar.text_input("Nuova Descrizione", value=task["description"], key="edit_desc")
        if st.sidebar.button("💾 Salva Modifiche"):
            update_task(task["id"], new_title, new_description)
            st.success("Compito aggiornato.")
            st.rerun()

        st.sidebar.markdown("---")
        if st.sidebar.button("🗑️ Elimina Compito"):
            delete_tasks([task["id"]])
            st.success("Compito eliminato.")
            st.session_state.selected_task_id = None
            st.rerun()

    else:
         st.info("")
