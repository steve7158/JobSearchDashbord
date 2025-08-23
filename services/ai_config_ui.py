"""
AI Service Configuration UI Component

This component provides a user interface for:
- Viewing available AI providers
- Switching between providers and models
- Monitoring AI service status
- Configuring AI settings
"""

import streamlit as st
from typing import Dict, Any, Optional
from services.ai_service import ai_service


class AIServiceConfigUI:
    """
    UI component for AI service configuration and monitoring.
    """
    
    def __init__(self):
        """Initialize the AI service config UI."""
        self.session_key_prefix = "ai_config_"
    
    def render_ai_status_sidebar(self) -> None:
        """Render AI service status in sidebar."""
        with st.sidebar:
            st.markdown("### 🤖 AI Service Status")
            
            if ai_service.is_available():
                provider_info = ai_service.get_provider_info()
                
                st.success("✅ AI Service Active")
                st.info(f"**Provider:** {provider_info['current_provider'].title()}")
                st.info(f"**Model:** {provider_info['current_model']}")
                
                # Provider switching
                if len(provider_info['available_providers']) > 1:
                    with st.expander("🔄 Switch Provider"):
                        self.render_provider_selector()
            else:
                st.error("❌ No AI providers available")
                st.info("💡 Configure API keys in .env file")
    
    def render_provider_selector(self) -> None:
        """Render provider and model selection interface."""
        provider_info = ai_service.get_provider_info()
        
        # Provider selection
        selected_provider = st.selectbox(
            "Select AI Provider:",
            options=provider_info['available_providers'],
            index=provider_info['available_providers'].index(provider_info['current_provider']) 
            if provider_info['current_provider'] in provider_info['available_providers'] else 0,
            key=f"{self.session_key_prefix}provider"
        )
        
        # Model selection for selected provider
        available_models = ai_service.get_available_models(selected_provider)
        if available_models:
            selected_model = st.selectbox(
                "Select Model:",
                options=available_models,
                index=available_models.index(provider_info['current_model']) 
                if provider_info['current_model'] in available_models else 0,
                key=f"{self.session_key_prefix}model"
            )
        else:
            selected_model = None
        
        # Apply changes button
        if st.button("Apply Changes", key=f"{self.session_key_prefix}apply"):
            if ai_service.set_provider(selected_provider, selected_model):
                st.success(f"✅ Switched to {selected_provider.title()}")
                st.rerun()
            else:
                st.error("❌ Failed to switch provider")
    
    def render_ai_config_tab(self) -> None:
        """Render full AI configuration interface in a tab."""
        st.header("🤖 AI Service Configuration")
        
        # Service status overview
        col1, col2, col3 = st.columns(3)
        
        provider_info = ai_service.get_provider_info()
        
        with col1:
            st.metric(
                "Available Providers", 
                len(provider_info['available_providers'])
            )
        
        with col2:
            st.metric(
                "Current Provider", 
                provider_info['current_provider'].title() if provider_info['current_provider'] else "None"
            )
        
        with col3:
            status = "🟢 Active" if ai_service.is_available() else "🔴 Inactive"
            st.metric("Service Status", status)
        
        # Provider details
        st.markdown("### Provider Information")
        
        for provider_name in provider_info['available_providers']:
            with st.expander(f"{provider_name.title()} Provider"):
                models = ai_service.get_available_models(provider_name)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Available Models:** {len(models)}")
                    for model in models[:5]:  # Show first 5 models
                        st.text(f"• {model}")
                    if len(models) > 5:
                        st.text(f"... and {len(models) - 5} more")
                
                with col2:
                    is_current = provider_name == provider_info['current_provider']
                    st.markdown(f"**Status:** {'🟢 Active' if is_current else '⚪ Available'}")
                    
                    if not is_current and st.button(f"Switch to {provider_name.title()}", key=f"switch_{provider_name}"):
                        if ai_service.set_provider(provider_name):
                            st.success(f"✅ Switched to {provider_name.title()}")
                            st.rerun()
        
        # Configuration guide
        if not ai_service.is_available():
            st.markdown("### 🔧 Configuration Guide")
            st.warning("No AI providers are currently available. Follow the setup guide below:")
            
            st.markdown("""
            **Step 1: Edit your .env file**
            ```
            # Your .env file should contain:
            # (Create one if it doesn't exist)
            ```
            
            **Step 2: Add your API keys**
            ```
            OPENAI_API_KEY=your_openai_api_key_here
            GROQ_API_KEY=your_groq_api_key_here
            LLAMA_API_KEY=your_llama_api_key_here
            ```
            
            **Step 3: Install additional dependencies (optional)**
            ```
            pip install groq python-dotenv
            ```
            
            **Step 4: Restart the application**
            """)
        
        # Test AI functionality
        if ai_service.is_available():
            st.markdown("### 🧪 Test AI Functionality")
            
            test_prompt = st.text_input(
                "Enter a test prompt:",
                value="Explain what artificial intelligence is in one sentence.",
                key=f"{self.session_key_prefix}test_prompt"
            )
            
            if st.button("Test AI Response", key=f"{self.session_key_prefix}test"):
                with st.spinner("Testing AI service..."):
                    try:
                        response = ai_service.generate_completion(
                            messages=[{"role": "user", "content": test_prompt}],
                            max_tokens=100,
                            temperature=0.7
                        )
                        
                        if response:
                            st.success("✅ AI Test Successful!")
                            st.markdown(f"**Response:** {response}")
                        else:
                            st.error("❌ No response from AI service")
                    
                    except Exception as e:
                        st.error(f"❌ AI test failed: {str(e)}")
    
    def get_ai_status_info(self) -> Dict[str, Any]:
        """Get AI service status information for display."""
        if not ai_service.is_available():
            return {
                'status': 'inactive',
                'message': 'No AI providers available',
                'color': 'red'
            }
        
        provider_info = ai_service.get_provider_info()
        return {
            'status': 'active',
            'provider': provider_info['current_provider'],
            'model': provider_info['current_model'],
            'total_providers': len(provider_info['available_providers']),
            'message': f"Using {provider_info['current_provider'].title()}",
            'color': 'green'
        }


# Global instance for easy access
ai_config_ui = AIServiceConfigUI()
