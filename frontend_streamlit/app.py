import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# Section 1: Page Configuration and Viewport Styling
# ==========================================
st.set_page_config(
    page_title="Academic Reporting System",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject custom CSS to manipulate the DOM for mobile responsiveness
# and expand touch targets for input elements.
st.markdown(
    """
    <style>
    /* Viewport padding adjustment for mobile screens */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Container styling for metric displays */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 5% 10%;
        border-radius: 8px;
        color: black;
    }
    /* Standardize border radius for alert components */
    .stAlert {
        border-radius: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# Section 2: Configuration and API Client Functions
# ==========================================
API_BASE_URL = "https://academic-reporting-api-573297019071.asia-south1.run.app/api/v1"


def init_session_state():
    """Initializes required session state variables if they do not exist."""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "draft_report" not in st.session_state:
        st.session_state.draft_report = None


def get_headers():
    """Constructs the authorization header using the stored JWT."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


# ==========================================
# Section 3: Authentication Interface
# ==========================================
def login_screen():
    st.title("Academic Reporting System")
    st.markdown("Secure authentication portal for faculty and administrative staff.")

    with st.container():
        st.subheader("System Login")
        email = st.text_input("Email Address", placeholder="user@dmce.edu")
        password = st.text_input("Password", type="password")

        # use_container_width=True forces 100% width for mobile accessibility
        if st.button("Authenticate", type="primary", use_container_width=True):
            with st.spinner("Verifying credentials..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        json={"email": email, "password": password},
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data.get("access_token")
                        st.session_state.user = data.get("user")
                        st.rerun()
                    else:
                        st.error(
                            "Authentication failed. Verify credentials and try again."
                        )
                except Exception as e:
                    st.error(f"Network connection error: {e}")


# ==========================================
# Section 4: Faculty Interface (Mobile-First Layout)
# ==========================================
def faculty_dashboard():
    st.header(f"Faculty Portal: {st.session_state.user['name']}")

    # Tabbed navigation conserves vertical viewport space on mobile devices
    tab_logging, tab_history = st.tabs(["Task Intake", "Submission History"])

    with tab_logging:
        st.markdown("### Step 1: Unstructured Input")
        st.markdown(
            "Enter standard task descriptions. The AI engine will structure the output."
        )

        raw_task = st.text_area(
            "Daily Activity Log",
            height=150,
            placeholder="e.g., Conducted SE IT lecture on Data Structures, completed assignment evaluation for 20 students.",
        )

        if st.button("Process Input Data", type="primary", use_container_width=True):
            if raw_task:
                with st.spinner("Executing natural language processing pipeline..."):
                    try:
                        # LangGraph Phase 1: Intake and sanitization
                        res = requests.post(
                            f"{API_BASE_URL}/tasks/intake",
                            json={
                                "raw_input": raw_task,
                                "professor_id": st.session_state.user["id"],
                            },
                            headers=get_headers(),
                        )
                        if res.status_code == 200:
                            st.success("Input accepted into current context.")

                            # LangGraph Phase 2: Draft generation
                            draft_res = requests.post(
                                f"{API_BASE_URL}/reports/generate",
                                json={"professor_id": st.session_state.user["id"]},
                                headers=get_headers(),
                            )
                            if draft_res.status_code == 200:
                                st.session_state.draft_report = draft_res.json()
                    except Exception as e:
                        st.error("Pipeline communication failure.")
            else:
                st.warning("Input payload cannot be empty.")

        # Human-in-the-Loop Validation Component
        if st.session_state.draft_report:
            st.markdown("---")
            st.markdown("### Step 2: Verification and Dispatch")
            with st.expander("Review Formatted Output", expanded=True):
                st.write("**System Summary:**")
                st.info(
                    st.session_state.draft_report.get(
                        "executive_summary", "Not available"
                    )
                )

                st.write("**Extracted Data Points:**")
                for task in st.session_state.draft_report.get("tasks", []):
                    st.markdown(f"- **{task['action']}**: {task['metric']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Purge Draft", use_container_width=True):
                    st.session_state.draft_report = None
                    st.rerun()
            with col2:
                if st.button(
                    "Authorize Dispatch", type="primary", use_container_width=True
                ):
                    with st.spinner("Committing record to main database..."):
                        requests.post(
                            f"{API_BASE_URL}/reports/dispatch",
                            json={
                                "professor_id": st.session_state.user["id"],
                                "is_approved": True,
                            },
                            headers=get_headers(),
                        )
                        st.session_state.draft_report = None
                        st.success("Transaction complete. Data recorded.")
                        st.rerun()

    with tab_history:
        st.markdown("### Historical Records")
        try:
            hist_res = requests.get(
                f"{API_BASE_URL}/simple/reports/my-history", headers=get_headers()
            )
            if hist_res.status_code == 200:
                history = hist_res.json()
                for report in history:
                    with st.expander(
                        f"Record Timestamp: {report['date_submitted'][:10]}"
                    ):
                        st.write(report["executive_summary"])
        except Exception:
            st.info("Unable to fetch historical data from backend.")


# ==========================================
# Section 5: Administrative Interface (Desktop Layout)
# ==========================================
def hod_dashboard():
    st.header("Departmental Analytics Dashboard")

    # Horizontal metric alignment utilizes wide desktop viewports
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Daily Active Submissions", value="14", delta="2")
    with col2:
        st.metric(label="Faculty Compliance Rate", value="85%", delta="5%")
    with col3:
        st.metric(label="Aggregate Task Volume", value="45")

    st.markdown("---")

    # Asymmetric column distribution for complex data structures
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Real-Time Submission Stream")
        data = {
            "Faculty ID": ["IT-101", "IT-102", "IT-105", "IT-108"],
            "Timestamp": ["10:30", "11:15", "13:00", "14:45"],
            "Task Count": [4, 2, 5, 3],
            "System Summary": [
                "Completed 2 lectures, NAAC documentation",
                "Evaluated assignments",
                "Research laboratory setup",
                "Conducted practical sessions",
            ],
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with c2:
        st.subheader("Categorical Distribution")
        chart_data = pd.DataFrame(
            {
                "Classification": [
                    "Pedagogy",
                    "Administration",
                    "Research",
                    "Evaluation",
                ],
                "Volume": [45, 20, 15, 30],
            }
        )
        st.bar_chart(chart_data.set_index("Classification"))


# ==========================================
# Section 6: Application Router
# ==========================================
def main():
    init_session_state()

    # Sidebar rendering for state management
    if st.session_state.user:
        with st.sidebar:
            st.write(f"Active Session: **{st.session_state.user['name']}**")
            st.write(f"Privilege Level: **{st.session_state.user['role']}**")
            if st.button("Terminate Session", use_container_width=True):
                st.session_state.token = None
                st.session_state.user = None
                st.session_state.draft_report = None
                st.rerun()

    # Dynamic interface routing based on authentication and authorization state
    if not st.session_state.token:
        login_screen()
    else:
        if st.session_state.user["role"].upper() == "HOD":
            hod_dashboard()
        else:
            faculty_dashboard()


if __name__ == "__main__":
    main()
