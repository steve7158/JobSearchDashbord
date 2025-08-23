import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
from typing import Dict, Any, Optional, Tuple
from UI.ui_hiringmanager import HiringManagerUI
from UI.ui_main import MainUITabs
from UI.ui_summaryMetrics import SummaryMetricsUI
from Utils.constants import FOOTER_HTML, STYLES_STREAMLIT
from services.job_portal_service import JobPortalService
from UI.ui_sidebar import JobSearchSidebar


class JobPortalDashboard:
    """
    Main Dashboard class for the Job Portal application.
    
    This class encapsulates all the dashboard functionality including:
    - Page configuration and styling
    - Session state management
    - Job search and display
    - Analytics and visualization
    - Data export functionality
    """
    
    def __init__(self):
        """Initialize the dashboard with default configuration."""
        self.configure_page()
        self.apply_styling()
        self.initialize_session_state()
        self.sidebar = JobSearchSidebar(get_job_service_func=self.get_job_service)
        self.hiringManagerUI = HiringManagerUI()
        self.summaryMetricsUI = SummaryMetricsUI()
        self.mainUITabs = MainUITabs()
    def configure_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Job Portal Dashboard",
            page_icon="💼",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def apply_styling(self):
        """Apply custom CSS styling to the dashboard."""
        st.markdown(STYLES_STREAMLIT, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        session_defaults = {
            'jobs_data': None,
            'last_search_time': None,
            'auth_browser_opened': False,
            'auth_completed': False
        }
        
        for key, default_value in session_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    @st.cache_resource
    def get_job_service(linkedin_email=None, linkedin_password=None):
        """
        Factory method to create and cache JobPortalService instance.
        
        Args:
            linkedin_email: LinkedIn email for authentication
            linkedin_password: LinkedIn password for authentication
            
        Returns:
            JobPortalService instance
        """
        return JobPortalService(linkedin_email=linkedin_email, linkedin_password=linkedin_password)

    def render_header(self):
        """Render the dashboard header."""
        st.markdown('<h1 class="main-header">💼 Job Portal Dashboard</h1>', unsafe_allow_html=True)
        st.markdown("---")
    
    def perform_job_search(self, search_config: Dict[str, Any], job_service) -> bool:
        """
        Perform job search based on configuration.
        
        Args:
            search_config: Dictionary containing search parameters
            job_service: JobPortalService instance
            
        Returns:
            bool: True if search was successful, False otherwise
        """
        try:
            jobs_df = job_service.scrape_jobs(
                site_name=search_config['selected_sites'],
                search_term=search_config['search_term'],
                google_search_term=search_config['google_search_term'],
                location=search_config['location'],
                results_wanted=search_config['results_wanted'],
                hours_old=search_config['hours_old'],
                country_indeed=search_config['country_indeed'],
                linkedin_fetch_description=search_config['linkedin_description']
            )
            
            st.session_state.jobs_data = jobs_df
            st.session_state.last_search_time = datetime.now()
            
            st.success(f"✅ Found {len(jobs_df)} jobs!")
            
            # Check for LinkedIn jobs and offer hiring manager extraction
            linkedin_jobs_count = len(jobs_df[jobs_df['job_url'].str.contains('linkedin.com', na=False)]) if 'job_url' in jobs_df.columns else 0
            
            if linkedin_jobs_count > 0:
                st.info(f"🧑‍💼 Found {linkedin_jobs_count} LinkedIn jobs. You can fetch hiring manager details below.")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error occurred while searching: {str(e)}")
            return False

    def render_welcome_message(self):
        """Render welcome message when no data is available."""
        st.info("👋 Welcome! Use the sidebar to configure your job search and click 'Search Jobs' to get started.")
        
        # Display example of what the dashboard can do
        st.subheader("🌟 Dashboard Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**🔍 Job Search**")
            st.write("• Multi-site job scraping")
            st.write("• Customizable search parameters")
            st.write("• Real-time data fetching")
        
        with col2:
            st.write("**📊 Analytics**")
            st.write("• Interactive charts and graphs")
            st.write("• Salary analysis")
            st.write("• Company insights")
        
        with col3:
            st.write("**💾 Export & Filter**")
            st.write("• CSV/Excel export")
            st.write("• Advanced filtering")
            st.write("• Data visualization")
    
    def render_footer(self):
        """Render the dashboard footer."""
        st.markdown("---")
        st.markdown(
            FOOTER_HTML,
            unsafe_allow_html=True
        )
    
    def run(self):
        """Main method to run the dashboard."""
        self.render_header()
        
        # Initialize and render sidebar
        search_config, search_button, job_service = self.sidebar.render()
        
        # Main content area
        if search_button and search_config['selected_sites']:
            with st.spinner("🔍 Searching for jobs... This may take a few moments."):
                success = self.perform_job_search(search_config, job_service)
                if not success:
                    st.stop()
        
        elif search_button and not search_config['selected_sites']:
            st.warning("⚠️ Please select at least one job site to search.")
        
        # Display results if data exists
        if st.session_state.jobs_data is not None:
            jobs_df = st.session_state.jobs_data
            
            # Display last search info
            if st.session_state.last_search_time:
                st.info(f"📅 Last search: {st.session_state.last_search_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Hiring Manager Section
            self.hiringManagerUI.render(jobs_df, job_service)
            # Summary metrics
            self.summaryMetricsUI.render(jobs_df)
            st.markdown("---")
            
            # Main tabs
            self.mainUITabs.render_main_tabs(jobs_df, job_service)
        
        else:
            self.render_welcome_message()
        
        # Footer
        self.render_footer()


def main():
    """Main function to run the dashboard application."""
    dashboard = JobPortalDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
