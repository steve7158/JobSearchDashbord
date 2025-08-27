import streamlit as st
import pandas as pd
from datetime import datetime
import json
from typing import Dict, Any, List, Optional


class BackupRestoreTabUI:
    """
    Backup & Restore Tab UI component for data backup and restoration.
    
    This class provides functionality to:
    - Create data backups
    - Restore from backup files
    - Manage backup/restore operations
    """
    
    def __init__(self):
        """Initialize the Backup & Restore Tab UI component."""
        pass
    
    def render(self):
        """Render backup and restore functionality."""
        st.subheader("💾 Backup & Restore")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Create Backup**")
            if st.session_state.get('jobs_data') is not None:
                backup_name = st.text_input("Backup name", value=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                
                if st.button("📦 Create Backup", type="primary"):
                    try:
                        # Create backup of current jobs data
                        backup_data = {
                            'timestamp': datetime.now().isoformat(),
                            'jobs_data': st.session_state.jobs_data.to_dict('records'),
                            'metadata': {
                                'total_jobs': len(st.session_state.jobs_data),
                                'columns': list(st.session_state.jobs_data.columns)
                            }
                        }
                        
                        st.download_button(
                            label="💾 Download Backup",
                            data=json.dumps(backup_data, indent=2, default=str),
                            file_name=f"{backup_name}.json",
                            mime="application/json"
                        )
                        st.success("✅ Backup created successfully!")
                    except Exception as e:
                        st.error(f"❌ Error creating backup: {e}")
            else:
                st.info("No data available to backup")
        
        with col2:
            st.write("**Restore from Backup**")
            uploaded_file = st.file_uploader("Choose backup file", type=['json'])
            
            if uploaded_file is not None:
                if st.button("🔄 Restore from Backup", type="secondary"):
                    try:
                        backup_data = json.loads(uploaded_file.read())
                        
                        if 'jobs_data' in backup_data:
                            restored_df = pd.DataFrame(backup_data['jobs_data'])
                            st.session_state.jobs_data = restored_df
                            st.session_state.last_search_time = datetime.now()
                            
                            st.success(f"✅ Restored {len(restored_df)} jobs from backup!")
                            st.info("Data restored successfully. Switch back to main view to see the data.")
                        else:
                            st.error("❌ Invalid backup file format")
                    except Exception as e:
                        st.error(f"❌ Error restoring backup: {e}")
