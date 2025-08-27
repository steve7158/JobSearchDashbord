import streamlit as st
from typing import Dict, Any, List, Optional, Tuple
from UI.ui_ai_coverletter_tab import AICoverLetterTabUI
from UI.ui_data_management_tab import DataManagementTabUI
from UI.ui_system_info_tab import SystemInfoTabUI
from UI.ui_configuration_tools_tab import ConfigurationToolsTabUI
from UI.ui_backup_restore_tab import BackupRestoreTabUI
from UI.ui_developer_tools_tab import DeveloperToolsTabUI
from UI.ui_applied_jobs_tab import AppliedJobsTabUI


class UtilitiesUI:
    """
    Utilities UI component for various dashboard utilities and tools.
    
    This class provides utility functions like:
    - Data cleanup and management
    - Configuration management
    - System diagnostics
    - Backup and restore functionality
    
    The component uses a configuration-driven approach for easy maintenance
    and extension of utility tabs.
    """
    
    def __init__(self):
        """Initialize the Utilities UI component."""
        self.tabs_config = self._get_tabs_configuration()
    
    def _get_tabs_configuration(self) -> List[Dict[str, Any]]:
        """
        Define tab configuration with icons, names, and components.
        
        Returns:
            List of dictionaries containing tab configuration
        """
        return [
            {
                "icon": "🗄️",
                "name": "Data Management",
                "component": DataManagementTabUI(),
                "description": "Manage session data and cache"
            },
            {
                "icon": "🔧",
                "name": "System Info",
                "component": SystemInfoTabUI(),
                "description": "View system and environment information"
            },
            {
                "icon": "⚙️",
                "name": "Configuration",
                "component": ConfigurationToolsTabUI(),
                "description": "Configure dashboard settings and preferences"
            },
            {
                "icon": "💾",
                "name": "Backup & Restore",
                "component": BackupRestoreTabUI(),
                "description": "Create backups and restore data"
            },
            {
                "icon": "🤖",
                "name": "AI Cover Letter",
                "component": AICoverLetterTabUI(),
                "description": "Generate AI-powered cover letters"
            },
            {
                "icon": "🛠️",
                "name": "Developer Tools",
                "component": DeveloperToolsTabUI(),
                "description": "Debug tools and performance metrics"
            },
            {
                "icon": "💼",
                "name": "Applied Jobs",
                "component": AppliedJobsTabUI(),
                "description": "Manage and track your job applications"
            }        ]
    
    def _render_header(self) -> None:
        """Render the utilities header section."""
        st.markdown('<h1 class="main-header">🔧 Utilities</h1>', unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("""
        Welcome to the Utilities section! Here you can manage your dashboard data, 
        configure settings, create backups, and access developer tools.
        """)
    
    def _render_footer(self) -> None:
        """Render the utilities footer section."""
        st.markdown("---")
        
        # Show available utilities count
        total_utilities = len(self.tabs_config)
        st.info(f"💡 **Tip:** {total_utilities} utility tools available to help you manage your dashboard effectively.")
        
        # Optional: Show utility descriptions
        with st.expander("📋 Utility Overview", expanded=False):
            for config in self.tabs_config:
                st.write(f"**{config['icon']} {config['name']}**: {config['description']}")
    
    def add_custom_tab(self, icon: str, name: str, component: Any, description: str = "") -> None:
        """
        Add a custom utility tab dynamically.
        
        Args:
            icon: Icon for the tab
            name: Name of the tab
            component: Component instance with render() method
            description: Optional description of the utility
        """
        self.tabs_config.append({
            "icon": icon,
            "name": name,
            "component": component,
            "description": description
        })
    
    def render(self) -> None:
        """Main render method for the Utilities component."""
        self._render_header()
        
        # Create tab labels dynamically
        tab_labels = [f"{config['icon']} {config['name']}" for config in self.tabs_config]
        tabs = st.tabs(tab_labels)
        
        # Render each tab component
        for tab, config in zip(tabs, self.tabs_config):
            with tab:
                try:
                    config['component'].render()
                except Exception as e:
                    st.error(f"❌ Error rendering {config['name']}: {str(e)}")
                    st.info("Please check the console for detailed error information.")
        
        self._render_footer()
