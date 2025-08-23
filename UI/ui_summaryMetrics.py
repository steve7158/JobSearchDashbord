
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
from datetime import datetime


class SummaryMetricsUI:
    """
    UI component class for displaying job summary metrics and detailed job listings.
    
    This class provides a complete interface for:
    - Job summary statistics and metrics
    - Enhanced job listings with logos and details
    - Hiring manager information display
    - Job action buttons and analytics
    - Multiple view modes and pagination
    """
    
    def __init__(self):
        """Initialize the SummaryMetricsUI component."""
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables for summary metrics operations."""
        session_defaults = {
            'summary_display_columns': [],
            'summary_current_page': 1,
            'summary_rows_per_page': 10,
            'summary_show_logos': True,
            'summary_view_mode': 'Detailed'
        }
        
        for key, default_value in session_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def render(self, jobs_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Render the complete summary metrics UI component.
        
        Args:
            jobs_df: DataFrame containing job data
            
        Returns:
            Dictionary containing component state and metrics
        """
        if jobs_df.empty:
            self._render_empty_state()
            return {'total_jobs': 0, 'has_data': False}
        
        # Render summary metrics
        metrics = self.render_summary_metrics(jobs_df)
        
        return {
            'total_jobs': len(jobs_df),
            'has_data': True,
            'metrics': metrics,
            'unique_companies': jobs_df['company'].nunique() if 'company' in jobs_df.columns else 0,
            'remote_jobs': jobs_df['is_remote'].sum() if 'is_remote' in jobs_df.columns else 0
        }
    
    def _render_empty_state(self):
        """Render empty state when no job data is available."""
        st.info("📋 No job data available. Search for jobs to see metrics and listings.")

    def render_summary_metrics(self, jobs_df: pd.DataFrame) -> Dict[str, Any]:
        """Render job summary metrics with enhanced formatting."""
        st.markdown("### 📊 Job Summary Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Calculate metrics
        total_jobs = len(jobs_df)
        unique_companies = jobs_df['company'].nunique() if 'company' in jobs_df.columns else 0
        remote_jobs = jobs_df['is_remote'].sum() if 'is_remote' in jobs_df.columns else 0
        sites_count = jobs_df['site'].nunique() if 'site' in jobs_df.columns else 0
        avg_salary = jobs_df['min_amount'].mean() if 'min_amount' in jobs_df.columns and not jobs_df['min_amount'].isna().all() else 0
        
        with col1:
            st.metric(
                "Total Jobs", 
                total_jobs,
                delta=f"{total_jobs} found" if total_jobs > 0 else None
            )
        
        with col2:
            diversity_pct = (unique_companies/total_jobs)*100 if total_jobs > 0 else 0
            st.metric(
                "Unique Companies", 
                unique_companies,
                delta=f"{diversity_pct:.1f}% diversity" if total_jobs > 0 else None
            )
        
        with col3:
            remote_percentage = (remote_jobs/total_jobs)*100 if total_jobs > 0 else 0
            st.metric(
                "Remote Jobs", 
                remote_jobs,
                delta=f"{remote_percentage:.1f}% remote" if total_jobs > 0 else None
            )
        
        with col4:
            st.metric(
                "Sites Searched", 
                sites_count,
                delta="job sources"
            )
        
        with col5:
            salary_display = f"${avg_salary:,.0f}" if avg_salary > 0 else "N/A"
            st.metric(
                "Avg Min Salary", 
                salary_display,
                delta="average minimum" if avg_salary > 0 else None
            )
        
        return {
            'total_jobs': total_jobs,
            'unique_companies': unique_companies,
            'remote_jobs': remote_jobs,
            'sites_count': sites_count,
            'avg_salary': avg_salary,
            'remote_percentage': remote_percentage
        }
    