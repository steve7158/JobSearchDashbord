import streamlit as st
import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import io

class AppliedJobsTabUI:
    """UI component for managing applied jobs history."""
    
    def __init__(self):
        self.history_file = "Data/applicationHistory/history.csv"
        self.columns = [
            'application_date', 'title', 'company', 'location', 'job_url', 
            'source', 'status', 'shortlisted', 'notes'
        ]
        self._ensure_history_file_exists()
    
    def _ensure_history_file_exists(self):
        """Ensure the history file and directory exist."""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        if not os.path.exists(self.history_file):
            # Create empty CSV with headers
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(self.history_file, index=False)
    
    def load_application_history(self) -> pd.DataFrame:
        """Load application history from CSV file."""
        try:
            if os.path.exists(self.history_file):
                df = pd.read_csv(self.history_file)
                if not df.empty:
                    # Convert application_date to datetime
                    df['application_date'] = pd.to_datetime(df['application_date'], errors='coerce')
                    
                    # Ensure string columns are properly typed
                    string_columns = ['title', 'company', 'location', 'job_url', 'source', 'status', 'shortlisted', 'notes']
                    for col in string_columns:
                        if col in df.columns:
                            df[col] = df[col].astype(str)
                            # Replace 'nan' strings with empty strings
                            df[col] = df[col].replace('nan', '')
                
                return df
            else:
                return pd.DataFrame(columns=self.columns)
        except Exception as e:
            st.error(f"Error loading application history: {e}")
            return pd.DataFrame(columns=self.columns)
    
    def save_application_history(self, df: pd.DataFrame):
        """Save application history to CSV file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # Clean up the dataframe before saving
            df_clean = df.copy()
            
            # Replace NaN values with empty strings for string columns
            string_columns = ['title', 'company', 'location', 'job_url', 'source', 'status', 'shortlisted', 'notes']
            for col in string_columns:
                if col in df_clean.columns:
                    df_clean[col] = df_clean[col].fillna('')
            
            df_clean.to_csv(self.history_file, index=False)
            return True
        except Exception as e:
            st.error(f"Error saving application history: {e}")
            return False
    
    def add_application_from_job_search(self, job_row: pd.Series) -> bool:
        """Add application from job search results."""
        try:
            job_data = {
                'title': job_row.get('title', 'Unknown'),
                'company': job_row.get('company', 'Unknown'),
                'location': job_row.get('location', 'Unknown'),
                'job_url': job_row.get('job_url', ''),
                'source': job_row.get('site', 'Job Search'),
                'status': 'Applied',
                'shortlisted': 'Pending',
                'notes': f"Applied via job search on {datetime.now().strftime('%Y-%m-%d')}"
            }
            return self.add_application(job_data)
        except Exception as e:
            st.error(f"Error adding application from job search: {e}")
            return False
    
    def add_application(self, job_data: Dict[str, Any]) -> bool:
        """Add a new job application to history."""
        try:
            # Load existing history
            df = self.load_application_history()
            
            # Create new application record with proper string handling
            new_application = {
                'application_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'title': str(job_data.get('title', 'Unknown')),
                'company': str(job_data.get('company', 'Unknown')),
                'location': str(job_data.get('location', 'Unknown')),
                'job_url': str(job_data.get('job_url', '')),
                'source': str(job_data.get('source', 'Manual')),
                'status': str(job_data.get('status', 'Applied')),
                'shortlisted': str(job_data.get('shortlisted', 'Pending')),
                'notes': str(job_data.get('notes', ''))
            }
            
            # Add to dataframe
            new_df = pd.concat([df, pd.DataFrame([new_application])], ignore_index=True)
            
            # Save to file
            return self.save_application_history(new_df)
        except Exception as e:
            st.error(f"Error adding application: {e}")
            return False
    
    def _render_application_form(self):
        """Render form to add new job application manually."""
        with st.expander("➕ Add New Application", expanded=False):
            st.subheader("Manual Job Application Entry")
            
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Job Title", key="new_job_title")
                company = st.text_input("Company", key="new_job_company")
                location = st.text_input("Location", key="new_job_location")
                source = st.selectbox("Source", 
                                    ["LinkedIn", "Indeed", "Glassdoor", "Company Website", "Referral", "Other"],
                                    key="new_job_source")
            
            with col2:
                job_url = st.text_input("Job URL (optional)", key="new_job_url")
                status = st.selectbox("Application Status",
                                    ["Applied", "Under Review", "Interview Scheduled", "Rejected", "Offer"],
                                    key="new_job_status")
                shortlisted = st.selectbox("Shortlisted",
                                         ["Pending", "Yes", "No"],
                                         key="new_job_shortlisted")
                notes = st.text_area("Notes", key="new_job_notes")
            
            if st.button("Add Application", type="primary"):
                if title and company:
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'job_url': job_url,
                        'source': source,
                        'status': status,
                        'shortlisted': shortlisted,
                        'notes': notes
                    }
                    
                    if self.add_application(job_data):
                        st.success("✅ Application added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add application")
                else:
                    st.warning("⚠️ Please fill in at least Job Title and Company")
    
    def _render_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Render filters for the applied jobs."""
        if df.empty:
            return df
        
        st.subheader("🔍 Filter Applications")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Company filter
            companies = ['All'] + sorted(df['company'].dropna().unique().tolist())
            selected_company = st.selectbox("Company", companies, key="filter_company")
        
        with col2:
            # Status filter
            statuses = ['All'] + sorted(df['status'].dropna().unique().tolist())
            selected_status = st.selectbox("Status", statuses, key="filter_status")
        
        with col3:
            # Shortlisted filter
            shortlisted_options = ['All'] + sorted(df['shortlisted'].dropna().unique().tolist())
            selected_shortlisted = st.selectbox("Shortlisted", shortlisted_options, key="filter_shortlisted")
        
        with col4:
            # Source filter
            sources = ['All'] + sorted(df['source'].dropna().unique().tolist())
            selected_source = st.selectbox("Source", sources, key="filter_source")
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_company != 'All':
            filtered_df = filtered_df[filtered_df['company'] == selected_company]
        
        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['status'] == selected_status]
        
        if selected_shortlisted != 'All':
            filtered_df = filtered_df[filtered_df['shortlisted'] == selected_shortlisted]
        
        if selected_source != 'All':
            filtered_df = filtered_df[filtered_df['source'] == selected_source]
        
        return filtered_df
    
    def _render_summary_metrics(self, df: pd.DataFrame):
        """Render summary metrics for applications."""
        if df.empty:
            return
        
        st.subheader("📊 Application Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_apps = len(df)
            st.metric("Total Applications", total_apps)
        
        with col2:
            shortlisted = len(df[df['shortlisted'] == 'Yes'])
            st.metric("Shortlisted", shortlisted)
        
        with col3:
            pending = len(df[df['shortlisted'] == 'Pending'])
            st.metric("Pending", pending)
        
        with col4:
            rejected = len(df[df['status'] == 'Rejected'])
            st.metric("Rejected", rejected)
        
        with col5:
            offers = len(df[df['status'] == 'Offer'])
            st.metric("Offers", offers)
    
    def _render_editable_table(self, df: pd.DataFrame):
        """Render editable table for application management."""
        if df.empty:
            st.info("📝 No applications found. Add your first application using the form above.")
            return df
        
        st.subheader("📋 Application Management")
        
        # Ensure proper data types before displaying
        df_display = df.copy()
        
        # Ensure string columns are properly typed
        string_columns = ['title', 'company', 'location', 'job_url', 'source', 'status', 'shortlisted', 'notes']
        for col in string_columns:
            if col in df_display.columns:
                df_display[col] = df_display[col].astype(str)
                df_display[col] = df_display[col].replace('nan', '')
        
        # Create editable dataframe
        edited_df = st.data_editor(
            df_display,
            column_config={
                "application_date": st.column_config.DatetimeColumn(
                    "Application Date",
                    width="medium",
                    format="DD/MM/YYYY HH:mm"
                ),
                "title": st.column_config.TextColumn(
                    "Job Title",
                    width="large"
                ),
                "company": st.column_config.TextColumn(
                    "Company",
                    width="medium"
                ),
                "location": st.column_config.TextColumn(
                    "Location", 
                    width="medium"
                ),
                "job_url": st.column_config.LinkColumn(
                    "Job URL",
                    width="small"
                ),
                "source": st.column_config.SelectboxColumn(
                    "Source",
                    options=["LinkedIn", "Indeed", "Glassdoor", "Company Website", "Referral", "Other"],
                    width="small"
                ),
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Applied", "Under Review", "Interview Scheduled", "Rejected", "Offer"],
                    width="medium"
                ),
                "shortlisted": st.column_config.SelectboxColumn(
                    "Shortlisted",
                    options=["Pending", "Yes", "No"],
                    width="small"
                ),
                "notes": st.column_config.TextColumn(
                    "Notes",
                    width="large"
                )
            },
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # Save changes button
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("💾 Save Changes", type="primary"):
                if self.save_application_history(edited_df):
                    st.success("✅ Changes saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save changes")
        
        with col2:
            if st.button("🔄 Refresh Data"):
                st.rerun()
        
        return edited_df
    
    def _render_export_options(self, df: pd.DataFrame):
        """Render export options for application data."""
        if df.empty:
            return
        
        st.subheader("📤 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Export as CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="📄 Download as CSV",
                data=csv_data,
                file_name=f"applied_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Export as Excel
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_data = excel_buffer.getvalue()
            
            st.download_button(
                label="📊 Download as Excel",
                data=excel_data,
                file_name=f"applied_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            # Export filtered data
            if st.button("🎯 Export Filtered Data", use_container_width=True):
                st.info("💡 Use the filters above, then click download buttons to export filtered data")
    
    def render(self):
        """Render the Applied Jobs tab."""
        st.header("💼 Applied Jobs Management")
        
        # Add manual application form
        self._render_application_form()
        
        st.markdown("---")
        
        # Load application history
        df = self.load_application_history()
        
        # Show summary metrics
        self._render_summary_metrics(df)
        
        st.markdown("---")
        
        # Render filters
        filtered_df = self._render_filters(df)
        
        st.markdown("---")
        
        # Show filtered count
        if not filtered_df.empty:
            total_count = len(df)
            filtered_count = len(filtered_df)
            st.info(f"📊 Showing {filtered_count} of {total_count} applications")
        
        # Render editable table
        edited_df = self._render_editable_table(filtered_df)
        
        st.markdown("---")
        
        # Export options
        self._render_export_options(filtered_df if not filtered_df.empty else df)
        
        # Data management section
        with st.expander("🔧 Data Management", expanded=False):
            st.subheader("Data Management Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📁 File Information")
                st.info(f"**File Location:** `{self.history_file}`")
                if os.path.exists(self.history_file):
                    file_size = os.path.getsize(self.history_file)
                    st.info(f"**File Size:** {file_size} bytes")
                    mod_time = datetime.fromtimestamp(os.path.getmtime(self.history_file))
                    st.info(f"**Last Modified:** {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                st.subheader("⚠️ Danger Zone")
                if st.button("🗑️ Clear All Data", type="secondary"):
                    if st.button("🔴 Confirm Delete", type="secondary"):
                        empty_df = pd.DataFrame(columns=self.columns)
                        if self.save_application_history(empty_df):
                            st.success("✅ All application data cleared")
                            st.rerun()
                        else:
                            st.error("❌ Failed to clear data")
