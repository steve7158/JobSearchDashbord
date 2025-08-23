import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from Utils.prompt import SUMERIZE_PROMPT_TEMPLATE


class JobListTabUI:
    """
    Job List Tab UI component for the Job Portal Dashboard.
    
    This class handles all job listing display functionality including:
    - Multiple display formats (table, card, compact)
    - Column selection and customization
    - Pagination and sorting
    - Job details with expandable sections
    - Hiring manager information display
    - Action buttons and quick actions
    - Search and filtering within the list
    - Bulk operations on jobs
    """
    
    def __init__(self):
        """Initialize the Job List Tab UI component."""
        self.session_key_prefix = "job_list_tab_"
        self._initialize_session_state()
    
    def _initialize_session_state(self) -> None:
        """Initialize session state variables for the job list tab."""
        session_defaults = {
            f"{self.session_key_prefix}display_format": "card",
            f"{self.session_key_prefix}rows_per_page": 10,
            f"{self.session_key_prefix}show_logos": True,
            f"{self.session_key_prefix}selected_jobs": [],
            f"{self.session_key_prefix}sort_column": "date_posted",
            f"{self.session_key_prefix}sort_ascending": False,
        }
        
        for key, default_value in session_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
        
    def render(self, jobs_df: pd.DataFrame):
        """Render the job list tab."""
        st.subheader("📋 Job Listings")
        
        # Display options
        col1, col2 = st.columns([3, 1])
        with col1:
            show_columns = st.multiselect(
                "Select columns to display",
                jobs_df.columns.tolist(),
                default=['title', 'company', 'location', 'site', 'date_posted', 'job_type', 'is_remote'] if len(jobs_df.columns) > 0 else [],
                key="display_columns"
            )
        
        with col2:
            rows_per_page = st.selectbox("Rows per page", [5, 10, 15, 20], index=1)
        
        # Option to show logos
        show_logos = st.checkbox("Show Company Logos", value=True)
        
        if show_columns:
            # Pagination
            total_rows = len(jobs_df)
            total_pages = (total_rows - 1) // rows_per_page + 1
            
            if total_pages > 1:
                page = st.selectbox(f"Page (1-{total_pages})", range(1, total_pages + 1))
                start_idx = (page - 1) * rows_per_page
                end_idx = start_idx + rows_per_page
                display_df = jobs_df.iloc[start_idx:end_idx]
            else:
                display_df = jobs_df
            
            if show_logos and 'company_logo' in jobs_df.columns:
                self._render_jobs_with_logos(display_df)
            else:
                st.dataframe(
                    display_df[show_columns] if show_columns else display_df,
                    use_container_width=True,
                    hide_index=True
                )
    
    def _render_jobs_with_logos(self, display_df: pd.DataFrame):
        """Render jobs with company logos."""
        st.subheader("Job Listings with Company Logos")
        
        for idx, job in display_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 4, 1])
                
                with col1:
                    # Display company logo
                    if pd.notna(job.get('company_logo')) and job.get('company_logo'):
                        try:
                            st.image(
                                job['company_logo'], 
                                width=80,
                                caption=job.get('company', 'Unknown')
                            )
                        except Exception:
                            st.write(f"🏢 {job.get('company', 'Unknown')}")
                    else:
                        st.write(f"🏢 {job.get('company', 'Unknown')}")
                
                with col2:
                    self._render_job_details(job)
                
                with col3:
                    self._render_job_action_buttons(job, idx)
                
                st.divider()
    
    def _render_job_details(self, job: pd.Series):
        """Render detailed job information."""
        # Basic job info
        st.markdown(f"**{job.get('title', 'No Title')}**")
        st.write(f"**Company:** {job.get('company', 'Unknown')}")
        st.write(f"**Location:** {job.get('location', 'Unknown')}")
        st.write(f"**Site:** {job.get('site', 'Unknown')}")
        
        if pd.notna(job.get('date_posted')):
            st.write(f"**Posted:** {job.get('date_posted')}")
        
        if pd.notna(job.get('job_type')):
            st.write(f"**Type:** {job.get('job_type')}")
        
        if pd.notna(job.get('is_remote')):
            remote_text = "✅ Remote" if job.get('is_remote') else "🏢 On-site"
            st.write(f"**Work Mode:** {remote_text}")
        
        # Salary information
        if pd.notna(job.get('min_amount')) and job.get('min_amount') > 0:
            salary_text = f"${job.get('min_amount'):,.0f}"
            if pd.notna(job.get('max_amount')) and job.get('max_amount') > 0:
                salary_text += f" - ${job.get('max_amount'):,.0f}"
            if pd.notna(job.get('currency')):
                salary_text += f" {job.get('currency')}"
            st.write(f"**Salary:** {salary_text}")
        
        # Hiring Manager Information
        self._render_hiring_manager_info(job)
        
        # Job description in collapsible menu
        if pd.notna(job.get('description')) and job.get('description'):
            with st.expander("📝 View Job Description"):
                description = str(job.get('description'))
                
                # Add summarize button
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("🤖 Summarize", key=f"summarize_{hash(str(job.get('title', 'unknown')))}_{job.name if hasattr(job, 'name') else 'job'}"):
                        self._summarize_job_description(description)
                
                with col1:
                    st.markdown("**Full Description:**")
                
                st.markdown(description)
        
        # Additional details in collapsible menu
        with st.expander("ℹ️ Additional Details"):
            self._render_additional_job_details(job)
    
    def _render_hiring_manager_info(self, job: pd.Series):
        """Render hiring manager information for a job."""
        if 'hiring_managers_count' in job.index and job.get('hiring_managers_count', 0) > 0:
            hiring_count = int(job.get('hiring_managers_count', 0))
            st.write(f"**👥 Hiring Managers:** {hiring_count} found")
            
            if job.get('hiring_managers_names'):
                managers = str(job['hiring_managers_names']).split(' | ')
                titles = str(job.get('hiring_managers_titles', '')).split(' | ')
                profiles = str(job.get('hiring_managers_profiles', '')).split(' | ')
                
                # Show hiring managers in a compact format
                manager_info = []
                for i, manager in enumerate(managers[:3]):  # Limit to first 3 for display
                    if manager.strip():
                        title = titles[i] if i < len(titles) and titles[i].strip() else "Unknown Title"
                        profile = profiles[i] if i < len(profiles) and profiles[i].strip() else ""
                        
                        if profile:
                            manager_info.append(f"[{manager}]({profile}) ({title})")
                        else:
                            manager_info.append(f"{manager} ({title})")
                
                if manager_info:
                    st.markdown("**Hiring Team:** " + " • ".join(manager_info))
                    if len(managers) > 3:
                        st.caption(f"+ {len(managers) - 3} more hiring managers")
        elif 'hiring_manager_fetch_success' in job.index and job.get('hiring_manager_fetch_success') == False:
            if 'linkedin.com' in str(job.get('job_url', '')):
                st.write("**👥 Hiring Managers:** ❌ Not found")
        elif 'linkedin.com' in str(job.get('job_url', '')):
            st.write("**👥 Hiring Managers:** 🔍 Not fetched yet")
    
    def _render_additional_job_details(self, job: pd.Series):
        """Render additional job details in expandable section."""
        details_cols = st.columns(2)
        
        with details_cols[0]:
            if pd.notna(job.get('job_level')):
                st.write(f"**Level:** {job.get('job_level')}")
            if pd.notna(job.get('job_function')):
                st.write(f"**Function:** {job.get('job_function')}")
            if pd.notna(job.get('listing_type')):
                st.write(f"**Listing Type:** {job.get('listing_type')}")
            if pd.notna(job.get('experience_range')):
                st.write(f"**Experience:** {job.get('experience_range')}")
        
        with details_cols[1]:
            if pd.notna(job.get('company_industry')):
                st.write(f"**Industry:** {job.get('company_industry')}")
            if pd.notna(job.get('company_num_employees')):
                st.write(f"**Company Size:** {job.get('company_num_employees')} employees")
            if pd.notna(job.get('company_rating')):
                st.write(f"**Rating:** ⭐ {job.get('company_rating')}")
            if pd.notna(job.get('skills')):
                skills = str(job.get('skills'))
                if len(skills) > 100:
                    skills = skills[:100] + "..."
                st.write(f"**Skills:** {skills}")
        
        # Company description if available
        if pd.notna(job.get('company_description')):
            st.write("**Company Description:**")
            company_desc = str(job.get('company_description'))
            if len(company_desc) > 300:
                company_desc = company_desc[:300] + "..."
            st.write(company_desc)
    
    def _render_job_action_buttons(self, job: pd.Series, job_index: int = None):
        """Render action buttons for a job."""
        # Single column with vertical stack of buttons
        if pd.notna(job.get('job_url')):
            st.link_button("🔗 View Job", job['job_url'], use_container_width=True)
        
        if pd.notna(job.get('job_url_direct')):
            st.link_button("🎯 Direct Link", job['job_url_direct'], use_container_width=True)
        
        if pd.notna(job.get('company_url')):
            st.link_button("🏢 Company Page", job['company_url'], use_container_width=True)
        
        # Mark as Applied button
        if st.button("✅ Mark Applied", key=f"apply_{job_index}_{job.get('title', 'unknown')}", use_container_width=True):
            if self._mark_job_as_applied(job):
                st.success("Application recorded!")
                st.rerun()
            else:
                st.error("Failed to record application")
        
        # Generate Cover Letter button (only if job description is available)
        if pd.notna(job.get('description')) and job.get('description'):
            if st.button("📄 Generate Cover Letter", key=f"cover_letter_{job_index}_{job.get('title', 'unknown')}", use_container_width=True):
                self._generate_cover_letter(job)
            else:
                st.error("Failed to record application")
    
    def _mark_job_as_applied(self, job: pd.Series) -> bool:
        """Mark a job as applied by adding it to application history."""
        try:
            from UI.ui_applied_jobs_tab import AppliedJobsTabUI
            applied_jobs_ui = AppliedJobsTabUI()
            return applied_jobs_ui.add_application_from_job_search(job)
        except Exception as e:
            st.error(f"Error marking job as applied: {e}")
            return False
    
    def _summarize_job_description(self, description: str):
        """Summarize job description using AI service."""
        try:
            from services.ai_service import ai_service
            
            if not ai_service.is_available():
                st.error("AI service is not available. Please check your API keys.")
                return
            
            # Create a prompt for summarizing the job description
            prompt = SUMERIZE_PROMPT_TEMPLATE.format(description=description)
            
            with st.spinner("Generating summary..."):
                summary = ai_service.get_chatcompletion(
                    prompt=prompt,
                    max_tokens=500,
                    temperature=0.3
                )
            
            if summary:
                st.success("Summary generated!")
                st.markdown("**AI Summary:**")
                st.markdown(summary)
            else:
                st.error("Failed to generate summary. Please try again.")
                
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")
            st.info("Make sure the AI service is properly configured with valid API keys.")
    
    def _generate_cover_letter(self, job: pd.Series):
        """Generate cover letter for the job using AI service."""
        try:
            from services.cover_letter_service import CoverLetterGenerator
            
            generator = CoverLetterGenerator()
            
            # Check if AI service is available
            if not generator.ai_service.is_available():
                st.error("AI service is not available. Please check your API keys.")
                return
            
            description = str(job.get('description', ''))
            
            with st.spinner("Generating personalized cover letter..."):
                html_file, cover_letter_data = generator.generate_cover_letter_from_job(
                    job_description=description
                )
            
            if html_file and cover_letter_data:
                st.success("Cover letter generated successfully!")
                
                # Show summary of generated cover letter
                st.markdown("### 📄 Cover Letter Generated")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Company:** {cover_letter_data.get('company_name', 'Unknown')}")
                    st.markdown(f"**Position:** {cover_letter_data.get('position_title', 'Unknown')}")
                
                with col2:
                    st.markdown(f"**Hiring Manager:** {cover_letter_data.get('hiring_manager_name', 'Unknown')}")
                    st.markdown(f"**File:** {html_file}")
                
                # Show a preview of the opening paragraph
                if cover_letter_data.get('opening_paragraph'):
                    with st.expander("📖 Preview Opening Paragraph"):
                        st.markdown(f"*{cover_letter_data.get('opening_paragraph')}*")
                
                # Provide download/view options
                col1, col2 = st.columns(2)
                with col1:
                    # Create download button for the HTML file
                    try:
                        with open(html_file, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        st.download_button(
                            label="📥 Download HTML",
                            data=html_content,
                            file_name=f"cover_letter_{cover_letter_data.get('company_name', 'unknown').replace(' ', '_')}.html",
                            mime="text/html",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error creating download: {e}")
                
                with col2:
                    st.info("💡 Open the HTML file in your browser and print to PDF")
            
            else:
                st.error("Failed to generate cover letter. Please try again.")
                
        except Exception as e:
            st.error(f"Error generating cover letter: {str(e)}")
            st.info("Make sure the AI service is properly configured with valid API keys.")
