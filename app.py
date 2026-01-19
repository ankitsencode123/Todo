import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import uuid
from collections import defaultdict

st.set_page_config(page_title="TaskFlow Pro", layout="wide", initial_sidebar_state="expanded")

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "lists" not in st.session_state:
    st.session_state.lists = ["Personal", "Work", "Health"]
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def add_task(title, list_name, priority, due_date, description=""):
    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "list": list_name,
        "priority": priority,
        "due_date": due_date.isoformat() if due_date else None,
        "description": description,
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    st.session_state.tasks.append(task)

def toggle_task(task_id):
    for task in st.session_state.tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            task["completed_at"] = datetime.now().isoformat() if task["completed"] else None
            break

def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]

def get_completion_stats():
    total = len(st.session_state.tasks)
    completed = len([t for t in st.session_state.tasks if t["completed"]])
    return total, completed, (completed / total * 100) if total > 0 else 0

def get_tasks_by_list():
    tasks_by_list = defaultdict(lambda: {"total": 0, "completed": 0})
    for task in st.session_state.tasks:
        tasks_by_list[task["list"]]["total"] += 1
        if task["completed"]:
            tasks_by_list[task["list"]]["completed"] += 1
    return dict(tasks_by_list)

def get_priority_distribution():
    priority_dist = defaultdict(int)
    for task in st.session_state.tasks:
        if not task["completed"]:
            priority_dist[task["priority"]] += 1
    return dict(priority_dist)

def get_weekly_completion_data():
    weekly_data = defaultdict(int)
    for task in st.session_state.tasks:
        if task["completed"] and task["completed_at"]:
            completed_date = datetime.fromisoformat(task["completed_at"])
            week_start = (completed_date - timedelta(days=completed_date.weekday())).date()
            weekly_data[week_start] += 1
    return dict(sorted(weekly_data.items()))

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: transparent;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
    }
    .task-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    .task-card:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    }
    .priority-high {
        border-left: 5px solid #ff4757;
    }
    .priority-medium {
        border-left: 5px solid #ffa502;
    }
    .priority-low {
        border-left: 5px solid #1e90ff;
    }
    h1 {
        background: linear-gradient(120deg, #fff, #a8edea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("# 📊 TaskFlow Pro")
    st.markdown("---")
    
    page = st.radio("Navigation", ["📝 My Tasks", "📈 Analytics", "⚙️ Settings"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    total, completed, percentage = get_completion_stats()
    st.metric("Total Tasks", total)
    st.metric("Completed", completed)
    st.metric("Completion Rate", f"{percentage:.1f}%")
    
    st.markdown("---")
    st.markdown("### Data Management")
    
    if st.button("💾 Export Tasks", use_container_width=True):
        data = json.dumps({"tasks": st.session_state.tasks, "lists": st.session_state.lists}, indent=2)
        st.download_button("Download JSON", data, "taskflow_backup.json", "application/json", use_container_width=True)
    
    uploaded = st.file_uploader("📂 Import Tasks", type=["json"])
    if uploaded:
        try:
            data = json.load(uploaded)
            st.session_state.tasks = data.get("tasks", [])
            st.session_state.lists = data.get("lists", ["Personal", "Work", "Health"])
            st.success("✅ Tasks imported!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Import failed: {str(e)}")

if page == "📝 My Tasks":
    st.title("✨ TaskFlow Pro")
    st.markdown("### Your intelligent task management companion")
    
    col1, col2, col3 = st.columns(3)
    total, completed, percentage = get_completion_stats()
    
    with col1:
        st.metric("📋 Total Tasks", total, f"{len([t for t in st.session_state.tasks if not t['completed']])} active")
    with col2:
        st.metric("✅ Completed", completed, f"+{len([t for t in st.session_state.tasks if t['completed'] and t['completed_at'] and (datetime.now() - datetime.fromisoformat(t['completed_at'])).days < 1])} today")
    with col3:
        st.metric("🎯 Success Rate", f"{percentage:.1f}%", f"{percentage - 50:.1f}%")
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["➕ Add New Task", "📑 Task Lists"])
    
    with tab1:
        with st.form("add_task_form", clear_on_submit=True):
            st.markdown("### Create New Task")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                task_title = st.text_input("Task Title", placeholder="Enter your task...")
            with col2:
                task_list = st.selectbox("List", st.session_state.lists)
            
            col3, col4 = st.columns(2)
            with col3:
                task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            with col4:
                task_due = st.date_input("Due Date", min_value=datetime.now().date())
            
            task_desc = st.text_area("Description (optional)", placeholder="Add more details...")
            
            submitted = st.form_submit_button("🚀 Add Task", use_container_width=True)
            if submitted and task_title:
                add_task(task_title, task_list, task_priority, task_due, task_desc)
                st.success(f"✅ Task '{task_title}' added successfully!")
                st.rerun()
    
    with tab2:
        filter_list = st.selectbox("Filter by List", ["All"] + st.session_state.lists)
        filter_status = st.radio("Status", ["All", "Active", "Completed"], horizontal=True)
        filter_priority = st.multiselect("Priority", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])
        
        st.markdown("---")
        
        filtered_tasks = st.session_state.tasks
        if filter_list != "All":
            filtered_tasks = [t for t in filtered_tasks if t["list"] == filter_list]
        if filter_status == "Active":
            filtered_tasks = [t for t in filtered_tasks if not t["completed"]]
        elif filter_status == "Completed":
            filtered_tasks = [t for t in filtered_tasks if t["completed"]]
        filtered_tasks = [t for t in filtered_tasks if t["priority"] in filter_priority]
        
        filtered_tasks.sort(key=lambda x: (x["completed"], {"High": 0, "Medium": 1, "Low": 2}[x["priority"]]))
        
        if not filtered_tasks:
            st.info("🎉 No tasks found. Add your first task to get started!")
        else:
            for task in filtered_tasks:
                priority_class = f"priority-{task['priority'].lower()}"
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])
                    
                    with col1:
                        if st.checkbox("", value=task["completed"], key=f"check_{task['id']}", label_visibility="collapsed"):
                            if not task["completed"]:
                                toggle_task(task["id"])
                                st.rerun()
                        else:
                            if task["completed"]:
                                toggle_task(task["id"])
                                st.rerun()
                    
                    with col2:
                        title_style = "text-decoration: line-through; opacity: 0.6;" if task["completed"] else ""
                        st.markdown(f"<div style='{title_style}'><b>{task['title']}</b></div>", unsafe_allow_html=True)
                        if task["description"]:
                            st.caption(task["description"])
                        
                        info_parts = []
                        if task["due_date"]:
                            due = datetime.fromisoformat(task["due_date"]).date()
                            days_left = (due - datetime.now().date()).days
                            if days_left < 0:
                                info_parts.append(f"⏰ Overdue by {abs(days_left)} days")
                            elif days_left == 0:
                                info_parts.append("⏰ Due today")
                            else:
                                info_parts.append(f"📅 Due in {days_left} days")
                        info_parts.append(f"📂 {task['list']}")
                        st.caption(" • ".join(info_parts))
                    
                    with col3:
                        priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🔵"}
                        st.markdown(f"**{priority_colors[task['priority']]} {task['priority']}**")
                    
                    with col4:
                        if st.button("🗑️", key=f"del_{task['id']}", help="Delete task"):
                            delete_task(task["id"])
                            st.rerun()
                    
                    st.markdown("---")

