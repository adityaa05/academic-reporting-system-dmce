import gradio as gr
import requests
import json
from datetime import datetime
from typing import Optional, List, Dict, Tuple

# API Configuration
API_BASE_URL = "https://academic-reporting-api-573297019071.asia-south1.run.app/api/v1"

# Global state for auth
class AuthState:
    def __init__(self):
        self.token: Optional[str] = None
        self.user: Optional[Dict] = None

    def is_authenticated(self) -> bool:
        return self.token is not None

    def is_hod(self) -> bool:
        return self.user and self.user.get('role') == 'HOD'

    def is_faculty(self) -> bool:
        return self.user and self.user.get('role') == 'FACULTY'

auth_state = AuthState()

# API Client
def api_request(method: str, endpoint: str, data: Optional[Dict] = None, use_auth: bool = True):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if use_auth and auth_state.token:
        headers["Authorization"] = f"Bearer {auth_state.token}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = error_data.get('detail', error_msg)
            except:
                pass
        return False, error_msg

# Auth functions
def login(email: str, password: str) -> Tuple[str, bool, bool]:
    if not email or not password:
        return "Please enter both email and password", gr.update(), gr.update()

    success, result = api_request("POST", "/auth/login", {
        "email": email,
        "password": password
    }, use_auth=False)

    if success:
        auth_state.token = result['access_token']
        auth_state.user = result['user']

        role = auth_state.user.get('role', 'FACULTY')
        name = auth_state.user.get('name', 'User')

        message = f"Welcome, {name}!"

        if role == 'HOD':
            return message, gr.update(visible=False), gr.update(visible=True)
        else:
            return message, gr.update(visible=True), gr.update(visible=False)
    else:
        return f"Login failed: {result}", gr.update(), gr.update()

def logout() -> Tuple[str, bool, bool]:
    auth_state.token = None
    auth_state.user = None
    return "Logged out successfully", gr.update(visible=False), gr.update(visible=False)

# Faculty functions
def add_task(task_list: List[str], new_task: str) -> Tuple[List[str], str]:
    if not new_task.strip():
        return task_list, ""

    task_list = task_list or []
    task_list.append(new_task.strip())
    return task_list, ""

def remove_task(task_list: List[str], index: int) -> List[str]:
    if task_list and 0 <= index < len(task_list):
        task_list.pop(index)
    return task_list

def generate_report(task_list: List[str]) -> str:
    if not task_list:
        return "No tasks to generate report from."

    success, result = api_request("POST", "/reports/generate-formatted", {
        "tasks": task_list
    })

    if success:
        formatted_tasks = result.get('formatted_tasks', [])
        report_text = "AI-Generated Report:\n\n"
        for i, task in enumerate(formatted_tasks, 1):
            report_text += f"{i}. {task['title']}\n"
            report_text += f"   {task['description']}\n\n"
        return report_text
    else:
        return f"Error generating report: {result}"

def submit_report(task_list: List[str]) -> Tuple[str, List[str]]:
    if not task_list:
        return "No tasks to submit.", task_list

    # First generate the report
    success, result = api_request("POST", "/reports/generate-formatted", {
        "tasks": task_list
    })

    if not success:
        return f"Error generating report: {result}", task_list

    # Then dispatch it
    success, result = api_request("POST", "/reports/dispatch-formatted", {
        "is_approved": True
    })

    if success:
        return "Report submitted successfully!", []
    else:
        return f"Error submitting report: {result}", task_list

def load_report_history() -> str:
    success, result = api_request("GET", "/simple/reports/my-history")

    if success:
        reports = result.get('reports', [])
        if not reports:
            return "No report history available."

        history_text = "Your Report History:\n\n"
        for report in reports:
            history_text += f"Date: {report.get('submitted_at', 'N/A')}\n"
            history_text += f"Status: {report.get('status', 'N/A')}\n"
            history_text += f"Tasks: {len(report.get('tasks', []))}\n"
            history_text += "-" * 50 + "\n\n"
        return history_text
    else:
        return f"Error loading history: {result}"

# HOD functions
def load_hod_stats() -> Tuple[str, str]:
    success, result = api_request("GET", "/hod/stats")

    if success:
        stats_text = f"""Department Statistics:

Total Faculty: {result.get('total_faculty', 0)}
Reports Today: {result.get('reports_today', 0)}
Completion Rate: {result.get('completion_rate', 0)}%
Pending Reports: {result.get('total_faculty', 0) - result.get('reports_today', 0)}
"""

        recent = result.get('recent_submissions', [])
        recent_text = "Recent Submissions:\n\n"
        if recent:
            for sub in recent:
                recent_text += f"• {sub['professor']} - {sub['tasks']} tasks at {sub['time']}\n"
        else:
            recent_text += "No recent submissions."

        return stats_text, recent_text
    else:
        return f"Error loading stats: {result}", ""

def load_all_faculty_reports(days: int) -> str:
    success, result = api_request("GET", f"/simple/reports/all?days={days}")

    if success:
        reports = result.get('reports', [])
        if not reports:
            return f"No reports found in the last {days} days."

        reports_text = f"All Faculty Reports (Last {days} Days):\n\n"
        for report in reports:
            reports_text += f"Faculty: {report.get('faculty_name', 'N/A')}\n"
            reports_text += f"Date: {report.get('submitted_at', 'N/A')}\n"
            reports_text += f"Tasks: {len(report.get('tasks', []))}\n"

            if report.get('tasks'):
                reports_text += "Details:\n"
                for task in report['tasks']:
                    reports_text += f"  - {task}\n"

            reports_text += "-" * 50 + "\n\n"
        return reports_text
    else:
        return f"Error loading reports: {result}"

