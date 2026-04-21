import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import DATA_FILE, MIN_SCORE_THRESHOLD
from src.models import JobPosting, ApplicationStatus
from src.agents.data_engineer import DataEngineerAgent


class DashboardAgent:
    def __init__(self):
        self.data_agent = DataEngineerAgent()

    def _load_data(self, min_score: int = None) -> pd.DataFrame:
        jobs = self.data_agent.load_existing_jobs()

        if not jobs:
            return pd.DataFrame()

        min_score = min_score or MIN_SCORE_THRESHOLD
        
        data = []
        for job in jobs:
            if job.score and job.score < min_score:
                continue
            data.append({
                "Job ID": job.job_id,
                "Title": job.title,
                "Company": job.company,
                "Location": job.location,
                "Experience": job.experience_required,
                "Source": job.source,
                "Score": job.score,
                "Status": job.status.value,
                "URL": job.url,
            })

        return pd.DataFrame(data)

    def _render_funnel(self, df: pd.DataFrame):
        st.markdown("### 🎯 Application Pipeline")
        
        total = len(df)
        quality = len(df[df["Score"] >= MIN_SCORE_THRESHOLD])
        new_jobs = len(df[df["Status"] == "New"])
        applied = len(df[df["Status"] == "Applied"])
        interviewing = len(df[df["Status"] == "Interviewing"])
        offer = len(df[df["Status"] == "Offer"])
        
        funnel_stages = [
            ("🔍 Scraped", total, "#6366f1"),
            (f"✅ Quality (≥{MIN_SCORE_THRESHOLD})", quality, "#8b5cf6"),
            ("📝 New (To Apply)", new_jobs, "#f59e0b"),
            ("🚀 Applied", applied, "#10b981"),
            ("💬 Interviewing", interviewing, "#3b82f6"),
            ("🏆 Offer", offer, "#22c55e"),
        ]
        
        cols = st.columns(len(funnel_stages))
        
        for i, (label, count, color) in enumerate(funnel_stages):
            with cols[i]:
                percentage = (count / total * 100) if total > 0 else 0
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {color}20, {color}10);
                    border: 2px solid {color};
                    border-radius: 12px;
                    padding: 15px 10px;
                    text-align: center;
                    margin: 5px 0;
                ">
                    <div style="font-size: 12px; color: #666; margin-bottom: 5px;">{label}</div>
                    <div style="font-size: 28px; font-weight: bold; color: {color};">{count}</div>
                    <div style="font-size: 11px; color: #888;">{percentage:.0f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Status Breakdown")
            status_colors = {
                "New": "#f59e0b",
                "Applied": "#10b981", 
                "Interviewing": "#3b82f6",
                "Rejected": "#ef4444",
                "Not Applying": "#6b7280",
                "Offer": "#22c55e"
            }
            
            status_counts = df["Status"].value_counts()
            
            for status, count in status_counts.items():
                color = status_colors.get(status, "#6b7280")
                pct = count / total * 100
                
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin: 10px 0;">
                    <div style="width: 120px; font-weight: 500;">{status}</div>
                    <div style="flex: 1; height: 24px; background: #f0f0f0; border-radius: 12px; overflow: hidden; margin: 0 10px;">
                        <div style="width: {pct}%; height: 100%; background: {color}; border-radius: 12px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;">
                            <span style="color: white; font-size: 12px; font-weight: bold;">{count}</span>
                        </div>
                    </div>
                    <div style="width: 50px; text-align: right; color: #666;">{pct:.0f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📈 Quick Stats")
            
            avg_score = df["Score"].mean()
            max_score = df["Score"].max()
            
            if applied > 0:
                interview_rate = interviewing / applied * 100
            else:
                interview_rate = 0
                
            if interviewing > 0:
                offer_rate = offer / interviewing * 100
            else:
                offer_rate = 0
            
            stats = [
                ("📊 Avg Score", f"{avg_score:.1f}", "#6366f1"),
                ("⭐ Highest", f"{max_score:.1f}", "#8b5cf6"),
                ("📨 Applied", str(applied), "#10b981"),
                ("💬 Interview Rate", f"{interview_rate:.0f}%", "#3b82f6"),
                ("🏆 Offer Rate", f"{offer_rate:.0f}%", "#22c55e"),
            ]
            
            for label, value, color in stats:
                st.markdown(f"""
                <div style="
                    background: {color}15;
                    border-left: 4px solid {color};
                    padding: 12px 15px;
                    border-radius: 8px;
                    margin: 8px 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <span style="color: #666;">{label}</span>
                    <span style="font-size: 20px; font-weight: bold; color: {color};">{value}</span>
                </div>
                """, unsafe_allow_html=True)

    def render(self):
        st.set_page_config(page_title="Job Hunt Dashboard", layout="wide", page_icon="💼")
        
        st.markdown("""
        <style>
        .main-header {
            font-size: 32px;
            font-weight: bold;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            border-radius: 8px 8px 0 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-header">💼 Job Hunt Dashboard</div>', unsafe_allow_html=True)

        with st.sidebar:
            st.header("⚙️ Settings")
            
            min_score_filter = st.slider(
                "Min Score Threshold",
                min_value=0,
                max_value=100,
                value=MIN_SCORE_THRESHOLD,
                key="score_threshold"
            )
            
            st.markdown("---")
        
        df = self._load_data(min_score=min_score_filter)

        if df.empty:
            st.info("No jobs found. Run the scraper first!")
            return

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Jobs", len(df), delta_color="off")
        with col2:
            new_count = len(df[df["Status"] == "New"])
            st.metric("New", new_count, delta_color="off")
        with col3:
            applied_count = len(df[df["Status"] == "Applied"])
            st.metric("Applied", applied_count, delta_color="off")
        with col4:
            interviewing_count = len(df[df["Status"] == "Interviewing"])
            st.metric("Interviewing", interviewing_count, delta_color="off")
        with col5:
            offer_count = len(df[df["Status"] == "Offer"])
            st.metric("Offers", offer_count, delta="1" if offer_count > 0 else None, delta_color="normal")

        st.divider()

        tabs = st.tabs(["📋 All Jobs", "🔍 By Status", "📊 Statistics", "📈 Analytics"])

        with tabs[0]:
            from streamlit import column_config
            
            df_display = df.copy()
            df_display["Apply"] = df_display["URL"]
            
            status_colors = {
                "New": "orange",
                "Applied": "green",
                "Interviewing": "blue",
                "Rejected": "red",
                "Not Applying": "gray",
                "Offer": "violet"
            }
            
            st.dataframe(
                df_display[["Title", "Company", "Location", "Experience", "Score", "Status", "Apply"]],
                column_config={
                    "Apply": column_config.LinkColumn("Apply", display_text="🔗 Apply"),
                    "Status": column_config.TextColumn("Status", help="Job application status"),
                },
                width='stretch',
                hide_index=True,
                use_container_width=True,
            )

        with tabs[1]:
            status_filter = st.selectbox(
                "Filter by Status",
                options=["All"] + [s.value for s in ApplicationStatus],
                key="status_filter"
            )

            if status_filter != "All":
                filtered = df[df["Status"] == status_filter]
            else:
                filtered = df

            if not filtered.empty:
                from streamlit import column_config
                filtered_display = filtered.copy()
                filtered_display["Apply"] = filtered["URL"]
                
                st.dataframe(
                    filtered_display[["Title", "Company", "Location", "Score", "Status", "Apply"]],
                    column_config={
                        "Apply": column_config.LinkColumn("Apply", display_text="🔗 Apply"),
                    },
                    width='stretch',
                    hide_index=True,
                    use_container_width=True,
                )

        with tabs[2]:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🏢 Top Companies")
                if not df.empty:
                    company_counts = df["Company"].value_counts().head(10)
                    st.bar_chart(company_counts, color="#6366f1")

            with col2:
                st.markdown("### 📍 Jobs by Location")
                if not df.empty:
                    location_counts = df["Location"].value_counts()
                    st.bar_chart(location_counts, color="#8b5cf6")

        with tabs[3]:
            self._render_funnel(df)

        st.divider()

        st.subheader("⚡ Quick Actions")

        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            job_options = [f"{row['Title']} @ {row['Company']} (Score: {row['Score']})" for _, row in df.iterrows()]
            selected_option = st.selectbox(
                "Select Job",
                options=job_options,
                key="quick_job_select"
            )

        with col2:
            new_status = st.selectbox(
                "New Status",
                options=[s.value for s in ApplicationStatus],
                key="quick_status"
            )

        with col3:
            st.write("")  
            st.write("")
            if st.button("Update Status", type="primary", use_container_width=True):
                if selected_option:
                    idx = job_options.index(selected_option)
                    job_id = df.iloc[idx]['Job ID']
                    self.data_agent.update_status(job_id, ApplicationStatus(new_status))
                    st.success(f"Updated to {new_status}!")
                    st.rerun()

        st.divider()
        
        st.subheader("📝 Job Details")
        
        if not df.empty:
            job_id = st.selectbox(
                "Select a job to view details",
                options=df["Job ID"].tolist(),
                key="details_selector"
            )
            
            job_row = df[df["Job ID"] == job_id].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Title:** {job_row['Title']}")
                st.markdown(f"**Company:** {job_row['Company']}")
                st.markdown(f"**Location:** {job_row['Location']}")
                
            with col2:
                st.markdown(f"**Experience:** {job_row['Experience']} years")
                st.markdown(f"**Score:** {job_row['Score']}")
                st.markdown(f"**Status:** {job_row['Status']}")
            
            st.markdown(f"**URL:** [Apply Now →]({job_row['URL']})")

    def run(self):
        self.render()


def run_dashboard():
    dashboard = DashboardAgent()
    dashboard.run()


if __name__ == "__main__":
    run_dashboard()