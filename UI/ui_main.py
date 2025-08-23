
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from UI.ui_analytics_tab import AnalyticsTabUI
from UI.ui_export_tab import ExportTabUI
from UI.ui_filter_tab import FilterTabUI
from UI.ui_insights_tab import InsightTabUI
from UI.ui_job_list_tab import JobListTabUI
from UI.ui_applied_jobs_tab import AppliedJobsTabUI

class MainUITabs:
    def __init__(self):
        self.insight_tab_ui = InsightTabUI()
        self.job_list_tab_ui = JobListTabUI()
        self.analytics_tab_ui = AnalyticsTabUI()
        self.filter_tab_ui = FilterTabUI()
        self.export_tab_ui = ExportTabUI()
        self.applied_jobs_tab_ui = AppliedJobsTabUI()
    def render_main_tabs(self, jobs_df: pd.DataFrame, job_service):
        """Render the main dashboard tabs."""
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Job List", "📊 Analytics", "🔍 Filter Jobs", "💾 Export", "📈 Insights", "💼 Applied Jobs"])
        
        with tab1:
            self.job_list_tab_ui.render(jobs_df)
        
        with tab2:
            self.analytics_tab_ui.render(jobs_df)
        
        with tab3:
            self.filter_tab_ui.render(jobs_df)
        
        with tab4:
            self.export_tab_ui.render(jobs_df, job_service)
        
        with tab5:
            self.insight_tab_ui.render_insights_tab(jobs_df, job_service)
        
        with tab6:
            self.applied_jobs_tab_ui.render()
