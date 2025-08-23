import streamlit as st
import pandas as pd
import os
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime


class HiringManagerUI:
    """
    UI component class for handling hiring manager extraction and display.
    
    This class provides a complete interface for:
    - LinkedIn authentication management
    - Hiring manager data extraction
    - Progress tracking and status display
    - Statistics and analytics
    - Detailed hiring manager information display
    """
    
    def __init__(self):
        """Initialize the HiringManagerUI component."""
        self.linkedin_email_env = os.getenv('LINKEDIN_EMAIL', '')
        self.linkedin_password_env = os.getenv('LINKEDIN_PASSWORD', '')
        
        # Initialize session state for hiring manager operations
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables for hiring manager operations."""
        session_defaults = {
            'hiring_auth_browser_opened': False,
            'hiring_auth_completed': False,
            'hiring_fetch_in_progress': False,
            'hiring_last_fetch_time': None,
            'hiring_fetch_results': None
        }
        
        for key, default_value in session_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def render(self, jobs_df: pd.DataFrame, job_service) -> Dict[str, Any]:
        """
        Render the complete hiring manager UI component.
        
        Args:
            jobs_df: DataFrame containing job data
            job_service: JobPortalService instance
            
        Returns:
            Dictionary containing component state and results
        """
        linkedin_jobs_count = self._count_linkedin_jobs(jobs_df)
        
        if linkedin_jobs_count == 0:
            self._render_no_linkedin_jobs_message()
            return {'linkedin_jobs_count': 0, 'hiring_managers_available': False}
        
        # Main hiring manager section
        st.markdown("---")
        st.markdown("### 🧑‍💼 Hiring Manager Extraction")
        
        # Render main interface
        self._render_main_interface(linkedin_jobs_count, jobs_df, job_service)
        
        # Render statistics if data exists
        if self._has_hiring_manager_data(jobs_df):
            self._render_statistics_section(jobs_df, linkedin_jobs_count)
        
        # Render detailed view if data exists
        if self._has_hiring_manager_data(jobs_df):
            self._render_detailed_view_section(jobs_df)
        
        return {
            'linkedin_jobs_count': linkedin_jobs_count,
            'hiring_managers_available': self._has_hiring_manager_data(jobs_df),
            'total_managers_found': self._get_total_managers_count(jobs_df),
            'success_rate': self._calculate_success_rate(jobs_df, linkedin_jobs_count)
        }
    
    def _count_linkedin_jobs(self, jobs_df: pd.DataFrame) -> int:
        """Count LinkedIn jobs in the dataframe."""
        if 'job_url' not in jobs_df.columns:
            return 0
        return len(jobs_df[jobs_df['job_url'].str.contains('linkedin.com', na=False)])
    
    def _render_no_linkedin_jobs_message(self):
        """Render message when no LinkedIn jobs are found."""
        st.info("🔍 No LinkedIn jobs found in current results. Hiring manager extraction requires LinkedIn job postings.")
    
    def _render_main_interface(self, linkedin_jobs_count: int, jobs_df: pd.DataFrame, job_service):
        """Render the main hiring manager interface."""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_description_section(linkedin_jobs_count)
        
        with col2:
            self._render_control_panel(jobs_df, job_service, linkedin_jobs_count)
    
    def _render_description_section(self, linkedin_jobs_count: int):
        """Render the description section."""
        st.markdown(f"""
        **Extract hiring manager information from LinkedIn job pages**
        
        📊 **Available Jobs:** {linkedin_jobs_count} LinkedIn job postings  
        🎯 **Data Source:** "Meet the hiring team" sections  
        🔍 **Information Extracted:** Names, titles, LinkedIn profiles  
        
        ⚠️ **Processing Time:** May take several minutes ({linkedin_jobs_count} pages to process)
        """)
        
        # Show last fetch information if available
        if st.session_state.get('hiring_last_fetch_time'):
            last_fetch = st.session_state.hiring_last_fetch_time
            st.caption(f"Last extraction: {last_fetch.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _render_control_panel(self, jobs_df: pd.DataFrame, job_service, linkedin_jobs_count: int):
        """Render the control panel with authentication and fetch controls."""
        st.markdown("**🔧 Control Panel**")
        
        # Authentication section
        self._render_authentication_section(job_service)
        
        # Fetch section
        self._render_fetch_section(jobs_df, job_service, linkedin_jobs_count)
        
        # Status section
        self._render_status_section()
    
    def _render_authentication_section(self, job_service):
        """Render LinkedIn authentication controls."""
        if not (self.linkedin_email_env and self.linkedin_password_env):
            st.info("💡 Add LinkedIn credentials to .env for authenticated extraction")
            return
        
        st.markdown("**🔐 LinkedIn Authentication**")
        
        # Authentication status
        if st.session_state.get('hiring_auth_completed', False):
            st.success("✅ Authenticated")
            if st.button("🔄 Re-authenticate", key="hiring_reauth", help="Start new authentication session"):
                st.session_state.hiring_auth_completed = False
                st.session_state.hiring_auth_browser_opened = False
                st.rerun()
        else:
            auth_col1, auth_col2 = st.columns(2)
            
            with auth_col1:
                if st.button("🔐 Start Auth", key="hiring_start_auth", type="secondary", help="Open browser for LinkedIn authentication"):
                    with st.spinner("🌐 Opening browser..."):
                        if job_service.start_linkedin_interactive_auth():
                            st.session_state.hiring_auth_browser_opened = True
                            st.success("✅ Browser opened!")
                        else:
                            st.error("❌ Failed to open browser")
            
            with auth_col2:
                if st.session_state.get('hiring_auth_browser_opened', False):
                    if st.button("✅ Complete", key="hiring_complete_auth", type="primary", help="Click after completing login"):
                        with st.spinner("🔍 Verifying..."):
                            if job_service.confirm_linkedin_auth_complete():
                                st.success("🎉 Authentication confirmed!")
                                st.session_state.hiring_auth_completed = True
                                st.session_state.hiring_auth_browser_opened = False
                                st.rerun()
                            else:
                                st.error("❌ Authentication incomplete")
    
    def _render_fetch_section(self, jobs_df: pd.DataFrame, job_service, linkedin_jobs_count: int):
        """Render hiring manager fetch controls."""
        st.markdown("**🔍 Data Extraction**")
        
        # Check if data already exists
        has_existing_data = self._has_hiring_manager_data(jobs_df)
        
        if has_existing_data:
            st.warning("⚠️ Hiring manager data exists")
            overwrite = st.checkbox("Overwrite existing data", key="hiring_overwrite")
            if not overwrite:
                st.info("✅ Using existing data")
                return
        
        # Fetch button
        if st.session_state.get('hiring_fetch_in_progress', False):
            st.info("🔄 Extraction in progress...")
            if st.button("🛑 Cancel", key="hiring_cancel", type="secondary"):
                st.session_state.hiring_fetch_in_progress = False
                st.rerun()
        else:
            if st.button("🚀 Extract Hiring Managers", key="hiring_fetch", type="primary", use_container_width=True):
                self._execute_hiring_manager_fetch(jobs_df, job_service, linkedin_jobs_count)
    
    def _render_status_section(self):
        """Render current status information."""
        st.markdown("**📊 Status**")
        
        # Authentication status
        auth_status = "✅ Ready" if st.session_state.get('hiring_auth_completed', False) else "⚠️ Not authenticated"
        st.write(f"Auth: {auth_status}")
        
        # Last operation status
        if st.session_state.get('hiring_fetch_results'):
            results = st.session_state.hiring_fetch_results
            st.write(f"Last run: {results.get('status', 'Unknown')}")
            if 'total_managers' in results:
                st.write(f"Found: {results['total_managers']} managers")
    
    def _execute_hiring_manager_fetch(self, jobs_df: pd.DataFrame, job_service, linkedin_jobs_count: int):
        """Execute the hiring manager fetch operation."""
        st.session_state.hiring_fetch_in_progress = True
        
        auth_status = "with authentication" if st.session_state.get('hiring_auth_completed', False) else "without authentication"
        
        with st.spinner(f"🔍 Extracting hiring managers from {linkedin_jobs_count} LinkedIn jobs {auth_status}..."):
            try:
                # Progress tracking
                progress_bar = st.progress(0)
                status_container = st.container()
                
                with status_container:
                    st.info("🔧 Setting up browser automation...")
                
                # Authenticate if needed
                if self.linkedin_email_env and self.linkedin_password_env:
                    if not st.session_state.get('hiring_auth_completed', False):
                        st.warning("🔐 Authentication required! Complete login in browser, then click 'Complete' above.")
                        st.session_state.hiring_fetch_in_progress = False
                        st.stop()
                
                # Execute extraction
                with status_container:
                    st.info("🔍 Extracting hiring manager data...")
                
                jobs_with_managers = job_service.fetch_hiring_managers_for_jobs(jobs_df)
                
                # Update session state
                st.session_state.jobs_data = jobs_with_managers
                st.session_state.hiring_last_fetch_time = datetime.now()
                
                # Calculate results
                successful_fetches = jobs_with_managers['hiring_manager_fetch_success'].sum() if 'hiring_manager_fetch_success' in jobs_with_managers.columns else 0
                total_managers_found = jobs_with_managers['hiring_managers_count'].sum() if 'hiring_managers_count' in jobs_with_managers.columns else 0
                
                # Store results
                st.session_state.hiring_fetch_results = {
                    'status': 'Success',
                    'successful_fetches': successful_fetches,
                    'total_managers': total_managers_found,
                    'linkedin_jobs_count': linkedin_jobs_count,
                    'timestamp': datetime.now()
                }
                
                progress_bar.progress(1.0)
                
                # Show results
                if 'hiring_manager_method' in jobs_with_managers.columns:
                    auth_jobs = len(jobs_with_managers[jobs_with_managers['hiring_manager_method'] == 'authenticated'])
                    if auth_jobs > 0:
                        st.info(f"🔐 {auth_jobs} jobs processed with authentication")
                
                st.success(f"✅ Complete! Processed {successful_fetches}/{linkedin_jobs_count} jobs, found {total_managers_found} hiring managers")
                
                if total_managers_found > 0:
                    st.balloons()
                
            except Exception as e:
                st.error(f"❌ Extraction failed: {str(e)}")
                st.session_state.hiring_fetch_results = {
                    'status': 'Error',
                    'error': str(e),
                    'timestamp': datetime.now()
                }
            
            finally:
                st.session_state.hiring_fetch_in_progress = False
    
    def _has_hiring_manager_data(self, jobs_df: pd.DataFrame) -> bool:
        """Check if hiring manager data exists in the dataframe."""
        return any(col in jobs_df.columns for col in ['hiring_managers_count', 'hiring_managers_names'])
    
    def _get_total_managers_count(self, jobs_df: pd.DataFrame) -> int:
        """Get total count of hiring managers found."""
        if 'hiring_managers_count' not in jobs_df.columns:
            return 0
        return int(jobs_df['hiring_managers_count'].sum())
    
    def _calculate_success_rate(self, jobs_df: pd.DataFrame, linkedin_jobs_count: int) -> float:
        """Calculate the success rate of hiring manager extraction."""
        if linkedin_jobs_count == 0 or 'hiring_managers_count' not in jobs_df.columns:
            return 0.0
        
        jobs_with_managers = (jobs_df['hiring_managers_count'] > 0).sum()
        return (jobs_with_managers / linkedin_jobs_count) * 100
    
    def _render_statistics_section(self, jobs_df: pd.DataFrame, linkedin_jobs_count: int):
        """Render hiring manager statistics."""
        st.markdown("---")
        st.markdown("#### 📊 Hiring Manager Statistics")
        
        total_jobs_with_managers = (jobs_df['hiring_managers_count'] > 0).sum()
        total_managers_found = self._get_total_managers_count(jobs_df)
        success_rate = self._calculate_success_rate(jobs_df, linkedin_jobs_count)
        avg_managers_per_job = jobs_df[jobs_df['hiring_managers_count'] > 0]['hiring_managers_count'].mean() if total_jobs_with_managers > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Jobs with Managers",
                total_jobs_with_managers,
                delta=f"of {linkedin_jobs_count} total"
            )
        
        with col2:
            st.metric(
                "Total Managers Found",
                total_managers_found,
                delta=f"{avg_managers_per_job:.1f} avg per job" if avg_managers_per_job > 0 else None
            )
        
        with col3:
            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%",
                delta="LinkedIn jobs processed"
            )
        
        with col4:
            extraction_method = "🔐 Authenticated" if st.session_state.get('hiring_auth_completed', False) else "🔓 Public"
            st.metric(
                "Extraction Method",
                extraction_method,
                delta="Current mode"
            )
    
    def _render_detailed_view_section(self, jobs_df: pd.DataFrame):
        """Render detailed hiring manager view."""
        jobs_with_managers_df = jobs_df[jobs_df['hiring_managers_count'] > 0]
        
        if len(jobs_with_managers_df) == 0:
            return
        
        st.markdown("---")
        
        with st.expander(f"👥 Detailed Hiring Manager View ({len(jobs_with_managers_df)} jobs)", expanded=False):
            # View options
            view_col1, view_col2 = st.columns([3, 1])
            
            with view_col1:
                view_mode = st.radio(
                    "Display Mode",
                    ["Compact View", "Detailed View", "Manager Directory"],
                    horizontal=True,
                    key="hiring_view_mode"
                )
            
            with view_col2:
                sort_option = st.selectbox(
                    "Sort by",
                    ["Company", "Job Title", "Manager Count", "Date"],
                    key="hiring_sort"
                )
            
            # Render based on view mode
            if view_mode == "Compact View":
                self._render_compact_view(jobs_with_managers_df)
            elif view_mode == "Detailed View":
                self._render_detailed_view(jobs_with_managers_df)
            else:  # Manager Directory
                self._render_manager_directory(jobs_with_managers_df)
    
    def _render_compact_view(self, jobs_df: pd.DataFrame):
        """Render compact view of jobs with hiring managers."""
        for _, job in jobs_df.iterrows():
            with st.container():
                job_col, manager_col, action_col = st.columns([3, 2, 1])
                
                with job_col:
                    st.markdown(f"**{job.get('title', 'Unknown Title')}**")
                    st.caption(f"📍 {job.get('company', 'Unknown Company')} • {job.get('location', 'Unknown')}")
                
                with manager_col:
                    manager_count = int(job.get('hiring_managers_count', 0))
                    st.metric("👥 Managers", manager_count)
                    
                    if job.get('hiring_managers_names'):
                        managers = job['hiring_managers_names'].split(' | ')
                        first_manager = managers[0] if managers else "Unknown"
                        if manager_count > 1:
                            st.caption(f"{first_manager} + {manager_count-1} more")
                        else:
                            st.caption(first_manager)
                
                with action_col:
                    if pd.notna(job.get('job_url')):
                        st.link_button("View Job", job['job_url'], use_container_width=True)
                
                st.divider()
    
    def _render_detailed_view(self, jobs_df: pd.DataFrame):
        """Render detailed view of jobs with hiring managers."""
        for _, job in jobs_df.iterrows():
            with st.expander(f"🏢 {job.get('company', 'Unknown')} - {job.get('title', 'Unknown Title')}", expanded=False):
                # Job information
                job_info_col, manager_info_col = st.columns([1, 1])
                
                with job_info_col:
                    st.markdown("**📋 Job Details**")
                    st.write(f"**Company:** {job.get('company', 'Unknown')}")
                    st.write(f"**Title:** {job.get('title', 'Unknown')}")
                    st.write(f"**Location:** {job.get('location', 'Unknown')}")
                    
                    if pd.notna(job.get('job_url')):
                        st.link_button("🔗 View Job Posting", job['job_url'])
                
                with manager_info_col:
                    st.markdown("**👥 Hiring Team**")
                    
                    if job.get('hiring_managers_names'):
                        managers = job['hiring_managers_names'].split(' | ')
                        titles = job.get('hiring_managers_titles', '').split(' | ')
                        profiles = job.get('hiring_managers_profiles', '').split(' | ')
                        
                        for i, manager in enumerate(managers):
                            title = titles[i] if i < len(titles) and titles[i] else "Unknown Title"
                            profile = profiles[i] if i < len(profiles) and profiles[i] else ""
                            
                            manager_container = st.container()
                            with manager_container:
                                if profile:
                                    st.markdown(f"🧑‍💼 **[{manager}]({profile})**")
                                else:
                                    st.markdown(f"🧑‍💼 **{manager}**")
                                st.caption(f"📍 {title}")
                                st.markdown("---")
    
    def _render_manager_directory(self, jobs_df: pd.DataFrame):
        """Render manager directory view."""
        st.markdown("**📇 Hiring Manager Directory**")
        
        # Collect all managers
        all_managers = []
        
        for _, job in jobs_df.iterrows():
            if job.get('hiring_managers_names'):
                managers = job['hiring_managers_names'].split(' | ')
                titles = job.get('hiring_managers_titles', '').split(' | ')
                profiles = job.get('hiring_managers_profiles', '').split(' | ')
                
                for i, manager in enumerate(managers):
                    title = titles[i] if i < len(titles) and titles[i] else "Unknown Title"
                    profile = profiles[i] if i < len(profiles) and profiles[i] else ""
                    
                    all_managers.append({
                        'name': manager,
                        'title': title,
                        'profile': profile,
                        'company': job.get('company', 'Unknown'),
                        'job_title': job.get('title', 'Unknown'),
                        'job_url': job.get('job_url', '')
                    })
        
        # Display managers in a structured format
        manager_cols = st.columns(2)
        
        for i, manager in enumerate(all_managers):
            with manager_cols[i % 2]:
                with st.container():
                    # Manager card
                    if manager['profile']:
                        st.markdown(f"### 🧑‍💼 [{manager['name']}]({manager['profile']})")
                    else:
                        st.markdown(f"### 🧑‍💼 {manager['name']}")
                    
                    st.write(f"**🏷️ Title:** {manager['title']}")
                    st.write(f"**🏢 Company:** {manager['company']}")
                    st.write(f"**💼 Job:** {manager['job_title']}")
                    
                    if manager['job_url']:
                        st.link_button("View Job", manager['job_url'], key=f"manager_job_{i}")
                    
                    st.markdown("---")

