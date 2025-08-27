import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional


class DeveloperToolsTabUI:
    """
    Developer Tools Tab UI component for debugging and development utilities.
    
    This class provides functionality to:
    - Display debug information
    - Show performance metrics
    - Provide development utilities
    """
    
    def __init__(self):
        """Initialize the Developer Tools Tab UI component."""
        pass
    
    def render(self):
        """Render developer tools and debugging utilities."""
        st.subheader("🛠️ Developer Tools")
        
        if st.session_state.get('show_debug', False):
            st.write("**Debug Information**")
            
            with st.expander("Session State Contents", expanded=False):
                st.json(dict(st.session_state))
            
            with st.expander("Current Data Sample", expanded=False):
                if st.session_state.get('jobs_data') is not None:
                    st.dataframe(st.session_state.jobs_data.head())
                else:
                    st.info("No data loaded")
        
        st.write("**Performance Metrics**")
        if st.button("📊 Show Performance Stats", type="secondary"):
            if st.session_state.get('jobs_data') is not None:
                df = st.session_state.jobs_data
                stats = {
                    'Memory usage (MB)': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}",
                    'Total rows': len(df),
                    'Total columns': len(df.columns),
                    'Null values': df.isnull().sum().sum(),
                    'Data types': df.dtypes.value_counts().to_dict()
                }
                st.json(stats)
            else:
                st.info("No data loaded to analyze")
