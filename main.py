import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- Page config ---
st.set_page_config(page_title="Lavori in corso", layout="wide")

# --- Auto-refresh every 60 seconds ---
st_autorefresh(interval=60 * 1000, key="datarefresh")

# --- Supabase config ---
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)

# --- Status options in Italian ---
status_options = ["Non pronto", "In corso", "Pronto"]
status_emojis = {
    "Non pronto": "🔴",
    "In corso": "🟡",
    "Pronto": "🟢"
}

# --- Check role ---
def is_editor():
    return st.session_state.get("user_role") == "admin"

# --- Authentication ---
if "user_email" not in st.session_state:
    with st.form("login"):
        st.subheader("🔐 Accedi")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

        if login_btn:
            try:
                user = supabase.auth.sign_in_with_password({"email": email, "password": password})
                user_info = user.user
                st.session_state.user_email = user_info.email
                st.session_state.user_role = user_info.user_metadata.get("role", "viewer")
                st.success("Login effettuato")
                st.rerun()
            except Exception as e:
                st.error("Credenziali non valide")
    st.stop()

# --- Helper Functions ---
def get_tasks():
    response = supabase.table("tasks").select("*").order("id", desc=True).execute()
    return response.data

def add_task(title, description):
    supabase.table("tasks").insert({
        "title": title,
        "description": description,
        "status": "Non pronto"
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
st.title("📋 Tracker dei Compiti")

# --- Add Task Form ---
with st.form("add_task_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([3, 5, 2])
    with col1:
        title = st.text_input("Titolo Compito", placeholder="Es: Riparare i fili")
    with col2:
        description = st.text_input("Descrizione", placeholder="Es: Controlla i fili rossi e blu")
    with col3:
        submitted = st.form_submit_button("Aggiungi Compito")

    if submitted:
        if title.strip():
            add_task(title, description)
            st.success("Compito aggiunto!")
            st.rerun()
        else:
            st.warning("Inserisci un titolo valido.")

# --- Get Tasks ---
tasks = get_tasks()
st.markdown("---")

selected_task_id = st.session_state.get("selected_task_id", None)

# --- Filter by status ---
st.markdown("### 🔍 Filtro")
status_filter = st.selectbox("Filtra per stato", ["Tutti"] + status_options)

filtered_tasks = tasks
if status_filter != "Tutti":
    filtered_tasks = [task for task in tasks if task["status"] == status_filter]

# --- Layout ---
left_col, right_col = st.columns([7, 5])

with left_col:
    st.markdown("### 📄 Compiti")
    header = st.columns([1, 3, 3, 5])
    header[0].markdown("**Seleziona**")
    header[1].markdown("**Titolo**")
    header[2].markdown("**Stato**")
    header[3].markdown("**Descrizione**")

    for task in filtered_tasks:
        row = st.columns([1, 3, 3, 5])
        task_id = str(task["id"])
        is_selected = selected_task_id == task_id

        with row[0]:
            emoji = "✅" if is_selected else "⭕"
            if st.button(emoji, key=f"radio_{task_id}"):
                st.session_state.selected_task_id = task_id
                selected_task_id = task_id

        row[1].markdown(f"**{task['title']}**")
        row[2].markdown(f"{status_emojis.get(task['status'], '🔴')} {task['status']}")
        row[3].markdown(task['description'])

if selected_task_id:
    task = next(t for t in tasks if str(t["id"]) == selected_task_id)

    st.sidebar.markdown("### 🎯 Dettagli del compito")
    st.sidebar.markdown(f"**Titolo:** `{task['title']}`")
    st.sidebar.markdown(f"**Stato:** `{task['status']}`")
    st.sidebar.markdown(f"**Descrizione:** `{task['description']}`")

    if is_editor():
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
        st.sidebar.info("🔒 Solo visualizzazione. Nessuna modifica consentita.")

# --- Logout ---
if st.sidebar.button("🔓 Logout"):
    st.session_state.clear()
    st.rerun()