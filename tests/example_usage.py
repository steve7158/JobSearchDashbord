"""
Example usage of the JobSearchSidebar UI component class.

This file demonstrates how to use the JobSearchSidebar class in a Streamlit application.
"""

import streamlit as st
import sys
import os

# Add the parent directory to the Python path to import services
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.job_portal_service import JobPortalService
from UI.ui_sidebar import JobSearchSidebar


def get_job_service(linkedin_email=None, linkedin_password=None):
    """Factory function to create JobPortalService instance."""
    return JobPortalService(linkedin_email=linkedin_email, linkedin_password=linkedin_password)


def main():
    """Main application function demonstrating sidebar usage."""
    st.set_page_config(
        page_title="Job Search Dashboard",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("💼 Job Search Dashboard")
    st.markdown("This is an example of using the JobSearchSidebar UI component class.")
    
    # Initialize the sidebar component
    sidebar = JobSearchSidebar(get_job_service_func=get_job_service)
    
    # Render the sidebar and get configuration
    search_config, search_button_pressed, job_service = sidebar.render()
    
    # Main content area
    if search_button_pressed:
        st.header("🔍 Search Results")
        
        # Display the configuration that was collected
        st.subheader("Search Configuration")
        st.json(search_config)
        
        # Here you would typically use the job_service to perform the search
        if search_config['selected_sites']:
            with st.spinner("Searching for jobs..."):
                st.success(f"Would search for '{search_config['search_term']}' "
                          f"in {search_config['location']} "
                          f"on sites: {', '.join(search_config['selected_sites'])}")
                
                # Example of how you might use the configuration
                st.info(f"Fetching {search_config['results_wanted']} results "
                       f"from jobs posted within {search_config['hours_old']} hours")
                
                if search_config['linkedin_description']:
                    st.info("Including detailed LinkedIn descriptions")
        else:
            st.warning("Please select at least one job site to search.")
    
    else:
        st.info("👈 Configure your search parameters in the sidebar and click 'Search Jobs'")
        
        # Show some help text
        st.markdown("""
        ### How to use this dashboard:
        
        1. **Configure LinkedIn Authentication** (optional but recommended)
           - Add credentials to your `.env` file, or
           - Use the manual credential input (less secure)
        
        2. **Set Search Parameters**
           - Choose job sites to search
           - Enter search terms and location
           - Adjust number of results and job age
        
        3. **Advanced Settings** (optional)
           - Customize Google search terms
           - Select Indeed country
        
        4. **Click Search Jobs** to start the search
        """)


if __name__ == "__main__":
    main()