# UI Components
def create_login_tab():
    with gr.Column(visible=True) as login_tab:
        gr.Markdown("# Academic Reporting System")
        gr.Markdown("## Login")

        email = gr.Textbox(label="Email", placeholder="your.email@example.com")
        password = gr.Textbox(label="Password", type="password")
        login_btn = gr.Button("Login", variant="primary")
        login_msg = gr.Textbox(label="Status", interactive=False)

    return login_tab, email, password, login_btn, login_msg

def create_faculty_tab():
    with gr.Column(visible=False) as faculty_tab:
        gr.Markdown("# Faculty Dashboard")

        with gr.Row():
            gr.Markdown(f"**Today's Date:** {datetime.now().strftime('%A, %B %d, %Y')}")

        with gr.Tabs():
            with gr.Tab("Log Tasks"):
                task_list_state = gr.State([])

                with gr.Row():
                    new_task_input = gr.Textbox(
                        label="Add Task",
                        placeholder="E.g., Completed theory lectures for CS101",
                        lines=2
                    )
                add_task_btn = gr.Button("Add Task")

                task_display = gr.Dataframe(
                    headers=["#", "Task"],
                    datatype=["number", "str"],
                    label="Today's Tasks",
                    interactive=False
                )

                with gr.Row():
                    generate_btn = gr.Button("Preview Report")
                    submit_btn = gr.Button("Submit Report", variant="primary")

                report_preview = gr.Textbox(
                    label="Report Preview",
                    lines=10,
                    interactive=False
                )
                submit_msg = gr.Textbox(label="Status", interactive=False)

                def update_display(task_list):
                    if not task_list:
                        return []
                    return [[i+1, task] for i, task in enumerate(task_list)]

                def add_and_update(task_list, new_task):
                    new_list, cleared = add_task(task_list, new_task)
                    return new_list, update_display(new_list), cleared

                add_task_btn.click(
                    fn=add_and_update,
                    inputs=[task_list_state, new_task_input],
                    outputs=[task_list_state, task_display, new_task_input]
                )

                generate_btn.click(
                    fn=generate_report,
                    inputs=[task_list_state],
                    outputs=[report_preview]
                )

                def submit_and_update(task_list):
                    msg, new_list = submit_report(task_list)
                    return msg, new_list, update_display(new_list), ""

                submit_btn.click(
                    fn=submit_and_update,
                    inputs=[task_list_state],
                    outputs=[submit_msg, task_list_state, task_display, report_preview]
                )

            with gr.Tab("Report History"):
                refresh_history_btn = gr.Button("Refresh History")
                history_display = gr.Textbox(
                    label="Your Previous Reports",
                    lines=15,
                    interactive=False
                )

                refresh_history_btn.click(
                    fn=load_report_history,
                    outputs=[history_display]
                )

        logout_btn = gr.Button("Logout")

    return faculty_tab, logout_btn

def create_hod_tab():
    with gr.Column(visible=False) as hod_tab:
        gr.Markdown("# HOD Dashboard")

        with gr.Tabs():
            with gr.Tab("Dashboard"):
                refresh_stats_btn = gr.Button("Refresh Stats")

                stats_display = gr.Textbox(
                    label="Department Statistics",
                    lines=8,
                    interactive=False
                )

                recent_display = gr.Textbox(
                    label="Recent Submissions",
                    lines=10,
                    interactive=False
                )

                refresh_stats_btn.click(
                    fn=load_hod_stats,
                    outputs=[stats_display, recent_display]
                )

            with gr.Tab("Faculty Reports"):
                days_slider = gr.Slider(
                    minimum=1,
                    maximum=90,
                    value=30,
                    step=1,
                    label="Days to show"
                )
                load_reports_btn = gr.Button("Load Reports")

                reports_display = gr.Textbox(
                    label="All Faculty Reports",
                    lines=20,
                    interactive=False
                )

                load_reports_btn.click(
                    fn=load_all_faculty_reports,
                    inputs=[days_slider],
                    outputs=[reports_display]
                )

        logout_btn_hod = gr.Button("Logout")

    return hod_tab, logout_btn_hod

# Main app
def create_app():
    with gr.Blocks(title="Academic Reporting System", theme=gr.themes.Soft()) as app:
        login_tab, email, password, login_btn, login_msg = create_login_tab()
        faculty_tab, logout_btn_faculty = create_faculty_tab()
        hod_tab, logout_btn_hod = create_hod_tab()

        login_btn.click(
            fn=login,
            inputs=[email, password],
            outputs=[login_msg, faculty_tab, hod_tab]
        )

        def logout_and_show_login():
            msg, faculty_vis, hod_vis = logout()
            return msg, gr.update(visible=True), faculty_vis, hod_vis

        logout_btn_faculty.click(
            fn=logout_and_show_login,
            outputs=[login_msg, login_tab, faculty_tab, hod_tab]
        )

        logout_btn_hod.click(
            fn=logout_and_show_login,
            outputs=[login_msg, login_tab, faculty_tab, hod_tab]
        )

    return app

if __name__ == "__main__":
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=7860)
