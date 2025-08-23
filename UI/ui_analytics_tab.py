import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class AnalyticsTabUI:
    """
    Analytics Tab UI component for the Job Portal Dashboard.
    
    This class handles all analytics and visualization functionality including:
    - Job distribution charts
    - Company analytics
    - Salary analysis
    - Location insights
    - Time-based trends
    """
    
    def __init__(self):
        """Initialize the Analytics Tab UI component."""
        pass
    
    def render(self, jobs_df: pd.DataFrame) -> None:
        """
        Main render method for the analytics tab.
        
        Args:
            jobs_df: DataFrame containing job data
        """
        st.subheader("📊 Job Analytics")
        
        if jobs_df.empty:
            st.warning("No job data available for analytics.")
            return
        
        # Display summary metrics
        self._render_summary_metrics(jobs_df)
        
        # Main analytics sections
        self._render_job_distribution_charts(jobs_df)
        self._render_company_analytics(jobs_df)
        self._render_salary_analytics(jobs_df)
        self._render_location_analytics(jobs_df)
        self._render_temporal_analytics(jobs_df)
        self._render_hiring_manager_analytics(jobs_df)
    
    def _render_summary_metrics(self, jobs_df: pd.DataFrame) -> None:
        """Render key summary metrics at the top of the analytics tab."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_jobs = len(jobs_df)
            st.metric("Total Jobs", total_jobs)
        
        with col2:
            unique_companies = jobs_df['company'].nunique() if 'company' in jobs_df.columns else 0
            st.metric("Unique Companies", unique_companies)
        
        with col3:
            remote_jobs = len(jobs_df[jobs_df.get('is_remote', False) == True]) if 'is_remote' in jobs_df.columns else 0
            remote_percentage = (remote_jobs / total_jobs * 100) if total_jobs > 0 else 0
            st.metric("Remote Jobs", f"{remote_jobs} ({remote_percentage:.1f}%)")
        
        with col4:
            jobs_with_salary = len(jobs_df[jobs_df.get('min_amount', 0) > 0]) if 'min_amount' in jobs_df.columns else 0
            salary_percentage = (jobs_with_salary / total_jobs * 100) if total_jobs > 0 else 0
            st.metric("Jobs with Salary", f"{jobs_with_salary} ({salary_percentage:.1f}%)")
    
    def _render_job_distribution_charts(self, jobs_df: pd.DataFrame) -> None:
        """Render job distribution charts (pie charts and bar charts)."""
        st.subheader("📈 Job Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_site_distribution_chart(jobs_df)
        
        with col2:
            self._render_job_type_chart(jobs_df)
    
    def _render_site_distribution_chart(self, jobs_df: pd.DataFrame) -> None:
        """Render pie chart showing jobs by site/platform."""
        if 'site' not in jobs_df.columns:
            st.info("Site information not available")
            return
        
        site_counts = jobs_df['site'].value_counts()
        if len(site_counts) == 0:
            st.info("No site data available")
            return
        
        fig_site = px.pie(
            values=site_counts.values,
            names=site_counts.index,
            title="Jobs by Platform/Site",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_site.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_site, use_container_width=True)
    
    def _render_job_type_chart(self, jobs_df: pd.DataFrame) -> None:
        """Render bar chart showing top job types."""
        if 'job_type' not in jobs_df.columns or jobs_df['job_type'].isna().all():
            st.info("Job type information not available")
            return
        
        job_type_counts = jobs_df['job_type'].value_counts().head(10)
        if len(job_type_counts) == 0:
            st.info("No job type data available")
            return
        
        fig_type = px.bar(
            x=job_type_counts.index,
            y=job_type_counts.values,
            title="Top 10 Job Types",
            labels={'x': 'Job Type', 'y': 'Number of Jobs'},
            color=job_type_counts.values,
            color_continuous_scale='Blues'
        )
        fig_type.update_layout(
            xaxis_tickangle=45,
            showlegend=False
        )
        st.plotly_chart(fig_type, use_container_width=True)
    
    def _render_company_analytics(self, jobs_df: pd.DataFrame) -> None:
        """Render company-related analytics."""
        st.subheader("🏢 Company Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_top_companies_chart(jobs_df)
        
        with col2:
            self._render_remote_vs_onsite_chart(jobs_df)
    
    def _render_top_companies_chart(self, jobs_df: pd.DataFrame) -> None:
        """Render horizontal bar chart of top companies by job count."""
        if 'company' not in jobs_df.columns:
            st.info("Company information not available")
            return
        
        company_counts = jobs_df['company'].value_counts().head(15)
        if len(company_counts) == 0:
            st.info("No company data available")
            return
        
        fig_company = px.bar(
            x=company_counts.values,
            y=company_counts.index,
            orientation='h',
            title="Top 15 Companies by Job Count",
            labels={'x': 'Number of Jobs', 'y': 'Company'},
            color=company_counts.values,
            color_continuous_scale='Viridis'
        )
        fig_company.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        st.plotly_chart(fig_company, use_container_width=True)
    
    def _render_remote_vs_onsite_chart(self, jobs_df: pd.DataFrame) -> None:
        """Render chart comparing remote vs on-site jobs."""
        if 'is_remote' not in jobs_df.columns:
            st.info("Remote work information not available")
            return
        
        remote_counts = jobs_df['is_remote'].value_counts()
        
        # Create labels and values
        labels = []
        values = []
        
        if True in remote_counts.index:
            labels.append('Remote')
            values.append(remote_counts[True])
        
        if False in remote_counts.index:
            labels.append('On-site')
            values.append(remote_counts[False])
        
        if not labels:
            st.info("No remote work data available")
            return
        
        fig_remote = px.bar(
            x=labels,
            y=values,
            title="Remote vs On-site Jobs",
            labels={'x': 'Work Type', 'y': 'Number of Jobs'},
            color=labels,
            color_discrete_map={'Remote': '#2E8B57', 'On-site': '#4682B4'}
        )
        fig_remote.update_layout(showlegend=False)
        st.plotly_chart(fig_remote, use_container_width=True)
    
    def _render_salary_analytics(self, jobs_df: pd.DataFrame) -> None:
        """Render salary-related analytics."""
        if 'min_amount' not in jobs_df.columns or jobs_df['min_amount'].isna().all():
            st.info("💰 Salary information not available")
            return
        
        st.subheader("💰 Salary Analysis")
        
        # Filter out zero and null salaries
        salary_df = jobs_df[jobs_df['min_amount'] > 0].copy()
        
        if len(salary_df) == 0:
            st.info("No salary data available for analysis")
            return
        
        # Display salary summary metrics
        self._render_salary_summary_metrics(salary_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_salary_distribution_chart(salary_df)
        
        with col2:
            self._render_company_salary_chart(salary_df)
    
    def _render_salary_summary_metrics(self, salary_df: pd.DataFrame) -> None:
        """Render salary summary metrics."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_salary = salary_df['min_amount'].mean()
            st.metric("Average Salary", f"${avg_salary:,.0f}")
        
        with col2:
            median_salary = salary_df['min_amount'].median()
            st.metric("Median Salary", f"${median_salary:,.0f}")
        
        with col3:
            min_salary = salary_df['min_amount'].min()
            st.metric("Minimum Salary", f"${min_salary:,.0f}")
        
        with col4:
            max_salary = salary_df['min_amount'].max()
            st.metric("Maximum Salary", f"${max_salary:,.0f}")
    
    def _render_salary_distribution_chart(self, salary_df: pd.DataFrame) -> None:
        """Render salary distribution histogram."""
        fig_salary_hist = px.histogram(
            salary_df,
            x='min_amount',
            title="Salary Distribution",
            nbins=20,
            labels={'min_amount': 'Salary ($)', 'count': 'Number of Jobs'}
        )
        fig_salary_hist.update_layout(
            bargap=0.1,
            showlegend=False
        )
        st.plotly_chart(fig_salary_hist, use_container_width=True)
    
    def _render_company_salary_chart(self, salary_df: pd.DataFrame) -> None:
        """Render average salary by company chart."""
        if 'company' not in salary_df.columns:
            st.info("Company information not available for salary analysis")
            return
        
        company_salary = salary_df.groupby('company')['min_amount'].agg(['mean', 'count']).sort_values('mean', ascending=False)
        
        # Filter companies with at least 2 job postings
        company_salary_filtered = company_salary[company_salary['count'] >= 2].head(10)
        
        if len(company_salary_filtered) == 0:
            st.info("Insufficient data for company salary comparison")
            return
        
        fig_company_salary = px.bar(
            x=company_salary_filtered['mean'],
            y=company_salary_filtered.index,
            orientation='h',
            title="Average Salary by Company (Top 10, min 2 jobs)",
            labels={'x': 'Average Salary ($)', 'y': 'Company'},
            color=company_salary_filtered['mean'],
            color_continuous_scale='RdYlGn'
        )
        fig_company_salary.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        st.plotly_chart(fig_company_salary, use_container_width=True)
    
    def _render_location_analytics(self, jobs_df: pd.DataFrame) -> None:
        """Render location-based analytics."""
        if 'location' not in jobs_df.columns:
            return
        
        st.subheader("📍 Location Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_top_locations_chart(jobs_df)
        
        with col2:
            self._render_location_salary_chart(jobs_df)
    
    def _render_top_locations_chart(self, jobs_df: pd.DataFrame) -> None:
        """Render top locations by job count."""
        location_counts = jobs_df['location'].value_counts().head(15)
        
        if len(location_counts) == 0:
            st.info("No location data available")
            return
        
        fig_location = px.bar(
            x=location_counts.values,
            y=location_counts.index,
            orientation='h',
            title="Top 15 Locations by Job Count",
            labels={'x': 'Number of Jobs', 'y': 'Location'},
            color=location_counts.values,
            color_continuous_scale='Plasma'
        )
        fig_location.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        st.plotly_chart(fig_location, use_container_width=True)
    
    def _render_location_salary_chart(self, jobs_df: pd.DataFrame) -> None:
        """Render average salary by location."""
        if 'min_amount' not in jobs_df.columns:
            st.info("Salary information not available for location analysis")
            return
        
        # Filter jobs with salary data
        salary_location_df = jobs_df[(jobs_df['min_amount'] > 0) & (jobs_df['location'].notna())]
        
        if len(salary_location_df) == 0:
            st.info("No salary data available for location analysis")
            return
        
        location_salary = salary_location_df.groupby('location')['min_amount'].agg(['mean', 'count']).sort_values('mean', ascending=False)
        
        # Filter locations with at least 2 job postings
        location_salary_filtered = location_salary[location_salary['count'] >= 2].head(10)
        
        if len(location_salary_filtered) == 0:
            st.info("Insufficient data for location salary comparison")
            return
        
        fig_location_salary = px.bar(
            x=location_salary_filtered['mean'],
            y=location_salary_filtered.index,
            orientation='h',
            title="Average Salary by Location (Top 10, min 2 jobs)",
            labels={'x': 'Average Salary ($)', 'y': 'Location'},
            color=location_salary_filtered['mean'],
            color_continuous_scale='Cividis'
        )
        fig_location_salary.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        st.plotly_chart(fig_location_salary, use_container_width=True)
    
    def _render_temporal_analytics(self, jobs_df: pd.DataFrame) -> None:
        """Render time-based analytics if date information is available."""
        if 'date_posted' not in jobs_df.columns:
            return
        
        # Try to parse date_posted column
        try:
            jobs_df_temp = jobs_df.copy()
            jobs_df_temp['date_posted'] = pd.to_datetime(jobs_df_temp['date_posted'], errors='coerce')
            jobs_df_temp = jobs_df_temp[jobs_df_temp['date_posted'].notna()]
            
            if len(jobs_df_temp) == 0:
                return
            
            st.subheader("📅 Temporal Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                self._render_jobs_over_time_chart(jobs_df_temp)
            
            with col2:
                self._render_jobs_by_day_of_week_chart(jobs_df_temp)
        
        except Exception as e:
            # If date parsing fails, skip temporal analytics
            pass
    
    def _render_jobs_over_time_chart(self, jobs_df_temp: pd.DataFrame) -> None:
        """Render jobs posted over time."""
        jobs_df_temp['date_only'] = jobs_df_temp['date_posted'].dt.date
        daily_counts = jobs_df_temp['date_only'].value_counts().sort_index()
        
        fig_time = px.line(
            x=daily_counts.index,
            y=daily_counts.values,
            title="Jobs Posted Over Time",
            labels={'x': 'Date', 'y': 'Number of Jobs Posted'}
        )
        fig_time.update_layout(showlegend=False)
        st.plotly_chart(fig_time, use_container_width=True)
    
    def _render_jobs_by_day_of_week_chart(self, jobs_df_temp: pd.DataFrame) -> None:
        """Render jobs posted by day of week."""
        jobs_df_temp['day_of_week'] = jobs_df_temp['date_posted'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = jobs_df_temp['day_of_week'].value_counts().reindex(day_order, fill_value=0)
        
        fig_dow = px.bar(
            x=day_counts.index,
            y=day_counts.values,
            title="Jobs Posted by Day of Week",
            labels={'x': 'Day of Week', 'y': 'Number of Jobs Posted'},
            color=day_counts.values,
            color_continuous_scale='Blues'
        )
        fig_dow.update_layout(showlegend=False)
        st.plotly_chart(fig_dow, use_container_width=True)
    
    def _render_hiring_manager_analytics(self, jobs_df: pd.DataFrame) -> None:
        """Render hiring manager analytics if available."""
        if 'hiring_managers_count' not in jobs_df.columns:
            return
        
        st.subheader("👥 Hiring Manager Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Jobs with vs without hiring managers
            has_hm = jobs_df['hiring_managers_count'] > 0
            hm_counts = has_hm.value_counts()
            
            labels = ['With Hiring Managers' if True in hm_counts.index else 'No Data',
                     'Without Hiring Managers' if False in hm_counts.index else 'No Data']
            values = [hm_counts.get(True, 0), hm_counts.get(False, 0)]
            
            fig_hm = px.pie(
                values=values,
                names=labels,
                title="Jobs with Hiring Manager Information",
                color_discrete_map={
                    'With Hiring Managers': '#2E8B57',
                    'Without Hiring Managers': '#CD5C5C'
                }
            )
            st.plotly_chart(fig_hm, use_container_width=True)
        
        with col2:
            # Distribution of hiring manager count
            hm_distribution = jobs_df[jobs_df['hiring_managers_count'] > 0]['hiring_managers_count'].value_counts().sort_index()
            
            if len(hm_distribution) > 0:
                fig_hm_dist = px.bar(
                    x=hm_distribution.index,
                    y=hm_distribution.values,
                    title="Distribution of Hiring Manager Count",
                    labels={'x': 'Number of Hiring Managers', 'y': 'Number of Jobs'},
                    color=hm_distribution.values,
                    color_continuous_scale='Greens'
                )
                fig_hm_dist.update_layout(showlegend=False)
                st.plotly_chart(fig_hm_dist, use_container_width=True)
            else:
                st.info("No hiring manager data available for distribution analysis")
    