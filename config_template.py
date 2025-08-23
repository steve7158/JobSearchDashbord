# Configuration file for AutoApplyService
# Copy this file to config.py and fill in your details

# LLM API Configuration
LLM_PROVIDER = "openai"  # "openai" or "anthropic"
OPENAI_API_KEY = "your-openai-api-key-here"
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"

# WebDriver Configuration
CHROME_DRIVER_PATH = ""  # Leave empty to use system PATH
HEADLESS_MODE = False  # Set to True for headless browsing
WAIT_TIME = 10  # Seconds to wait for elements

# Default User Profile
DEFAULT_USER_PROFILE = {
    "first_name": "Your First Name",
    "last_name": "Your Last Name",
    "email": "your.email@example.com",
    "phone": "+1-555-123-4567",
    "address": "123 Your Street",
    "city": "Your City",
    "state": "Your State",
    "zip_code": "12345",
    "country": "USA",
    "current_title": "Your Current Job Title",
    "years_of_experience": "5",
    "linkedin_url": "https://linkedin.com/in/yourprofile",
    "github_url": "https://github.com/yourusername",
    "portfolio_url": "https://yourportfolio.com",
    "education_level": "Bachelor's",
    "university": "Your University",
    "degree": "Your Degree",
    "graduation_year": "2020",
    "skills": ["Skill1", "Skill2", "Skill3"],
    "work_authorized": True,
    "visa_status": "Citizen",
    "salary_expectation": "100000",
    "notice_period": "2 weeks",
    "willing_to_relocate": False
}
