import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from typing import Dict, Any, List, Optional
from services.cover_letter_service import CoverLetterGenerator


class AICoverLetterTabUI:
    """
    AI Cover Letter Tab UI component for generating personalized cover letters.
    
    This class provides functionality to:
    - Take job description as input
    - Generate AI-powered cover letters
    - Preview and download generated cover letters
    - Provide tips and guidance for better results
    """
    
    def __init__(self):
        """Initialize the AI Cover Letter Tab UI component."""
        self.cover_letter_generator = CoverLetterGenerator()
    
    def render(self):
        """Render AI-powered cover letter generation tool."""
        st.subheader("🤖 AI Cover Letter Generator")
        
        st.markdown("""
        Generate a personalized cover letter using AI based on job description. 
        The AI will analyze the job requirements and create a tailored cover letter for you.
        """)
        
        # Job description input
        st.write("**Job Description**")
        job_description = st.text_area(
            "Paste the job description here:",
            height=200,
            placeholder="Paste the full job description including company name, role, requirements, and any other relevant details..."
        )
        
        # Advanced options in expander
        with st.expander("⚙️ Advanced Options", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                tone = st.selectbox(
                    "Cover letter tone:",
                    ["Professional", "Enthusiastic", "Confident", "Friendly"],
                    index=0
                )
                
                length = st.selectbox(
                    "Cover letter length:",
                    ["Concise", "Standard", "Detailed"],
                    index=1
                )
            
            with col2:
                focus_areas = st.multiselect(
                    "Focus areas to highlight:",
                    ["Technical Skills", "Leadership", "Problem Solving", "Team Collaboration", "Innovation", "Communication"],
                    default=["Technical Skills", "Problem Solving"]
                )
                
                custom_note = st.text_input(
                    "Additional note to include:",
                    placeholder="Any specific point you want to mention..."
                )
        
        # Generation section
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            generate_button = st.button(
                "🚀 Generate Cover Letter", 
                type="primary",
                use_container_width=True,
                disabled=not job_description.strip()
            )
        
        if not job_description.strip():
            st.info("📝 Please enter a job description to generate a cover letter.")
        
        # Generation process
        if generate_button and job_description.strip():
            try:
                with st.spinner("🤖 AI is analyzing the job description and generating your cover letter..."):
                    # Generate cover letter using the existing service
                    html_file_path, cover_letter_data = self.cover_letter_generator.generate_cover_letter_from_job(
                        job_description=job_description
                    )
                    
                    # Read the generated HTML content
                    with open(html_file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    st.success("✅ Cover letter generated successfully!")
                    
                    # Display preview and download options
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("📄 Cover Letter Preview")
                        
                        # Create a preview of the cover letter content
                        preview_data = {
                            "Company": cover_letter_data.get('company_name', 'N/A'),
                            "Position": cover_letter_data.get('position', 'N/A'),
                            "Date": cover_letter_data.get('date', 'N/A'),
                            "Applicant": cover_letter_data.get('applicant_name', 'N/A')
                        }
                        
                        for key, value in preview_data.items():
                            st.write(f"**{key}:** {value}")
                        
                        # Show a portion of the cover letter content
                        if 'cover_letter_body' in cover_letter_data:
                            st.write("**Content Preview:**")
                            # Show first 300 characters
                            preview_text = cover_letter_data['cover_letter_body'][:300] + "..."
                            st.write(preview_text)
                    
                    with col2:
                        st.subheader("💾 Download Options")
                        
                        # Generate filename
                        company_name = cover_letter_data.get('company_name', 'Company').replace(' ', '_')
                        position = cover_letter_data.get('position', 'Position').replace(' ', '_')
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"cover_letter_{company_name}_{position}_{timestamp}.html"
                        
                        # Download button for HTML
                        st.download_button(
                            label="📥 Download HTML",
                            data=html_content,
                            file_name=filename,
                            mime="text/html",
                            use_container_width=True
                        )
                        
                        # Optional: Download as JSON data
                        json_filename = filename.replace('.html', '_data.json')
                        st.download_button(
                            label="📊 Download Data (JSON)",
                            data=json.dumps(cover_letter_data, indent=2),
                            file_name=json_filename,
                            mime="application/json",
                            use_container_width=True
                        )
                        
                        # Display HTML preview button
                        if st.button("👁️ View Full HTML", use_container_width=True):
                            st.session_state.show_html_preview = True
                    
                    # Full HTML preview in expander
                    if st.session_state.get('show_html_preview', False):
                        with st.expander("🌐 Full HTML Preview", expanded=True):
                            st.components.v1.html(html_content, height=600, scrolling=True)
                            
                            if st.button("❌ Close Preview"):
                                st.session_state.show_html_preview = False
                                st.rerun()
                    
                    # Cleanup temporary file
                    try:
                        os.unlink(html_file_path)
                    except:
                        pass  # Ignore cleanup errors
                        
            except Exception as e:
                st.error(f"❌ Error generating cover letter: {str(e)}")
                
                # Provide helpful error information
                if "AI service is not available" in str(e):
                    st.warning("🔧 **AI Service Setup Required**")
                    st.info("""
                    To use the AI cover letter generator, you need to:
                    1. Configure your AI service API keys
                    2. Ensure the AI service is properly initialized
                    3. Check your internet connection
                    
                    Please check the AI configuration in the main dashboard settings.
                    """)
                elif "API" in str(e):
                    st.warning("🔑 **API Configuration Issue**")
                    st.info("Please check your AI service API keys and configuration.")
                else:
                    st.warning("🛠️ **Technical Issue**")
                    st.info("Please try again. If the problem persists, check the application logs.")
        
        # Tips and information
        with st.expander("💡 Tips for Better Cover Letters", expanded=False):
            st.markdown("""
            **For best results:**
            
            1. **Complete Job Description**: Include the full job posting with:
               - Company name and background
               - Detailed role requirements
               - Required skills and qualifications
               - Company culture information
            
            2. **Clear Formatting**: Ensure the job description is well-formatted and readable
            
            3. **Specific Details**: The more specific the job description, the better the AI can tailor your cover letter
            
            4. **Review and Edit**: Always review the generated cover letter and make personal adjustments
            
            5. **Personalization**: Add your own personal touch and specific examples
            """)
        
        # Usage statistics (if available)
        if hasattr(st.session_state, 'cover_letter_generated_count'):
            st.session_state.cover_letter_generated_count += 1
        else:
            st.session_state.cover_letter_generated_count = 0
        
        if st.session_state.cover_letter_generated_count > 0:
            st.info(f"📊 Cover letters generated this session: {st.session_state.cover_letter_generated_count}")
