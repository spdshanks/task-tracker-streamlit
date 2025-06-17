import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# ---- CONNECT TO SUPABASE ----
url = st.secrets["supabase"]["https://nzvmnsbtatptmzdawhvq.supabase.co"]
key = st.secrets["supabase"]["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im56dm1uc2J0YXRwdG16ZGF3aHZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAxMDE3MzEsImV4cCI6MjA2NTY3NzczMX0.paaBIC4choracy3ehB17JcpFFtKsXLUAmD_3y3MVbIg"]
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
