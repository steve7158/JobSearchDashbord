
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

# Import AI helper
from .helper_ai_filter_tab import AIFilterHelper


class FilterTabUI:
    """
    Filter Tab UI component for the Job Portal Dashboard.
    
    This class handles all job filtering functionality including:
    - Basic filters (company, job type, remote work)
    - Advanced filters (salary range, date range, location)
    - Text search and keyword filtering
    - Filter combinations and saved filter sets
    - Filtered results display with multiple view options
    """
    
    def __init__(self):
        """Initialize the Filter Tab UI component."""
        self.session_key_prefix = "filter_tab_"
        self.ai_helper = AIFilterHelper(self.session_key_prefix)
        self._initialize_session_state()
    
    def _initialize_session_state(self) -> None:
        """Initialize session state variables for filter persistence."""
        if f"{self.session_key_prefix}saved_filters" not in st.session_state:
            st.session_state[f"{self.session_key_prefix}saved_filters"] = {}
        
        if f"{self.session_key_prefix}filter_history" not in st.session_state:
            st.session_state[f"{self.session_key_prefix}filter_history"] = []
    
    def render(self, jobs_df: pd.DataFrame) -> None:
        """
        Main render method for the filter tab.
        
        Args:
            jobs_df: DataFrame containing job data
        """
        st.subheader("🔍 Filter Jobs")
        
        if jobs_df.empty:
            st.warning("No job data available for filtering.")
            return
        
        # AI-powered search section
        ai_filtered_df = self.ai_helper.render_ai_search_section(jobs_df)
        
        # Use AI-filtered results if available, otherwise use original
        current_jobs_df = ai_filtered_df if ai_filtered_df is not None else jobs_df
        
        # Filter summary
        self._render_filter_summary(current_jobs_df)
        
        # Main filter controls
        filters = self._render_filter_controls(current_jobs_df)
        
        # Advanced filter options
        advanced_filters = self._render_advanced_filters(current_jobs_df)
        
        # Combine all filters
        all_filters = {**filters, **advanced_filters}
        
        # Apply filters
        filtered_df = self._apply_filters(current_jobs_df, all_filters)
        
        # Save filter to history
        self._save_filter_to_history(all_filters, len(filtered_df))
        
        # Display results
        self._render_filter_results(filtered_df, jobs_df)
        
        # Filter management
        self._render_filter_management(all_filters)
    
    def _render_filter_summary(self, jobs_df: pd.DataFrame) -> None:
        """Render summary of available filter options."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            unique_companies = jobs_df['company'].nunique() if 'company' in jobs_df.columns else 0
            st.metric("Companies", unique_companies)
        
        with col2:
            unique_job_types = jobs_df['job_type'].nunique() if 'job_type' in jobs_df.columns else 0
            st.metric("Job Types", unique_job_types)
        
        with col3:
            unique_locations = jobs_df['location'].nunique() if 'location' in jobs_df.columns else 0
            st.metric("Locations", unique_locations)
        
        with col4:
            jobs_with_salary = len(jobs_df[jobs_df.get('min_amount', 0) > 0]) if 'min_amount' in jobs_df.columns else 0
            st.metric("Jobs with Salary", jobs_with_salary)
    
    def _render_filter_controls(self, jobs_df: pd.DataFrame) -> Dict[str, Any]:
        """Render basic filter control widgets and return filter values."""
        st.markdown("### 🎯 Basic Filters")
        
        filters = {}
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Company filter
            if 'company' in jobs_df.columns:
                companies = ['All'] + sorted(jobs_df['company'].dropna().unique().tolist())
                filters['company'] = st.selectbox(
                    "🏢 Filter by Company", 
                    companies,
                    key=f"{self.session_key_prefix}company"
                )
        
        with col2:
            # Job type filter
            if 'job_type' in jobs_df.columns:
                job_types = ['All'] + sorted(jobs_df['job_type'].dropna().unique().tolist())
                filters['job_type'] = st.selectbox(
                    "💼 Filter by Job Type", 
                    job_types,
                    key=f"{self.session_key_prefix}job_type"
                )
        
        with col3:
            # Remote work filter
            if 'is_remote' in jobs_df.columns:
                remote_options = {'All': None, 'Remote Only': True, 'On-site Only': False}
                filters['remote'] = st.selectbox(
                    "🏠 Remote Work", 
                    list(remote_options.keys()),
                    key=f"{self.session_key_prefix}remote"
                )
                filters['remote_value'] = remote_options[filters['remote']]
        
        # Salary filters
        if 'min_amount' in jobs_df.columns and not jobs_df['min_amount'].isna().all():
            self._render_salary_filters(jobs_df, filters)
        
        return filters
    
    def _render_salary_filters(self, jobs_df: pd.DataFrame, filters: Dict[str, Any]) -> None:
        """Render salary range filters."""
        salary_df = jobs_df[jobs_df['min_amount'] > 0]
        if len(salary_df) > 0:
            st.markdown("**💰 Salary Range**")
            col1, col2 = st.columns(2)
            
            min_salary = int(salary_df['min_amount'].min())
            max_salary = int(salary_df['min_amount'].max())
            
            with col1:
                filters['min_salary'] = st.number_input(
                    "Minimum Salary ($)",
                    min_value=min_salary,
                    max_value=max_salary,
                    value=min_salary,
                    step=5000,
                    key=f"{self.session_key_prefix}min_salary"
                )
            
            with col2:
                filters['max_salary'] = st.number_input(
                    "Maximum Salary ($)",
                    min_value=min_salary,
                    max_value=max_salary,
                    value=max_salary,
                    step=5000,
                    key=f"{self.session_key_prefix}max_salary"
                )
            
            # Salary range slider for better UX
            salary_range = st.slider(
                "Salary Range ($)",
                min_value=min_salary,
                max_value=max_salary,
                value=(filters['min_salary'], filters['max_salary']),
                step=5000,
                key=f"{self.session_key_prefix}salary_slider"
            )
            filters['min_salary'], filters['max_salary'] = salary_range
    
    def _render_advanced_filters(self, jobs_df: pd.DataFrame) -> Dict[str, Any]:
        """Render advanced filter options."""
        advanced_filters = {}
        
        with st.expander("⚙️ Advanced Filters", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Location filter
                if 'location' in jobs_df.columns:
                    locations = ['All'] + sorted(jobs_df['location'].dropna().unique().tolist())
                    advanced_filters['location'] = st.selectbox(
                        "📍 Filter by Location",
                        locations,
                        key=f"{self.session_key_prefix}location"
                    )
                
                # Site filter
                if 'site' in jobs_df.columns:
                    sites = ['All'] + sorted(jobs_df['site'].dropna().unique().tolist())
                    advanced_filters['site'] = st.selectbox(
                        "🌐 Filter by Site",
                        sites,
                        key=f"{self.session_key_prefix}site"
                    )
                
                # Experience level filter
                if 'job_level' in jobs_df.columns:
                    job_levels = ['All'] + sorted(jobs_df['job_level'].dropna().unique().tolist())
                    advanced_filters['job_level'] = st.selectbox(
                        "📊 Filter by Experience Level",
                        job_levels,
                        key=f"{self.session_key_prefix}job_level"
                    )
            
            with col2:
                # Text search in job titles
                advanced_filters['title_search'] = st.text_input(
                    "🔍 Search in Job Titles",
                    placeholder="e.g., Python, Senior, Manager",
                    key=f"{self.session_key_prefix}title_search"
                )
                
                # Text search in descriptions
                advanced_filters['description_search'] = st.text_input(
                    "📝 Search in Descriptions",
                    placeholder="e.g., React, AWS, Machine Learning",
                    key=f"{self.session_key_prefix}description_search"
                )
                
                # Hiring manager filter
                if 'hiring_managers_count' in jobs_df.columns:
                    advanced_filters['has_hiring_managers'] = st.selectbox(
                        "👥 Hiring Manager Info",
                        ['All', 'With Hiring Managers', 'Without Hiring Managers'],
                        key=f"{self.session_key_prefix}hiring_managers"
                    )
            
            # Date filters
            if 'date_posted' in jobs_df.columns:
                self._render_date_filters(jobs_df, advanced_filters)
            
            # Company rating filter
            if 'company_rating' in jobs_df.columns:
                rating_df = jobs_df[jobs_df['company_rating'].notna()]
                if len(rating_df) > 0:
                    min_rating = float(rating_df['company_rating'].min())
                    max_rating = float(rating_df['company_rating'].max())
                    
                    advanced_filters['min_rating'] = st.slider(
                        "⭐ Minimum Company Rating",
                        min_value=min_rating,
                        max_value=max_rating,
                        value=min_rating,
                        step=0.1,
                        key=f"{self.session_key_prefix}min_rating"
                    )
            
            # AI-based filters (if AI tags are available)
            self.ai_helper.render_ai_filters(jobs_df, advanced_filters)
        
        return advanced_filters
    
    def _render_date_filters(self, jobs_df: pd.DataFrame, advanced_filters: Dict[str, Any]) -> None:
        """Render date-based filters."""
        st.markdown("**📅 Date Filters**")
        
        try:
            jobs_df_temp = jobs_df.copy()
            jobs_df_temp['date_posted'] = pd.to_datetime(jobs_df_temp['date_posted'], errors='coerce')
            valid_dates = jobs_df_temp['date_posted'].dropna()
            
            if len(valid_dates) > 0:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Quick date options
                    date_option = st.selectbox(
                        "Quick Date Filter",
                        ['All Time', 'Last 24 Hours', 'Last 3 Days', 'Last Week', 'Last Month', 'Custom Range'],
                        key=f"{self.session_key_prefix}date_option"
                    )
                    
                    if date_option != 'All Time' and date_option != 'Custom Range':
                        today = datetime.now().date()
                        if date_option == 'Last 24 Hours':
                            advanced_filters['date_from'] = today - timedelta(days=1)
                        elif date_option == 'Last 3 Days':
                            advanced_filters['date_from'] = today - timedelta(days=3)
                        elif date_option == 'Last Week':
                            advanced_filters['date_from'] = today - timedelta(weeks=1)
                        elif date_option == 'Last Month':
                            advanced_filters['date_from'] = today - timedelta(days=30)
                        
                        advanced_filters['date_to'] = today
                
                with col2:
                    if date_option == 'Custom Range':
                        date_range = st.date_input(
                            "Select Custom Date Range",
                            value=(min_date, max_date),
                            min_value=min_date,
                            max_value=max_date,
                            key=f"{self.session_key_prefix}custom_date_range"
                        )
                        
                        if isinstance(date_range, tuple) and len(date_range) == 2:
                            advanced_filters['date_from'], advanced_filters['date_to'] = date_range
                        elif len(date_range) == 1:
                            advanced_filters['date_from'] = date_range[0]
                            advanced_filters['date_to'] = date_range[0]
        
        except Exception:
            st.info("Date filtering not available - invalid date format")
    
    def _apply_filters(self, jobs_df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply all filters to the jobs dataframe."""
        filtered_df = jobs_df.copy()
        
        # Basic filters
        if filters.get('company') and filters['company'] != 'All':
            filtered_df = filtered_df[filtered_df['company'] == filters['company']]
        
        if filters.get('job_type') and filters['job_type'] != 'All':
            filtered_df = filtered_df[filtered_df['job_type'] == filters['job_type']]
        
        if filters.get('remote_value') is not None:
            filtered_df = filtered_df[filtered_df['is_remote'] == filters['remote_value']]
        
        # Salary filters
        if 'min_salary' in filters and 'max_salary' in filters:
            salary_mask = (
                (filtered_df['min_amount'] >= filters['min_salary']) & 
                (filtered_df['min_amount'] <= filters['max_salary'])
            )
            filtered_df = filtered_df[salary_mask]
        
        # Advanced filters
        if filters.get('location') and filters['location'] != 'All':
            filtered_df = filtered_df[filtered_df['location'] == filters['location']]
        
        if filters.get('site') and filters['site'] != 'All':
            filtered_df = filtered_df[filtered_df['site'] == filters['site']]
        
        if filters.get('job_level') and filters['job_level'] != 'All':
            filtered_df = filtered_df[filtered_df['job_level'] == filters['job_level']]
        
        # Text search filters
        if filters.get('title_search'):
            title_mask = filtered_df['title'].str.contains(
                filters['title_search'], case=False, na=False
            )
            filtered_df = filtered_df[title_mask]
        
        if filters.get('description_search') and 'description' in filtered_df.columns:
            desc_mask = filtered_df['description'].str.contains(
                filters['description_search'], case=False, na=False
            )
            filtered_df = filtered_df[desc_mask]
        
        # Hiring manager filter
        if filters.get('has_hiring_managers'):
            if filters['has_hiring_managers'] == 'With Hiring Managers':
                filtered_df = filtered_df[filtered_df.get('hiring_managers_count', 0) > 0]
            elif filters['has_hiring_managers'] == 'Without Hiring Managers':
                filtered_df = filtered_df[filtered_df.get('hiring_managers_count', 0) == 0]
        
        # Date filters
        if 'date_from' in filters and 'date_to' in filters:
            try:
                filtered_df_temp = filtered_df.copy()
                filtered_df_temp['date_posted'] = pd.to_datetime(filtered_df_temp['date_posted'], errors='coerce')
                
                date_mask = (
                    (filtered_df_temp['date_posted'].dt.date >= filters['date_from']) &
                    (filtered_df_temp['date_posted'].dt.date <= filters['date_to'])
                )
                filtered_df = filtered_df[date_mask]
            except Exception:
                pass
        
        # Rating filter
        if 'min_rating' in filters and 'company_rating' in filtered_df.columns:
            rating_mask = filtered_df['company_rating'] >= filters['min_rating']
            filtered_df = filtered_df[rating_mask]
        
        # AI-based filters
        filtered_df = self.ai_helper.apply_ai_filters(filtered_df, filters)
        
        return filtered_df
    
    def _render_filter_results(self, filtered_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        """Render filtered job results with multiple display options."""
        st.markdown("### 📊 Filter Results")
        
        # Results summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filtered Jobs", len(filtered_df))
        with col2:
            percentage = (len(filtered_df) / len(original_df) * 100) if len(original_df) > 0 else 0
            st.metric("Percentage of Total", f"{percentage:.1f}%")
        with col3:
            if len(filtered_df) > 0:
                avg_salary = filtered_df[filtered_df.get('min_amount', 0) > 0]['min_amount'].mean()
                if not pd.isna(avg_salary):
                    st.metric("Avg Salary (Filtered)", f"${avg_salary:,.0f}")
        
        if len(filtered_df) == 0:
            st.warning("No jobs match the selected filters. Try adjusting your criteria.")
            return
        
        # Display options
        display_option = st.radio(
            "Choose display format:",
            ['Table View', 'Card View', 'Compact List'],
            horizontal=True,
            key=f"{self.session_key_prefix}display_option"
        )
        
        # Pagination
        items_per_page = st.selectbox(
            "Items per page:",
            [10, 20, 50, 100],
            index=1,
            key=f"{self.session_key_prefix}items_per_page"
        )
        
        total_pages = (len(filtered_df) - 1) // items_per_page + 1
        if total_pages > 1:
            page = st.selectbox(
                f"Page (1-{total_pages}):",
                range(1, total_pages + 1),
                key=f"{self.session_key_prefix}page"
            )
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            display_df = filtered_df.iloc[start_idx:end_idx]
        else:
            display_df = filtered_df
        
        # Render based on selected display option
        if display_option == 'Table View':
            self._render_table_view(display_df)
        elif display_option == 'Card View':
            self._render_card_view(display_df)
        else:  # Compact List
            self._render_compact_list(display_df)
    
    def _render_table_view(self, display_df: pd.DataFrame) -> None:
        """Render results in table format."""
        # Column selection for table
        available_columns = display_df.columns.tolist()
        default_columns = ['title', 'company', 'location', 'site', 'job_type', 'is_remote']
        default_columns = [col for col in default_columns if col in available_columns]
        
        selected_columns = st.multiselect(
            "Select columns to display:",
            available_columns,
            default=default_columns,
            key=f"{self.session_key_prefix}table_columns"
        )
        
        if selected_columns:
            st.dataframe(
                display_df[selected_columns],
                use_container_width=True,
                hide_index=True
            )
    
    def _render_card_view(self, display_df: pd.DataFrame) -> None:
        """Render results in card format with company logos."""
        for idx, job in display_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 4, 1])
                
                with col1:
                    # Company logo
                    if pd.notna(job.get('company_logo')) and job.get('company_logo'):
                        try:
                            st.image(job['company_logo'], width=60)
                        except Exception:
                            st.write("🏢")
                    else:
                        st.write("🏢")
                
                with col2:
                    # Job details
                    st.markdown(f"**{job.get('title', 'No Title')}**")
                    st.write(f"🏢 {job.get('company', 'Unknown')}")
                    st.write(f"📍 {job.get('location', 'Unknown')}")
                    
                    # Additional info in columns
                    info_col1, info_col2 = st.columns(2)
                    with info_col1:
                        if pd.notna(job.get('job_type')):
                            st.write(f"💼 {job.get('job_type')}")
                        if pd.notna(job.get('is_remote')):
                            remote_text = "🏠 Remote" if job.get('is_remote') else "🏢 On-site"
                            st.write(remote_text)
                    
                    with info_col2:
                        if pd.notna(job.get('min_amount')) and job.get('min_amount') > 0:
                            salary = f"💰 ${job.get('min_amount'):,.0f}"
                            if pd.notna(job.get('max_amount')) and job.get('max_amount') > 0:
                                salary += f" - ${job.get('max_amount'):,.0f}"
                            st.write(salary)
                        
                        # Hiring manager info
                        if job.get('hiring_managers_count', 0) > 0:
                            st.write(f"👥 {int(job.get('hiring_managers_count', 0))} hiring manager(s)")
                
                with col3:
                    # Action buttons
                    if pd.notna(job.get('job_url')):
                        st.link_button("View Job", job['job_url'], use_container_width=True)
                    
                    if pd.notna(job.get('job_url_direct')):
                        st.link_button("Direct Link", job['job_url_direct'], use_container_width=True)
                
                st.divider()
    
    def _render_compact_list(self, display_df: pd.DataFrame) -> None:
        """Render results in compact list format."""
        for idx, job in display_df.iterrows():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Single line with key info
                title = job.get('title', 'No Title')
                company = job.get('company', 'Unknown')
                location = job.get('location', 'Unknown')
                
                info_parts = [f"**{title}**", f"at {company}", f"in {location}"]
                
                if pd.notna(job.get('is_remote')) and job.get('is_remote'):
                    info_parts.append("(Remote)")
                
                if pd.notna(job.get('min_amount')) and job.get('min_amount') > 0:
                    info_parts.append(f"- ${job.get('min_amount'):,.0f}")
                
                st.markdown(" ".join(info_parts))
            
            with col2:
                if pd.notna(job.get('job_url')):
                    st.link_button("View", job['job_url'], use_container_width=True)
    
    def _save_filter_to_history(self, filters: Dict[str, Any], result_count: int) -> None:
        """Save current filter combination to history."""
        # Only save non-default filters
        active_filters = {k: v for k, v in filters.items() 
                         if v and v != 'All' and v != '' and k != 'remote_value'}
        
        if active_filters:
            filter_entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'filters': active_filters,
                'result_count': result_count
            }
            
            # Add to history (keep last 10)
            history = st.session_state[f"{self.session_key_prefix}filter_history"]
            history.insert(0, filter_entry)
            st.session_state[f"{self.session_key_prefix}filter_history"] = history[:10]
    
    def _render_filter_management(self, current_filters: Dict[str, Any]) -> None:
        """Render filter management options (save, load, history)."""
        with st.expander("💾 Filter Management", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Save Current Filter**")
                filter_name = st.text_input(
                    "Filter Name:",
                    placeholder="e.g., Senior Python Remote",
                    key=f"{self.session_key_prefix}save_name"
                )
                
                if st.button("Save Filter", key=f"{self.session_key_prefix}save_button"):
                    if filter_name:
                        saved_filters = st.session_state[f"{self.session_key_prefix}saved_filters"]
                        saved_filters[filter_name] = current_filters
                        st.session_state[f"{self.session_key_prefix}saved_filters"] = saved_filters
                        st.success(f"Filter '{filter_name}' saved!")
                    else:
                        st.error("Please enter a filter name")
            
            with col2:
                st.markdown("**Load Saved Filter**")
                saved_filters = st.session_state[f"{self.session_key_prefix}saved_filters"]
                
                if saved_filters:
                    selected_filter = st.selectbox(
                        "Select saved filter:",
                        [''] + list(saved_filters.keys()),
                        key=f"{self.session_key_prefix}load_filter"
                    )
                    
                    if st.button("Load Filter", key=f"{self.session_key_prefix}load_button"):
                        if selected_filter and selected_filter in saved_filters:
                            # This would require rerunning the app to apply filters
                            st.info("Filter loaded! Please refresh the page to apply.")
                        else:
                            st.error("Please select a filter to load")
                else:
                    st.info("No saved filters available")
            
            # Filter history
            st.markdown("**Recent Filter History**")
            history = st.session_state[f"{self.session_key_prefix}filter_history"]
            
            if history:
                for i, entry in enumerate(history[:5]):  # Show last 5
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            filter_summary = ", ".join([f"{k}: {v}" for k, v in entry['filters'].items()])
                            st.caption(f"{entry['timestamp']}: {filter_summary[:100]}...")
                        
                        with col2:
                            st.caption(f"{entry['result_count']} results")
                        
                        with col3:
                            if st.button("Apply", key=f"{self.session_key_prefix}history_{i}"):
                                st.info("Filter selected! Please refresh to apply.")
            else:
                st.info("No filter history available")