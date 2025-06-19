import streamlit as st
from supabase import create_client



# Set your Supabase project URL and API key
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# --- Setup status options ---
status_options = ["Not Ready", "In Progress", "Ready"]
status_emojis = {
    "Not Ready": "🔴",
    "In Progress": "🟡",
    "Ready": "🟢"
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
    st.rerun()
def delete_tasks(task_ids):
    for task_id in task_ids:
        supabase.table("tasks").delete().eq("id", str(task_id)).execute()
        st.rerun()


def update_task(task_id, new_title, new_description):
    supabase.table("tasks").update({
        "title": new_title,
        "description": new_description
    }).eq("id", task_id).execute()
    st.rerun()

# --- Page config ---
st.set_page_config(page_title="Lavori in corso", layout="centered")

from streamlit_autorefresh import st_autorefresh

# Automatically refresh every 60 seconds (60000 milliseconds)
st_autorefresh(interval=10 * 1000, key="datarefresh")

st.title("📋 Lavori in corso")

# --- Task Entry Form ---
with st.form("add_task_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([2, 3, 2])
    with col1:
        title = st.text_input("Articolo")
    with col2:
        description = st.text_input("Fornitore")
    with col3:
        submitted = st.form_submit_button("Aggiungi Articolo")

    if submitted:
        if title.strip():
            add_task(title, description)
            st.success("Task added!")
            st.rerun()
        else:
            st.warning("Perfavore Aggiungi un Articolo")

# --- Display Task Table ---
tasks = get_tasks()
selected_ids = []

if tasks:
    st.markdown("---")
    header = st.columns([1, 3, 3, 5])
    header[0].markdown("**✔️**")
    header[1].markdown("**Ariticolo**")
    header[2].markdown("**Stato**")
    header[3].markdown("**Discrizione**")

    for task in tasks:
        row = st.columns([1, 3, 3, 5])
        with row[0]:
            if st.checkbox("", key=f"check_{task['id']}"):
                selected_ids.append(task["id"])

        row[1].markdown(f"**{task['title']}**")
        row[2].markdown(f"{status_emojis.get(task['status'], '🔴')} {task['status']}")
        row[3].markdown(task['description'])

    # --- Actions on selected items ---
    if selected_ids:
        st.markdown("---")
        st.markdown(f"**Selected Task IDs:** {selected_ids}")
        col1, col2, col3 = st.columns([4, 2, 2])

        # Dropdown to choose new status
        with col1:
            new_status = st.selectbox("Change status to:", status_options, key="bulk_status")

        # Apply status
        with col2:
            if st.button("✅ Apply Status"):
                for task_id in selected_ids:
                    update_status(task_id, new_status)
                st.success("Status updated.")
                st.rerun()

        # Delete selected
        with col3:
            if st.button("🗑️ Delete Selected"):
                delete_tasks(selected_ids)
                st.success("Tasks deleted.")
                st.rerun()

        # Edit only if one selected
        if len(selected_ids) == 1:
            task_id = selected_ids[0]
            task = next(t for t in tasks if t["id"] == task_id)
            with st.expander("✏️ Modify Selected Task"):
                new_title = st.text_input("New Title", value=task["title"], key="edit_title")
                new_description = st.text_input("New Description", value=task["description"], key="edit_desc")
                if st.button("💾 Save Changes"):
                    update_task(task_id, new_title, new_description)
                    st.success("Task updated.")
                    st.rerun()
else:
    st.info("No tasks available.")
