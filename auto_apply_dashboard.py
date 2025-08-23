import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the services directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from services.auto_apply_service import AutoApplyService, UserProfile
from services.job_portal_service import JobPortalService


def show_env_setup_instructions():
    """Display instructions for setting up the .env file."""
    st.subheader("🔧 Environment Setup")
    
    env_exists = os.path.exists('.env')
    
    if not env_exists:
        st.warning("⚠️ .env file not found")
        st.info("To automatically load API keys, follow these steps:")
        
        with st.expander("📋 Setup Instructions", expanded=True):
            st.markdown("""
            **Step 1:** Create your environment file
            ```bash
            # Copy from the main .env file or create a new one
            cp .env .env.backup  # backup existing if needed
            ```
            
            **Step 2:** Edit the .env file with your API keys
            ```bash
            # Open .env file and replace with your actual keys
            OPENAI_API_KEY=sk-your-actual-openai-key-here
            GROQ_API_KEY=gsk-your-actual-groq-key-here
            ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here
            DEFAULT_AI_PROVIDER=openai
            ```
            
            **Step 3:** Restart the dashboard
            ```bash
            streamlit run auto_apply_dashboard.py
            ```
            """)
    else:
        st.success("✅ .env file found")
        
        # Check if API keys are set
        openai_key = os.getenv('OPENAI_API_KEY', '')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        col1, col2 = st.columns(2)
        with col1:
            if openai_key and openai_key != "your_openai_api_key_here":
                st.success("✅ OpenAI API key configured")
            else:
                st.warning("⚠️ OpenAI API key not set")
        
        with col2:
            if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
                st.success("✅ Anthropic API key configured")
            else:
                st.warning("⚠️ Anthropic API key not set")


def create_user_profile_form():
    """Create a form for users to input their profile information."""
    st.subheader("👤 User Profile Setup")
    
    # Personal Information
    with st.expander("📝 Personal Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name*")
            email = st.text_input("Email*")
            address = st.text_input("Address")
            state = st.text_input("State")
            country = st.selectbox("Country", ["USA", "Canada", "UK", "India", "Australia", "Other"])
        
        with col2:
            last_name = st.text_input("Last Name*")
            phone = st.text_input("Phone*")
            city = st.text_input("City")
            zip_code = st.text_input("ZIP Code")
    
    # Professional Information
    with st.expander("💼 Professional Information"):
        col1, col2 = st.columns(2)
        with col1:
            current_title = st.text_input("Current Job Title")
            years_of_experience = st.selectbox("Years of Experience", 
                ["0-1", "1-2", "2-5", "5-10", "10-15", "15+"])
            linkedin_url = st.text_input("LinkedIn URL")
        
        with col2:
            salary_expectation = st.text_input("Salary Expectation")
            notice_period = st.selectbox("Notice Period", 
                ["Immediately", "2 weeks", "1 month", "2 months", "3 months"])
            portfolio_url = st.text_input("Portfolio URL")
        
        github_url = st.text_input("GitHub URL")
    
    # Education
    with st.expander("🎓 Education"):
        col1, col2 = st.columns(2)
        with col1:
            education_level = st.selectbox("Education Level", 
                ["High School", "Associate", "Bachelor's", "Master's", "PhD"])
            degree = st.text_input("Degree/Major")
        
        with col2:
            university = st.text_input("University/School")
            graduation_year = st.text_input("Graduation Year")
    
    # Skills and Experience
    with st.expander("🛠️ Skills & Experience"):
        skills_input = st.text_area("Skills (one per line or comma-separated)")
        resume_text = st.text_area("Resume Summary/Experience", height=150)
        cover_letter_template = st.text_area("Cover Letter Template", height=100)
    
    # Work Authorization
    with st.expander("📋 Work Authorization"):
        col1, col2 = st.columns(2)
        with col1:
            work_authorized = st.selectbox("Work Authorization Status", 
                ["Authorized to work", "Need sponsorship", "Student visa", "Other"])
            willing_to_relocate = st.checkbox("Willing to relocate")
        
        with col2:
            visa_status = st.text_input("Visa Status (if applicable)")
            security_clearance = st.text_input("Security Clearance (if applicable)")
    
    # Process skills input
    skills = []
    if skills_input:
        if ',' in skills_input:
            skills = [skill.strip() for skill in skills_input.split(',')]
        else:
            skills = [skill.strip() for skill in skills_input.split('\n') if skill.strip()]
    
    # Create UserProfile object
    profile = UserProfile(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        country=country,
        current_title=current_title,
        years_of_experience=years_of_experience,
        linkedin_url=linkedin_url,
        portfolio_url=portfolio_url,
        github_url=github_url,
        education_level=education_level,
        university=university,
        degree=degree,
        graduation_year=graduation_year,
        skills=skills,
        resume_text=resume_text,
        cover_letter_template=cover_letter_template,
        work_authorized=(work_authorized == "Authorized to work"),
        visa_status=visa_status,
        security_clearance=security_clearance,
        salary_expectation=salary_expectation,
        notice_period=notice_period,
        willing_to_relocate=willing_to_relocate
    )
    
    return profile


