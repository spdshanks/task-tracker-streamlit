import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# ---- CONNECT TO SUPABASE ----
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase = create_client(url, key)


# ---- ADD TASK ----
def add_task(title, description):
    data = {"title": title, "description": description}
    supabase.table("tasks").insert(data).execute()

# ---- GET TASKS ----
def get_tasks():
    result = supabase.table("tasks").select("*").order("created_at", desc=True).execute()
    return result.data

# ---- UI ----
st.title("📝 Task Tracker")

with st.form("task_form"):
    title = st.text_input("Title")
    description = st.text_area("Description")
    submitted = st.form_submit_button("Add Task")

    if submitted and title:
        add_task(title, description)
        st.success("✅ Task added")

# Show tasks
st.subheader("All Tasks")
tasks = get_tasks()
if tasks:
    for task in tasks:
        st.markdown(f"**{task['title']}**  \n{task['description']}  \n🕒 _{task['created_at']}_  \n---")
else:
    st.write("No tasks yet.")