elif page == "📈 Analytics":
    st.title("📊 Analytics Dashboard")
    st.markdown("### Deep insights into your productivity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Tasks by List")
        tasks_by_list = get_tasks_by_list()
        if tasks_by_list:
            df_lists = pd.DataFrame([
                {"List": k, "Total": v["total"], "Completed": v["completed"], "Pending": v["total"] - v["completed"]}
                for k, v in tasks_by_list.items()
            ])
            fig = px.bar(df_lists, x="List", y=["Completed", "Pending"], 
                        title="Task Distribution by List",
                        color_discrete_map={"Completed": "#2ecc71", "Pending": "#e74c3c"},
                        barmode="stack")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                            font=dict(color='white'), height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available yet. Start adding tasks!")
    
    with col2:
        st.markdown("#### 🎯 Priority Distribution")
        priority_dist = get_priority_distribution()
        if priority_dist:
            fig = go.Figure(data=[go.Pie(
                labels=list(priority_dist.keys()),
                values=list(priority_dist.values()),
                hole=0.4,
                marker=dict(colors=['#1e90ff', '#ffa502', '#ff4757'])
            )])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white'), height=350,
                            title="Active Tasks by Priority")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No active tasks to analyze.")
    
    st.markdown("---")
    
    st.markdown("#### 📈 Weekly Completion Trend")
    weekly_data = get_weekly_completion_data()
    if weekly_data:
        df_weekly = pd.DataFrame([
            {"Week": k.strftime("%Y-%m-%d"), "Completed": v}
            for k, v in weekly_data.items()
        ])
        fig = px.line(df_weekly, x="Week", y="Completed", 
                     title="Tasks Completed Per Week",
                     markers=True)
        fig.update_traces(line=dict(color='#2ecc71', width=3), marker=dict(size=10))
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'), height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Complete some tasks to see your weekly progress!")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    overdue = [t for t in st.session_state.tasks if not t["completed"] and t["due_date"] and 
               datetime.fromisoformat(t["due_date"]).date() < datetime.now().date()]
    due_today = [t for t in st.session_state.tasks if not t["completed"] and t["due_date"] and 
                 datetime.fromisoformat(t["due_date"]).date() == datetime.now().date()]
    high_priority = [t for t in st.session_state.tasks if not t["completed"] and t["priority"] == "High"]
    
    with col1:
        st.metric("⚠️ Overdue Tasks", len(overdue))
    with col2:
        st.metric("🔥 Due Today", len(due_today))
    with col3:
        st.metric("🎯 High Priority", len(high_priority))

else:
    st.title("⚙️ Settings")
    st.markdown("### Customize your experience")
    
    st.markdown("#### 📂 Manage Lists")
    
    new_list = st.text_input("Create New List", placeholder="Enter list name...")
    if st.button("➕ Add List") and new_list:
        if new_list not in st.session_state.lists:
            st.session_state.lists.append(new_list)
            st.success(f"✅ List '{new_list}' created!")
            st.rerun()
        else:
            st.warning("List already exists!")
    
    st.markdown("#### Current Lists")
    for lst in st.session_state.lists:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"📁 {lst}")
        with col2:
            if st.button("Delete", key=f"del_list_{lst}"):
                st.session_state.lists.remove(lst)
                st.rerun()
    
    st.markdown("---")
    st.markdown("#### 🗑️ Danger Zone")
    if st.button("Clear All Completed Tasks", type="secondary"):
        st.session_state.tasks = [t for t in st.session_state.tasks if not t["completed"]]
        st.success("All completed tasks cleared!")
        st.rerun()
    
    if st.button("⚠️ Delete All Tasks", type="primary"):
        st.session_state.tasks = []
        st.warning("All tasks deleted!")
        st.rerun()
