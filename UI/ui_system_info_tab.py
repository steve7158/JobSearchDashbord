import streamlit as st
import os
from datetime import datetime
from typing import Dict, Any, List, Optional


class SystemInfoTabUI:
    """
    System Information Tab UI component for displaying system diagnostics.
    
    This class provides functionality to:
    - Display session state information
    - Show environment details
    - Provide system diagnostics
    """
    
    def __init__(self):
        """Initialize the System Info Tab UI component."""
        pass
    
    def render(self):
        """Render system information and diagnostics."""
        st.subheader("🔧 System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Session State Info**")
            state_info = {
                'Total session variables': len(st.session_state),
                'Jobs data loaded': 'Yes' if st.session_state.get('jobs_data') is not None else 'No',
                'Auth completed': st.session_state.get('auth_completed', False),
                'Last search time': str(st.session_state.get('last_search_time', 'Never'))
            }
            
            for key, value in state_info.items():
                st.write(f"• **{key}:** {value}")
        
        with col2:
            st.write("**Environment Info**")
            try:
                import streamlit as st_version
                import pandas as pd_version
                
                env_info = {
                    'Streamlit version': st.__version__,
                    'Pandas version': pd_version.__version__,
                    'Current time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Working directory': os.getcwd()
                }
                
                for key, value in env_info.items():
                    st.write(f"• **{key}:** {value}")
            except Exception as e:
                st.error(f"Error getting environment info: {e}")
