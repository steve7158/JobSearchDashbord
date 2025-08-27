import streamlit as st
import pandas as pd
from datetime import datetime
import json
from typing import Dict, Any, List, Optional


class DataManagementTabUI:
    """
    Data Management Tab UI component for managing dashboard data.
    
    This class provides functionality to:
    - Clear session data and cache
    - Download session information
    - Manage data state
    """
    
    def __init__(self):
        """Initialize the Data Management Tab UI component."""
        pass
    
    def render(self):
        """Render data management utilities."""
        st.subheader("🗄️ Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Clear Session Data**")
            if st.button("🗑️ Clear All Session Data", type="secondary"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("✅ Session data cleared!")
                st.rerun()
            
            st.write("**Clear Cache**")
            if st.button("🧹 Clear Cache", type="secondary"):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success("✅ Cache cleared!")
        
        with col2:
            st.write("**Download Session Data**")
            if st.session_state.get('jobs_data') is not None:
                session_data = {
                    'jobs_count': len(st.session_state.jobs_data),
                    'last_search_time': str(st.session_state.get('last_search_time', '')),
                    'data_columns': list(st.session_state.jobs_data.columns) if hasattr(st.session_state.jobs_data, 'columns') else []
                }
                
                st.download_button(
                    label="📥 Download Session Info",
                    data=json.dumps(session_data, indent=2),
                    file_name=f"session_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.info("No session data available to download")
