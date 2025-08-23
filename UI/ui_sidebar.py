import streamlit as st
import os
from typing import Dict, Any, Optional, Tuple
from services.ai_service import ai_service


class JobSearchSidebar:
    """UI component class for job search sidebar configuration."""
    
    def __init__(self, get_job_service_func):
        """
        Initialize the sidebar component.
        
        Args:
            get_job_service_func: Function to get job service instance
        """
        self.get_job_service = get_job_service_func
        self.linkedin_email_env = os.getenv('LINKEDIN_EMAIL', '')
        self.linkedin_password_env = os.getenv('LINKEDIN_PASSWORD', '')
        
        # Default values
        self.default_search_term = "Gen Ai"
        self.default_location = "India"
        self.default_results = 20
        self.default_hours_old = 72  # 3 days
        self.available_sites = ["linkedin", "glassdoor", "bayt", "naukri", "bdjobs"]
        self.indeed_countries = ["USA", "UK", "Canada", "Australia", "India"]
        
    def _render_linkedin_auth_section(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Render LinkedIn authentication section.
        
        Returns:
            Tuple of (linkedin_email, linkedin_password)
        """
        st.subheader("🔐 LinkedIn Authentication")
        st.markdown("*Optional: For enhanced hiring manager extraction*")
        
        # Check if credentials are in environment
        if (self.linkedin_email_env and self.linkedin_password_env and 
            not self.linkedin_email_env.endswith('example.com')):
            
            st.success("✅ LinkedIn credentials loaded from .env")
            use_linkedin_auth = st.checkbox(
                "Use LinkedIn Authentication", 
                value=True, 
                help="Use authenticated LinkedIn session for better hiring manager extraction"
            )
            
            if use_linkedin_auth:
                return self.linkedin_email_env, self.linkedin_password_env
            else:
                return None, None
        else:
            st.info("💡 Add LINKEDIN_EMAIL and LINKEDIN_PASSWORD to .env for authenticated scraping")
            
            with st.expander("Manual LinkedIn Credentials", expanded=False):
                st.warning("⚠️ Not recommended: Entering credentials here is less secure")
                linkedin_email = st.text_input(
                    "LinkedIn Email", 
                    value="", 
                    help="Your LinkedIn login email"
                )
                linkedin_password = st.text_input(
                    "LinkedIn Password", 
                    value="", 
                    type="password",
                    help="Your LinkedIn password"
                )
                
                if linkedin_email and linkedin_password:
                    st.success("✅ LinkedIn credentials entered")
                    return linkedin_email, linkedin_password
                else:
                    return None, None
    
    def _render_ai_configuration_section(self) -> Dict[str, Any]:
        """
        Render AI provider and model configuration section.
        
        Returns:
            Dictionary containing AI configuration
        """
        st.subheader("🤖 AI Configuration")
        
        # Get current AI service info
        provider_info = ai_service.get_provider_info()
        available_providers = provider_info.get('available_providers', [])
        current_provider = provider_info.get('current_provider', 'none')
        current_model = provider_info.get('current_model', 'none')
        
        # Provider selection
        if available_providers:
            provider_options = available_providers
            try:
                current_index = provider_options.index(current_provider)
            except ValueError:
                current_index = 0
                
            selected_provider = st.selectbox(
                "AI Provider",
                provider_options,
                index=current_index,
                help="Choose your AI provider for job analysis and filtering"
            )
            
            # Model selection for the chosen provider
            available_models = ai_service.get_available_models(selected_provider)
            if available_models:
                try:
                    model_index = available_models.index(current_model) if selected_provider == current_provider else 0
                except ValueError:
                    model_index = 0
                    
                selected_model = st.selectbox(
                    "AI Model",
                    available_models,
                    index=model_index,
                    help=f"Choose the {selected_provider} model to use"
                )
            else:
                selected_model = None
                st.warning(f"No models available for {selected_provider}")
            
            # Apply configuration if changed
            if (selected_provider != current_provider or 
                (selected_model and selected_model != current_model)):
                
                if st.button("🔄 Apply AI Settings", key="apply_ai_settings"):
                    success = ai_service.set_provider(selected_provider, selected_model)
                    if success:
                        st.success(f"✅ Switched to {selected_provider} - {selected_model}")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to switch to {selected_provider}")
            
            # Display current status
            ai_status = "🟢 Available" if ai_service.is_available() else "🔴 Unavailable"
            st.markdown(f"**Status:** {ai_status}")
            st.markdown(f"**Active:** {current_provider} - {current_model}")
            
            # Model recommendations
            with st.expander("💡 Model Recommendations", expanded=False):
                st.markdown("""
                **For Speed:**
                - Groq: `llama-3.1-8b-instant` (fastest)
                - OpenAI: `gpt-3.5-turbo` (fast, good quality)
                
                **For Quality:**
                - OpenAI: `gpt-4o` (best quality)
                - Groq: `llama-3.1-405b-reasoning` (high quality)
                
                **For Cost:**
                - Groq: Any model (free tier)
                - OpenAI: `gpt-3.5-turbo` (cheapest)
                """)
            
            return {
                'ai_provider': selected_provider,
                'ai_model': selected_model,
                'ai_available': ai_service.is_available()
            }
        else:
            st.warning("⚠️ No AI providers available")
            st.info("💡 Add API keys to .env file:\n- OPENAI_API_KEY\n- GROQ_API_KEY")
            return {
                'ai_provider': None,
                'ai_model': None,
                'ai_available': False
            }
    
    def _render_auth_status_indicator(self, linkedin_email: Optional[str], linkedin_password: Optional[str]):
        """
        Render authentication status indicator.
        
        Args:
            linkedin_email: LinkedIn email if provided
            linkedin_password: LinkedIn password if provided
        """
        if linkedin_email and linkedin_password:
            st.markdown("**Authentication Status:**")
            if st.session_state.get('auth_completed', False):
                st.success("🔐 LinkedIn Authenticated")
            elif st.session_state.get('auth_browser_opened', False):
                st.warning("⏳ Waiting for login completion")
            else:
                st.info("🔓 Ready for authentication")
    
    def _render_search_configuration(self) -> Dict[str, Any]:
        """
        Render job search configuration section.
        
        Returns:
            Dictionary containing search configuration parameters
        """
        st.subheader("Job Search Configuration")
        
        # Site selection
        selected_sites = st.multiselect(
            "Select Job Sites",
            self.available_sites,
            default=["linkedin"],
            help="Choose which job portals to search"
        )
        
        # Search parameters
        search_term = st.text_input(
            "Search Term",
            value=self.default_search_term,
            help="Enter job title or keywords"
        )
        
        location = st.text_input(
            "Location",
            value=self.default_location,
            help="Enter location for job search"
        )
        
        results_wanted = st.slider(
            "Number of Results",
            min_value=5,
            max_value=100,
            value=self.default_results,
            step=5,
            help="Number of job results to fetch"
        )
        
        hours_old_options = [24, 48, 72, 168, 720]  # 1 day, 2 days, 3 days, 1 week, 1 month
        hours_old = st.selectbox(
            "Maximum Job Age (hours)",
            hours_old_options,
            index=hours_old_options.index(self.default_hours_old),
            help="How old can the job postings be"
        )
        
        linkedin_description = st.checkbox(
            "Fetch LinkedIn Descriptions",
            value=True,
            help="Get detailed job descriptions (slower but more info)"
        )
        
        return {
            'selected_sites': selected_sites,
            'search_term': search_term,
            'location': location,
            'results_wanted': results_wanted,
            'hours_old': hours_old,
            'linkedin_description': linkedin_description
        }
    
    def _render_advanced_settings(self, search_term: str, location: str) -> Dict[str, Any]:
        """
        Render advanced settings section.
        
        Args:
            search_term: Current search term for Google search default
            location: Current location for Google search default
            
        Returns:
            Dictionary containing advanced settings
        """
        with st.expander("🔧 Advanced Settings"):
            google_search_term = st.text_input(
                "Google Search Term",
                value=f"{search_term} jobs near {location} since yesterday",
                help="Custom Google search query"
            )
            
            country_indeed = st.selectbox(
                "Indeed Country",
                self.indeed_countries,
                help="Country for Indeed job searches"
            )
            
            return {
                'google_search_term': google_search_term,
                'country_indeed': country_indeed
            }
    
    def render(self) -> Tuple[Dict[str, Any], bool, Any]:
        """
        Render the complete sidebar UI component.
        
        Returns:
            Tuple of (search_config, search_button_pressed, job_service)
        """
        st.sidebar.header("🔍 Search Parameters")
        
        with st.sidebar:
            # LinkedIn Authentication Section
            linkedin_email, linkedin_password = self._render_linkedin_auth_section()
            
            # Initialize job service with credentials
            job_service = self.get_job_service(linkedin_email, linkedin_password)
            
            # Authentication Status Indicator
            self._render_auth_status_indicator(linkedin_email, linkedin_password)
            
            st.markdown("---")
            
            # AI Configuration Section
            ai_config = self._render_ai_configuration_section()
            
            st.markdown("---")
            
            # Job Search Configuration
            search_config = self._render_search_configuration()
            
            # Advanced Settings
            advanced_settings = self._render_advanced_settings(
                search_config['search_term'], 
                search_config['location']
            )
            search_config.update(advanced_settings)
            
            # Add LinkedIn credentials and AI config to search config
            search_config.update({
                'linkedin_email': linkedin_email,
                'linkedin_password': linkedin_password
            })
            search_config.update(ai_config)
            
            # Search button
            search_button = st.button(
                "🚀 Search Jobs",
                type="primary",
                use_container_width=True
            )
            
            return search_config, search_button, job_service