def main():
    st.set_page_config(
        page_title="Auto Apply Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Auto Apply Assistant")
    st.markdown("Automatically fill job applications using AI analysis")
    
    # Initialize session state
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'auto_apply_service' not in st.session_state:
        st.session_state.auto_apply_service = None
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Configuration
        st.subheader("🔑 API Settings")
        
        # Get default values from environment
        default_provider = os.getenv('DEFAULT_LLM_PROVIDER', 'openai')
        openai_key_env = os.getenv('OPENAI_API_KEY', '')
        anthropic_key_env = os.getenv('ANTHROPIC_API_KEY', '')
        
        llm_provider = st.selectbox("LLM Provider", ["openai", "anthropic"], 
                                   index=0 if default_provider == "openai" else 1)
        
        # Show API key input with environment variable as default
        if llm_provider == "openai":
            api_key_default = openai_key_env if openai_key_env and openai_key_env != "your_openai_api_key_here" else ""
            api_key_placeholder = "Enter OpenAI API key or set OPENAI_API_KEY in .env"
        else:
            api_key_default = anthropic_key_env if anthropic_key_env and anthropic_key_env != "your_anthropic_api_key_here" else ""
            api_key_placeholder = "Enter Anthropic API key or set ANTHROPIC_API_KEY in .env"
        
        api_key = st.text_input("API Key", 
                               value=api_key_default,
                               type="password", 
                               placeholder=api_key_placeholder,
                               help=f"Enter your {llm_provider.upper()} API key or set it in the .env file")
        
        # Show status of environment variables
        if api_key_default:
            st.success(f"✅ {llm_provider.upper()} API key loaded from environment")
        elif llm_provider == "openai" and openai_key_env:
            st.warning("⚠️ OpenAI API key found in .env but appears to be placeholder")
        elif llm_provider == "anthropic" and anthropic_key_env:
            st.warning("⚠️ Anthropic API key found in .env but appears to be placeholder")
        else:
            st.info("💡 Set API keys in .env file for automatic loading")
        
        # Environment file status
        env_file_exists = os.path.exists('.env')
        if env_file_exists:
            st.success("✅ .env file found")
        else:
            st.warning("⚠️ .env file not found. Create a .env file and add your API keys")
        
        # Service Availability Status
        st.subheader("🔧 Service Status")
        
        # Check Workday service availability
        try:
            from services.workday_apply_service import apply_to_workday_job
            workday_available = True
        except ImportError:
            workday_available = False
        
        col1, col2 = st.columns(2)
        with col1:
            if workday_available:
                st.success("✅ Workday AutoApply Service - Available")
                st.caption("Specialized Workday portal automation enabled")
            else:
                st.warning("⚠️ Workday AutoApply Service - Unavailable")
                st.caption("Install 'playwright' for Workday support")
        
        with col2:
            # Check if Playwright is installed
            try:
                import playwright
                playwright_available = True
            except ImportError:
                playwright_available = False
                
            if playwright_available:
                st.success("✅ Playwright Browser Automation - Available")
                st.caption("Enhanced browser control for complex sites")
            else:
                st.info("💡 Playwright - Optional")
                st.caption("Run: pip install playwright playwright install")
        
        if workday_available and playwright_available:
            st.info("🎯 **Enhanced Mode**: Both standard and Workday-specific automation available")
        elif not workday_available and not playwright_available:
            st.info("🔧 **Standard Mode**: Using Selenium for all job portals")
        else:
            st.info("🔧 **Mixed Mode**: Some enhanced features may be limited")
        
        # Profile Management
        st.subheader("👤 Profile Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Profile"):
                if st.session_state.user_profile:
                    filename = f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    try:
                        with open(filename, 'w') as f:
                            json.dump(st.session_state.user_profile.__dict__, f, indent=2)
                        st.success(f"Profile saved as {filename}")
                    except Exception as e:
                        st.error(f"Error saving profile: {str(e)}")
        
        with col2:
            uploaded_file = st.file_uploader("📂 Load Profile", type="json")
            if uploaded_file:
                try:
                    profile_data = json.load(uploaded_file)
                    st.session_state.user_profile = UserProfile(**profile_data)
                    st.success("Profile loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading profile: {str(e)}")
        
        # Resume Upload for Auto-Profile Creation
        st.subheader("📄 Resume Analysis")
        resume_file = st.file_uploader("Upload Resume for Auto-Profile", 
                                     type=["txt", "pdf"], 
                                     help="Upload resume to auto-generate profile")
        
        if resume_file and api_key:
            if st.button("🤖 Generate Profile from Resume"):
                try:
                    # Read resume content
                    if resume_file.type == "text/plain":
                        resume_text = str(resume_file.read(), "utf-8")
                    else:
                        st.warning("PDF parsing not implemented yet. Please use .txt files.")
                        resume_text = ""
                    
                    if resume_text:
                        # Create temporary service for profile generation
                        temp_profile = UserProfile()
                        temp_service = AutoApplyService(temp_profile, llm_provider, api_key)
                        
                        with st.spinner("Analyzing resume..."):
                            st.session_state.user_profile = temp_service.create_user_profile_from_resume(resume_text)
                        
                        st.success("Profile generated from resume!")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Error generating profile: {str(e)}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Profile Setup", "🎯 Auto Apply", "📊 Results", "🔍 Job Search", "⚙️ Setup"])
    
    with tab5:
        st.header("⚙️ Environment Setup")
        show_env_setup_instructions()
        
        # Additional configuration options
        st.subheader("🛠️ Configuration Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Environment Variables:**")
            env_vars = {
                "OPENAI_API_KEY": "✅ Set" if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != "your_openai_api_key_here" else "❌ Not set",
                "ANTHROPIC_API_KEY": "✅ Set" if os.getenv('ANTHROPIC_API_KEY') and os.getenv('ANTHROPIC_API_KEY') != "your_anthropic_api_key_here" else "❌ Not set",
                "DEFAULT_LLM_PROVIDER": os.getenv('DEFAULT_LLM_PROVIDER', 'Not set'),
                "HEADLESS_MODE": os.getenv('HEADLESS_MODE', 'Not set'),
                "BROWSER_WAIT_TIME": os.getenv('BROWSER_WAIT_TIME', 'Not set'),
            }
            
            for key, value in env_vars.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.markdown("**Recommended .env file content:**")
            st.code("""
OPENAI_API_KEY=sk-your-actual-openai-key
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key
DEFAULT_LLM_PROVIDER=openai
HEADLESS_MODE=false
BROWSER_WAIT_TIME=10
DEBUG_MODE=false
            """, language="bash")
        
        # Troubleshooting section
        st.subheader("🔧 Troubleshooting")
        
        with st.expander("Common Issues and Solutions"):
            st.markdown("""
            **Issue: API keys not loading**
            - Ensure .env file is in the same directory as the dashboard
            - Restart the Streamlit application after editing .env
            - Check that there are no extra spaces around the = sign
            
            **Issue: ChromeDriver not found**
            - Download ChromeDriver from https://chromedriver.chromium.org/
            - Add ChromeDriver to your system PATH
            - Or place chromedriver executable in the project directory
            
            **Issue: Browser won't open**
            - Try setting HEADLESS_MODE=false in .env
            - Increase BROWSER_WAIT_TIME if pages load slowly
            - Check Chrome browser is installed
            
            **Issue: Form fields not detected**
            - Try with headless mode disabled to see the browser
            - Some sites require JavaScript to load forms
            - Verify the URL points to an actual application form
            """)
    
    with tab1:
        st.header("User Profile Configuration")
        
        # Show existing profile or create new one
        if st.session_state.user_profile:
            st.success("✅ Profile loaded successfully!")
            
            # Display current profile
            with st.expander("Current Profile Summary", expanded=False):
                profile_dict = st.session_state.user_profile.__dict__
                st.json(profile_dict)
            
            # Option to edit profile
            if st.button("✏️ Edit Profile"):
                st.session_state.user_profile = None
                st.rerun()
        
        # Create/Edit profile form
        if not st.session_state.user_profile:
            profile = create_user_profile_form()
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("💾 Save Profile", type="primary", use_container_width=True):
                    # Validate required fields
                    required_fields = ['first_name', 'last_name', 'email', 'phone']
                    missing_fields = [field for field in required_fields 
                                    if not getattr(profile, field)]
                    
                    if missing_fields:
                        st.error(f"Please fill required fields: {', '.join(missing_fields)}")
                    else:
                        st.session_state.user_profile = profile
                        st.success("Profile saved successfully!")
                        st.rerun()
    
    with tab2:
        st.header("🎯 Automatic Job Application")
        
        if not st.session_state.user_profile:
            st.warning("⚠️ Please set up your profile first in the Profile Setup tab.")
        elif not api_key:
            st.warning("⚠️ Please enter your API key in the sidebar.")
        else:
            st.success("✅ Ready to auto-fill applications!")
            
            # URL input
            application_url = st.text_input(
                "Job Application URL*",
                placeholder="https://company.com/careers/apply/job-id",
                help="Enter the direct URL to the job application form"
            )
            
            # Options
            col1, col2 = st.columns(2)
            with col1:
                review_mode = st.checkbox("Review before submit", value=True,
                                        help="Pause for manual review before submitting")
                # Get default from environment
                default_headless = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'
                headless_mode = st.checkbox("Headless browser", value=default_headless,
                                          help="Run browser in background (not recommended for first use)")
            
            with col2:
                confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.3, 0.1,
                                                help="Minimum confidence to fill fields automatically")
                # Get default wait time from environment
                default_wait_time = int(os.getenv('BROWSER_WAIT_TIME', '10'))
                wait_time = st.slider("Browser Wait Time (seconds)", 5, 30, default_wait_time, 1,
                                    help="Time to wait for page elements to load")
            
            # Start auto-apply process
            if st.button("🚀 Start Auto Apply", type="primary", disabled=not application_url):
                try:
                    # Initialize AutoApplyService
                    with st.spinner("Initializing browser and AI service..."):
                        service = AutoApplyService(
                            user_profile=st.session_state.user_profile,
                            llm_provider=llm_provider,
                            api_key=api_key
                        )
                        service.setup_driver(headless=headless_mode, wait_time=wait_time)
                        st.session_state.auto_apply_service = service
                    
                    # Start auto-fill process
                    with st.spinner("Analyzing and filling application form..."):
                        results = service.auto_fill_application(
                            url=application_url,
                            review_before_submit=review_mode
                        )
                    
                    # Display results
                    if results["success"]:
                        st.success("🎉 Application filled successfully!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Fields Analyzed", results["fields_analyzed"])
                        with col2:
                            st.metric("Fields Filled", results["fields_filled"])
                        with col3:
                            st.metric("Fields Failed", results["fields_failed"])
                        
                        # Show filled fields
                        if results["form_fields"]:
                            with st.expander("📋 Form Analysis Details"):
                                df = pd.DataFrame(results["form_fields"])
                                st.dataframe(df, use_container_width=True)
                    
                    else:
                        st.error("❌ Application filling failed")
                        if results["errors"]:
                            st.error("Errors: " + "; ".join(results["errors"]))
                    
                    # Store results in session state
                    if 'application_results' not in st.session_state:
                        st.session_state.application_results = []
                    st.session_state.application_results.append(results)
                
                except Exception as e:
                    st.error(f"❌ Error during auto-apply: {str(e)}")
                
                finally:
                    # Clean up
                    if st.session_state.auto_apply_service:
                        st.session_state.auto_apply_service.close_driver()
                        st.session_state.auto_apply_service = None
    
    with tab3:
        st.header("📊 Application Results")
        
        if 'application_results' in st.session_state and st.session_state.application_results:
            for i, result in enumerate(st.session_state.application_results):
                with st.expander(f"Application {i+1}: {result['url']}", expanded=(i == 0)):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Status", "✅ Success" if result["success"] else "❌ Failed")
                    with col2:
                        st.metric("Fields Analyzed", result["fields_analyzed"])
                    with col3:
                        st.metric("Fields Filled", result["fields_filled"])
                    with col4:
                        st.metric("Fields Failed", result["fields_failed"])
                    
                    if result["form_fields"]:
                        st.subheader("Form Analysis")
                        df = pd.DataFrame(result["form_fields"])
                        st.dataframe(df, use_container_width=True)
                    
                    if result["errors"]:
                        st.subheader("Errors")
                        for error in result["errors"]:
                            st.error(error)
            
            # Clear results button
            if st.button("🗑️ Clear Results"):
                st.session_state.application_results = []
                st.rerun()
        
        else:
            st.info("No application results yet. Use the Auto Apply tab to fill applications.")
    
    with tab4:
        st.header("🔍 Job Search Integration")
        st.info("This tab integrates with the Job Portal Service to search and apply to jobs automatically.")
        
        # Integration with JobPortalService
        if st.session_state.user_profile and api_key:
            job_service = JobPortalService()
            
            # Quick job search
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("Job Search Term", value="Software Engineer")
                location = st.text_input("Location", value="San Francisco")
            
            with col2:
                sites = st.multiselect("Job Sites", ["linkedin", "glassdoor"], default=["linkedin"])
                max_results = st.slider("Max Results", 5, 50, 10)
            
            if st.button("🔍 Search Jobs") and sites:
                with st.spinner("Searching for jobs..."):
                    try:
                        jobs_df = job_service.scrape_jobs(
                            site_name=sites,
                            search_term=search_term,
                            location=location,
                            results_wanted=max_results
                        )
                        
                        if not jobs_df.empty:
                            st.success(f"Found {len(jobs_df)} jobs!")
                            
                            # Display jobs with apply buttons
                            for idx, job in jobs_df.head(5).iterrows():
                                with st.container():
                                    st.markdown(f"**{job.get('title', 'N/A')}** at **{job.get('company', 'N/A')}**")
                                    st.write(f"Location: {job.get('location', 'N/A')}")
                                    
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        if pd.notna(job.get('description')):
                                            description = str(job.get('description'))[:200] + "..."
                                            st.write(description)
                                    
                                    with col2:
                                        if pd.notna(job.get('job_url')):
                                            if st.button(f"🤖 Auto Apply", key=f"apply_{idx}"):
                                                st.info("Auto-apply feature coming soon!")
                                    
                                    st.divider()
                        else:
                            st.warning("No jobs found. Try different search terms.")
                    
                    except Exception as e:
                        st.error(f"Error searching jobs: {str(e)}")
        else:
            st.warning("Please set up your profile and API key to use job search.")


if __name__ == "__main__":
    main()
