import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="Academic Reporting System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .task-card {
        background-color: #ffffff;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .report-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .new-report-badge {
        background-color: #ef4444;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .stButton > button {
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# Configuration
# ==========================================
API_BASE_URL = "https://academic-reporting-api-573297019071.asia-south1.run.app/api/v1"


# ==========================================
# Session State Initialization
# ==========================================
def init_session_state():
    """Initialize all session state variables"""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if "task_list" not in st.session_state:
        st.session_state.task_list = []
    if "formatted_report" not in st.session_state:
        st.session_state.formatted_report = None
    if "new_reports_count" not in st.session_state:
        st.session_state.new_reports_count = 0
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = None
    if "show_add_user_modal" not in st.session_state:
        st.session_state.show_add_user_modal = False
    if "show_edit_user_modal" not in st.session_state:
        st.session_state.show_edit_user_modal = False
    if "edit_user_data" not in st.session_state:
        st.session_state.edit_user_data = None
    if "show_delete_modal" not in st.session_state:
        st.session_state.show_delete_modal = False
    if "delete_user_data" not in st.session_state:
        st.session_state.delete_user_data = None


def get_headers():
    """Get authorization headers"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


# ==========================================
# Utility Functions
# ==========================================
def format_date(date_string):
    """Format date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except:
        return date_string


def format_datetime(date_string):
    """Format datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y %I:%M %p")
    except:
        return date_string


def format_time(date_string):
    """Format time string"""
    try:
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return dt.strftime("%I:%M %p")
    except:
        return date_string


def get_greeting():
    """Get greeting based on time of day"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


def is_today(date_string):
    """Check if date is today"""
    try:
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return dt.date() == datetime.now().date()
    except:
        return False


# ==========================================
# API Functions
# ==========================================
def login(email, password):
    """Login user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password},
        )
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            error_msg = response.json().get("detail", "Authentication failed")
            return False, error_msg
    except Exception as e:
        return False, f"Network error: {str(e)}"


def save_draft_tasks(tasks):
    """Save draft tasks to backend"""
    try:
        task_list = [{"text": task, "completed": False} for task in tasks]
        response = requests.post(
            f"{API_BASE_URL}/simple/tasks/draft/save",
            json={"tasks": task_list},
            headers=get_headers(),
        )
        return response.status_code == 200
    except:
        return False


def load_draft_tasks():
    """Load draft tasks from backend"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/simple/tasks/draft/load",
            headers=get_headers(),
        )
        if response.status_code == 200:
            data = response.json()
            tasks = data.get("tasks", [])
            return [task["text"] for task in tasks if not task.get("completed", False)]
        return []
    except:
        return []


def generate_formatted_report(tasks):
    """Generate AI-formatted report from tasks"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/reports/generate-formatted",
            json={"tasks": tasks},
            headers=get_headers(),
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, "Failed to generate report"
    except Exception as e:
        return False, str(e)


def submit_formatted_report():
    """Submit the formatted report"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/reports/dispatch-formatted",
            json={"is_approved": True},
            headers=get_headers(),
        )
        return response.status_code == 200
    except:
        return False


def get_my_history():
    """Get faculty's report history"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/simple/reports/my-history",
            headers=get_headers(),
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def get_hod_stats():
    """Get HOD dashboard statistics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/hod/stats",
            headers=get_headers(),
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_all_reports(days=30):
    """Get all faculty reports"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/simple/reports/all?days={days}",
            headers=get_headers(),
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def get_new_reports_count():
    """Get count of new reports today"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/simple/reports/new-count",
            headers=get_headers(),
        )
        if response.status_code == 200:
            return response.json().get("new_reports", 0)
        return 0
    except:
        return 0


