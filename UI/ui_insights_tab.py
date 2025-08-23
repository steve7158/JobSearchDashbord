import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

class InsightTabUI:
    def __init__(self):
        pass
   
    def render_insights_tab(self, jobs_df: pd.DataFrame, job_service):
        """Render the insights tab."""
        st.subheader("📈 Job Market Insights")
        
        # Generate insights
        summary = job_service.get_job_summary(jobs_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Market Summary**")
            st.json(summary)
        
        with col2:
            st.write("**💡 Key Insights**")
            
            insights = self._generate_insights(summary)
            
            for insight in insights:
                st.write(insight)
    
    def _generate_insights(self, summary: Dict[str, Any]) -> list:
        """Generate key insights from job data summary."""
        insights = []
        
        if summary['total_jobs'] > 0:
            insights.append(f"• Found {summary['total_jobs']} job opportunities")
            insights.append(f"• {summary['unique_companies']} unique companies are hiring")
            
            if summary['remote_jobs'] > 0:
                remote_percentage = (summary['remote_jobs'] / summary['total_jobs']) * 100
                insights.append(f"• {remote_percentage:.1f}% of jobs offer remote work")
            
            if summary.get('avg_salary_min') and summary['avg_salary_min'] > 0:
                insights.append(f"• Average minimum salary: ${summary['avg_salary_min']:,.0f}")
            
            if summary.get('job_types'):
                most_common_type = max(summary['job_types'], key=summary['job_types'].get)
                insights.append(f"• Most common job type: {most_common_type}")
            
            if summary.get('sites_scraped'):
                sites_used = ', '.join(summary['sites_scraped'])
                insights.append(f"• Data collected from: {sites_used}")
        
        return insights
 