def get_dashboard_metrics():
    """Get dashboard metrics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/dashboard/metrics",
            headers=get_headers(),
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_all_users():
    """Get all users"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/admin/users",
            headers=get_headers(),
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def create_user(name, email, password, department, role):
    """Create new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/admin/users",
            json={
                "name": name,
                "email": email,
                "password": password,
                "department": department,
                "role": role,
            },
            headers=get_headers(),
        )
        return response.status_code == 200, (
            response.json() if response.status_code != 200 else None
        )
    except Exception as e:
        return False, str(e)


def update_user(user_id, name, email, department, role, password=None):
    """Update user"""
    try:
        data = {
            "name": name,
            "email": email,
            "department": department,
            "role": role,
        }
        if password:
            data["password"] = password

        response = requests.put(
            f"{API_BASE_URL}/admin/users/{user_id}",
            json=data,
            headers=get_headers(),
        )
        return response.status_code == 200, (
            response.json() if response.status_code != 200 else None
        )
    except Exception as e:
        return False, str(e)


def delete_user(user_id):
    """Delete user"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/admin/users/{user_id}",
            headers=get_headers(),
        )
        return response.status_code == 200
    except:
        return False


# ==========================================
# Login Screen
# ==========================================
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div style="text-align: center; padding: 2rem 0;">
                <h1>📚 Academic Reporting System</h1>
                <p style="color: #6c757d; font-size: 1.1rem;">Datta Meghe College of Engineering</p>
                <p style="color: #6c757d;">Nagar Yuwak Shikshan Sanstha, Airoli</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        with st.container():
            st.subheader("Login")

            email = st.text_input("Email Address", placeholder="user@dmce.ac.in")
            password = st.text_input("Password", type="password")

            if st.button("Login", type="primary", use_container_width=True):
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    with st.spinner("Authenticating..."):
                        success, result = login(email, password)
                        if success:
                            st.session_state.token = result.get("access_token")
                            st.session_state.user = result.get("user")
                            st.success("Login successful!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(result)

            st.markdown("---")
            st.markdown(
                """
                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                    <p style="margin: 0; font-weight: bold;">Demo Credentials:</p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                        <strong>Faculty:</strong> priya.sharma@dmce.ac.in / academic123<br>
                        <strong>HOD:</strong> rajesh.kumar@dmce.ac.in / academic123
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==========================================
# Navigation
# ==========================================
def render_navigation():
    """Render sidebar navigation"""
    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-bottom: 1rem;">
                <h3 style="margin: 0;">👤 {st.session_state.user['name']}</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">{st.session_state.user['email']}</p>
                <span style="background-color: rgba(255,255,255,0.3); padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; margin-top: 0.5rem; display: inline-block;">{st.session_state.user['role']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"**Department:** {st.session_state.user.get('department', 'N/A')}")
        st.markdown("---")

        # Navigation based on role
        if st.session_state.user["role"].upper() == "HOD":
            st.markdown("### 📊 Navigation")

            # Get new reports count for badge
            new_count = st.session_state.new_reports_count

            if st.button(
                "🏠 Dashboard",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.current_page == "Dashboard"
                    else "secondary"
                ),
            ):
                st.session_state.current_page = "Dashboard"
                st.rerun()

            reports_label = (
                f"📁 Reports {'(' + str(new_count) + ')' if new_count > 0 else ''}"
            )
            if st.button(
                reports_label,
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.current_page == "Reports"
                    else "secondary"
                ),
            ):
                st.session_state.current_page = "Reports"
                st.rerun()

            if st.button(
                "📈 Analytics",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.current_page == "Analytics"
                    else "secondary"
                ),
            ):
                st.session_state.current_page = "Analytics"
                st.rerun()

            if st.button(
                "👥 Users",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.current_page == "Users"
                    else "secondary"
                ),
            ):
                st.session_state.current_page = "Users"
                st.rerun()

            if st.button(
                "👤 Profile",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.current_page == "Profile"
                    else "secondary"
                ),
            ):
                st.session_state.current_page = "Profile"
                st.rerun()
        else:
            st.markdown("### 📚 Navigation")

            if st.button(
                "🏠 Home",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.current_page == "Home"
                    else "secondary"
                ),
            ):
                st.session_state.current_page = "Home"
                st.rerun()

            if st.button(
                "📜 History",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.current_page == "History"
                    else "secondary"
                ),
            ):
                st.session_state.current_page = "History"
                st.rerun()

            if st.button(
                "👤 Profile",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.current_page == "Profile"
                    else "secondary"
                ),
            ):
                st.session_state.current_page = "Profile"
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.current_page = "Dashboard"
            st.session_state.task_list = []
            st.session_state.formatted_report = None
            st.rerun()


# ==========================================
# Faculty Pages
# ==========================================
def faculty_home():
    """Faculty dashboard - task logging and report generation"""
    st.markdown(
        f"""
        <div class="main-header">
            <h1>👋 {get_greeting()}, {st.session_state.user['name'].split()[0]}!</h1>
            <p style="margin: 0; font-size: 1.1rem;">Ready to log your daily activities</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Load draft tasks on first visit
    if "tasks_loaded" not in st.session_state:
        loaded_tasks = load_draft_tasks()
        if loaded_tasks:
            st.session_state.task_list = loaded_tasks
        st.session_state.tasks_loaded = True

    # Date and summary cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card" style="text-align: center;">
                <h1 style="margin: 0; font-size: 3rem; color: #667eea;">{datetime.now().day}</h1>
                <p style="margin: 0; color: #6c757d;">{datetime.now().strftime("%B %Y")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #667eea;">{len(st.session_state.task_list)}</h3>
                <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">Tasks Logged</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        status = "In Progress" if st.session_state.task_list else "No Tasks"
        status_color = "#28a745" if st.session_state.task_list else "#ffc107"
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: {status_color};">{status}</h3>
                <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">Status</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Today's Activities
    st.subheader("📝 Today's Activities")

    # Add task form
    with st.form(key="add_task_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            new_task = st.text_input(
                "Log your activity",
                placeholder="E.g., Completed theory lectures on Data Structures",
                label_visibility="collapsed",
            )
        with col2:
            submit_button = st.form_submit_button(
                "➕ Add Task", use_container_width=True, type="primary"
            )

        if submit_button and new_task.strip():
            st.session_state.task_list.append(new_task.strip())
            # Auto-save to backend
            save_draft_tasks(st.session_state.task_list)
            st.rerun()

    st.markdown(
        '<p style="color: #6c757d; font-size: 0.85rem; margin-top: 0.5rem;">💡 Just type a quick note. AI will format it into a proper report when you submit.</p>',
        unsafe_allow_html=True,
    )

    # Display tasks
    if st.session_state.task_list:
        st.markdown("#### Your Tasks")
        for idx, task in enumerate(st.session_state.task_list):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f"""
                    <div class="task-card">
                        <strong>{idx + 1}.</strong> {task}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button("🗑️", key=f"delete_{idx}", help="Delete task"):
                    st.session_state.task_list.pop(idx)
                    save_draft_tasks(st.session_state.task_list)
                    st.rerun()

        st.markdown("---")

        # Generate report button
        if st.button(
            "✨ Generate & Submit Report", type="primary", use_container_width=True
        ):
            with st.spinner("Generating AI-formatted report..."):
                success, result = generate_formatted_report(st.session_state.task_list)
                if success:
                    st.session_state.formatted_report = result
                    st.rerun()
                else:
                    st.error(f"Failed to generate report: {result}")
    else:
        st.info("No tasks logged yet. Add your first task above!")

    # Show formatted report for confirmation
    if st.session_state.formatted_report:
        st.markdown("---")
        st.markdown("### 📄 Review Your Formatted Report")

        st.warning(
            "⚠️ This AI-generated report will be submitted to your HOD. Review it carefully before confirming."
        )

        formatted_tasks = st.session_state.formatted_report.get("formatted_tasks", [])

        for task in formatted_tasks:
            st.markdown(
                f"""
                <div class="report-card">
                    <h4 style="margin: 0 0 0.5rem 0; color: #667eea;">{task.get('title', 'Untitled')}</h4>
                    <p style="margin: 0; color: #495057;">{task.get('description', '')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.formatted_report = None
                st.rerun()
        with col2:
            if st.button(
                "✅ Confirm & Submit", use_container_width=True, type="primary"
            ):
                with st.spinner("Submitting report..."):
                    if submit_formatted_report():
                        st.success("✅ Report submitted successfully!")
                        st.session_state.task_list = []
                        st.session_state.formatted_report = None
                        save_draft_tasks([])
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to submit report. Please try again.")


def faculty_history():
    """Faculty report history"""
    st.markdown(
        """
        <div class="main-header">
            <h1>📜 My Report History</h1>
            <p style="margin: 0;">View all your submitted daily reports</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Loading your reports..."):
        reports = get_my_history()

    if reports:
        st.success(f"Found {len(reports)} report(s)")

        for report in reports:
            date_submitted = report.get("date_submitted", "")
            formatted_date = format_date(date_submitted)
            tasks = report.get("formatted_tasks", [])

            with st.expander(
                f"📅 {formatted_date} - {len(tasks)} task(s)", expanded=False
            ):
                for task in tasks:
                    st.markdown(
                        f"""
                        <div class="report-card">
                            <h4 style="margin: 0 0 0.5rem 0; color: #667eea;">{task.get('title', 'Untitled')}</h4>
                            <p style="margin: 0; color: #495057;">{task.get('description', '')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
    else:
        st.info("📭 No reports submitted yet. Start logging your daily activities!")


def faculty_profile():
    """Faculty profile page"""
    st.markdown(
        """
        <div class="main-header">
            <h1>👤 Profile</h1>
            <p style="margin: 0;">Your account information</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user = st.session_state.user

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Avatar
        initial = user.get("name", "U")[0].upper()
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; margin: 0 auto; color: white; font-size: 3rem; font-weight: bold;">
                    {initial}
                </div>
                <h2 style="margin: 1rem 0 0.5rem 0;">{user.get('name', 'Unknown')}</h2>
                <span style="background-color: #667eea; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem;">{user.get('role', 'N/A')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Information cards
        st.markdown("### 📧 Email")
        st.info(user.get("email", "N/A"))

        st.markdown("### 🏢 Department")
        st.info(user.get("department", "N/A"))

        st.markdown("### 💼 Role")
        st.info(user.get("role", "N/A"))

        st.markdown("### 🆔 Faculty ID")
        st.info(user.get("id", "N/A"))


# ==========================================
# HOD Pages
# ==========================================
def hod_dashboard():
    """HOD Dashboard with stats and metrics"""
    st.markdown(
        """
        <div class="main-header">
            <h1>📊 HOD Dashboard</h1>
            <p style="margin: 0;">Department overview and key metrics</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    with st.spinner("Loading statistics..."):
        stats = get_hod_stats()

    if stats:
        st.session_state.last_refresh = datetime.now()

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white;">
                    <h2 style="margin: 0; font-size: 2.5rem;">{stats.get('total_faculty', 0)}</h2>
                    <p style="margin: 0.5rem 0 0 0;">👥 Total Faculty</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white;">
                    <h2 style="margin: 0; font-size: 2.5rem;">{stats.get('reports_today', 0)}</h2>
                    <p style="margin: 0.5rem 0 0 0;">📄 Reports Today</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            completion_rate = stats.get("completion_rate", 0)
            st.markdown(
                f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); color: white;">
                    <h2 style="margin: 0; font-size: 2.5rem;">{completion_rate}%</h2>
                    <p style="margin: 0.5rem 0 0 0;">📈 Completion Rate</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col4:
            pending = stats.get("total_faculty", 0) - stats.get("reports_today", 0)
            st.markdown(
                f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white;">
                    <h2 style="margin: 0; font-size: 2.5rem;">{pending}</h2>
                    <p style="margin: 0.5rem 0 0 0;">⏰ Pending Reports</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.session_state.last_refresh:
            st.caption(
                f"Last updated: {st.session_state.last_refresh.strftime('%I:%M:%S %p')}"
            )

        st.markdown("---")

        # Recent submissions and weekly trend
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📥 Recent Submissions")
            recent = stats.get("recent_submissions", [])

            if recent:
                for submission in recent:
                    professor = submission.get("professor", "Unknown")
                    time_str = submission.get("time", "")
                    tasks = submission.get("tasks", 0)

                    st.markdown(
                        f"""
                        <div class="task-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>{professor}</strong><br>
                                    <span style="color: #6c757d; font-size: 0.85rem;">{time_str}</span>
                                </div>
                                <div style="background-color: #667eea; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem;">
                                    {tasks} tasks
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No recent submissions")

        with col2:
            st.subheader("📊 Weekly Trend")
            weekly = stats.get("weekly_trend", [])

            if weekly:
                df = pd.DataFrame(weekly)
                st.bar_chart(df.set_index("day")["submissions"])
            else:
                st.info("No trend data available")
    else:
        st.error("Failed to load dashboard statistics")


def hod_reports():
    """HOD Aggregated Reports page"""
    st.markdown(
        """
        <div class="main-header">
            <h1>📁 Faculty Reports</h1>
            <p style="margin: 0;">View all faculty submissions</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Refresh and new reports badge
    col1, col2, col3 = st.columns([4, 1, 1])
    with col2:
        new_count = get_new_reports_count()
        st.session_state.new_reports_count = new_count
        if new_count > 0:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 0.5rem;">
                    <span class="new-report-badge">🆕 {new_count} New</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # Days filter
    days = st.slider("Show reports from last N days", 1, 90, 30)

    with st.spinner("Loading faculty reports..."):
        reports = get_all_reports(days)

    if reports:
        st.success(f"Found {len(reports)} report(s) in the last {days} days")

        for report in reports:
            date_submitted = report.get("date_submitted", "")
            formatted_date = format_datetime(date_submitted)
            faculty_name = report.get("faculty_name", "Unknown")
            tasks = report.get("formatted_tasks", [])
            is_new = is_today(date_submitted)

            border_style = (
                "border-left: 4px solid #10b981;"
                if is_new
                else "border-left: 4px solid #667eea;"
            )
            new_badge = (
                '<span class="new-report-badge" style="margin-left: 0.5rem;">NEW</span>'
                if is_new
                else ""
            )

            with st.expander(
                f"👤 {faculty_name}{new_badge} - 📅 {formatted_date} ({len(tasks)} tasks)",
                expanded=False,
            ):
                for task in tasks:
                    st.markdown(
                        f"""
                        <div class="report-card" style="{border_style}">
                            <h4 style="margin: 0 0 0.5rem 0; color: #667eea;">{task.get('title', 'Untitled')}</h4>
                            <p style="margin: 0; color: #495057;">{task.get('description', '')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
    else:
        st.info(f"📭 No reports found in the last {days} days")


def hod_analytics():
    """HOD Analytics page"""
    st.markdown(
        """
        <div class="main-header">
            <h1>📈 Analytics & Insights</h1>
            <p style="margin: 0;">Department-wide performance metrics</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Loading analytics data..."):
        stats = get_hod_stats()
        metrics = get_dashboard_metrics()

    # Summary cards
    col1, col2, col3 = st.columns(3)

    with col1:
        total_subs = metrics.get("total_submissions", 0) if metrics else 0
        st.markdown(
            f"""
            <div class="metric-card">
                <h2 style="margin: 0; color: #667eea; font-size: 2.5rem;">{total_subs}</h2>
                <p style="margin: 0.5rem 0 0 0; color: #6c757d;">Total Submissions</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        active_faculty = stats.get("reports_today", 0) if stats else 0
        st.markdown(
            f"""
            <div class="metric-card">
                <h2 style="margin: 0; color: #10b981; font-size: 2.5rem;">{active_faculty}</h2>
                <p style="margin: 0.5rem 0 0 0; color: #6c757d;">Active Faculty Today</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        completion = stats.get("completion_rate", 0) if stats else 0
        st.markdown(
            f"""
            <div class="metric-card">
                <h2 style="margin: 0; color: #8b5cf6; font-size: 2.5rem;">{completion}%</h2>
                <p style="margin: 0.5rem 0 0 0; color: #6c757d;">Completion Rate</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Weekly submission trend
    if stats:
        st.subheader("📊 Weekly Submission Trend")
        weekly = stats.get("weekly_trend", [])

        if weekly:
            df = pd.DataFrame(weekly)
            st.bar_chart(df.set_index("day")["submissions"], height=350)
        else:
            st.info("No trend data available")


def hod_users():
    """HOD User Management page"""
    st.markdown(
        """
        <div class="main-header">
            <h1>👥 User Management</h1>
            <p style="margin: 0;">Manage faculty and HOD accounts</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Action buttons
    col1, col2, col3 = st.columns([4, 1, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col3:
        if st.button("➕ Add User", use_container_width=True, type="primary"):
            st.session_state.show_add_user_modal = True
            st.rerun()

    # Add User Modal
    if st.session_state.show_add_user_modal:
        with st.container():
            st.markdown("### ➕ Add New User")

            with st.form("add_user_form"):
                name = st.text_input("Name *")
                email = st.text_input("Email *")
                password = st.text_input("Password *", type="password")
                department = st.selectbox("Department *", ["IT", "CS", "EXTC", "MECH"])
                role = st.selectbox("Role *", ["FACULTY", "HOD"])

                col1, col2 = st.columns(2)
                with col1:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)
                    if cancel:
                        st.session_state.show_add_user_modal = False
                        st.rerun()
                with col2:
                    submit = st.form_submit_button(
                        "Add User", use_container_width=True, type="primary"
                    )
                    if submit:
                        if not name or not email or not password:
                            st.error("Please fill all required fields")
                        else:
                            with st.spinner("Creating user..."):
                                success, error = create_user(
                                    name, email, password, department, role
                                )
                                if success:
                                    st.success("User created successfully!")
                                    st.session_state.show_add_user_modal = False
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Failed to create user: {error}")

    # Edit User Modal
    if st.session_state.show_edit_user_modal and st.session_state.edit_user_data:
        user_data = st.session_state.edit_user_data

        with st.container():
            st.markdown(f"### ✏️ Edit User: {user_data['name']}")

            with st.form("edit_user_form"):
                name = st.text_input("Name *", value=user_data["name"])
                email = st.text_input("Email *", value=user_data["email"])
                password = st.text_input(
                    "Password (leave empty to keep current)", type="password"
                )
                department = st.selectbox(
                    "Department *",
                    ["IT", "CS", "EXTC", "MECH"],
                    index=(
                        ["IT", "CS", "EXTC", "MECH"].index(user_data["department"])
                        if user_data["department"] in ["IT", "CS", "EXTC", "MECH"]
                        else 0
                    ),
                )
                role = st.selectbox(
                    "Role *",
                    ["FACULTY", "HOD"],
                    index=(
                        ["FACULTY", "HOD"].index(user_data["role"])
                        if user_data["role"] in ["FACULTY", "HOD"]
                        else 0
                    ),
                )

                col1, col2 = st.columns(2)
                with col1:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)
                    if cancel:
                        st.session_state.show_edit_user_modal = False
                        st.session_state.edit_user_data = None
                        st.rerun()
                with col2:
                    submit = st.form_submit_button(
                        "Update User", use_container_width=True, type="primary"
                    )
                    if submit:
                        if not name or not email:
                            st.error("Please fill all required fields")
                        else:
                            with st.spinner("Updating user..."):
                                success, error = update_user(
                                    user_data["id"],
                                    name,
                                    email,
                                    department,
                                    role,
                                    password if password else None,
                                )
                                if success:
                                    st.success("User updated successfully!")
                                    st.session_state.show_edit_user_modal = False
                                    st.session_state.edit_user_data = None
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Failed to update user: {error}")

    # Delete Confirmation Modal
    if st.session_state.show_delete_modal and st.session_state.delete_user_data:
        user_data = st.session_state.delete_user_data

        st.markdown("---")
        st.error(f"### ⚠️ Delete User: {user_data['name']}")
        st.warning(
            "This will also delete all their reports and tasks. This action cannot be undone."
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_delete_modal = False
                st.session_state.delete_user_data = None
                st.rerun()
        with col2:
            if st.button("Delete", use_container_width=True, type="primary"):
                with st.spinner("Deleting user..."):
                    if delete_user(user_data["id"]):
                        st.success("User deleted successfully!")
                        st.session_state.show_delete_modal = False
                        st.session_state.delete_user_data = None
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to delete user")
        st.markdown("---")

    # User table
    with st.spinner("Loading users..."):
        users = get_all_users()

    if users:
        st.success(f"Found {len(users)} user(s)")

        # Create DataFrame
        df_data = []
        for user in users:
            role_badge = (
                "🔵 Faculty" if user.get("role", "").upper() == "FACULTY" else "🟣 HOD"
            )
            df_data.append(
                {
                    "Name": user.get("name", "N/A"),
                    "Email": user.get("email", "N/A"),
                    "Role": role_badge,
                    "Department": user.get("department", "N/A"),
                    "ID": user.get("id", "N/A"),
                }
            )

        df = pd.DataFrame(df_data)
        st.dataframe(
            df[["Name", "Email", "Role", "Department"]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        st.subheader("User Actions")

        for user in users:
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                st.write(f"**{user.get('name', 'N/A')}**")
            with col2:
                st.write(user.get("email", "N/A"))
            with col3:
                if st.button(
                    "✏️ Edit", key=f"edit_{user['id']}", use_container_width=True
                ):
                    st.session_state.show_edit_user_modal = True
                    st.session_state.edit_user_data = user
                    st.rerun()
            with col4:
                if st.button(
                    "🗑️ Delete", key=f"delete_{user['id']}", use_container_width=True
                ):
                    st.session_state.show_delete_modal = True
                    st.session_state.delete_user_data = user
                    st.rerun()
    else:
        st.info("No users found")


def hod_profile():
    """HOD profile page (same as faculty)"""
    faculty_profile()


# ==========================================
# Main App
# ==========================================
def main():
    init_session_state()

    if not st.session_state.token:
        login_screen()
    else:
        render_navigation()

        # Route to appropriate page
        if st.session_state.user["role"].upper() == "HOD":
            # Update new reports count in background
            st.session_state.new_reports_count = get_new_reports_count()

            if st.session_state.current_page == "Dashboard":
                hod_dashboard()
            elif st.session_state.current_page == "Reports":
                hod_reports()
            elif st.session_state.current_page == "Analytics":
                hod_analytics()
            elif st.session_state.current_page == "Users":
                hod_users()
            elif st.session_state.current_page == "Profile":
                hod_profile()
        else:
            if st.session_state.current_page == "Home":
                faculty_home()
            elif st.session_state.current_page == "History":
                faculty_history()
            elif st.session_state.current_page == "Profile":
                faculty_profile()


if __name__ == "__main__":
    main()
