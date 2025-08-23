# 🤖 AutoApply Service

Automatically fill job application forms using AI analysis and web automation.

## 🌟 Features

- **LLM-Powered Analysis**: Uses OpenAI GPT-4 or Anthropic Claude to analyze HTML forms
- **Smart Field Mapping**: Intelligently maps form fields to user profile data
- **Web Automation**: Selenium-based browser automation for form filling
- **Review Mode**: Pause for manual review before submission
- **Profile Management**: Save and load user profiles
- **Resume Analysis**: Auto-generate profiles from resume text
- **Streamlit Dashboard**: User-friendly web interface

## 🚀 Quick Start

### 1. Prerequisites

- **ChromeDriver**: Download from [ChromeDriver](https://chromedriver.chromium.org/)
- **API Key**: Get an API key from [OpenAI](https://platform.openai.com/) or [Anthropic](https://console.anthropic.com/)

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Download ChromeDriver and add to PATH
# Or place in project directory
```

### 3. Basic Usage

```python
from services.auto_apply_service import AutoApplyService, UserProfile

# Create user profile
profile = UserProfile(
    first_name="John",
    last_name="Doe",
    email="john.doe@email.com",
    phone="+1-555-123-4567",
    current_title="Software Engineer",
    # ... add more fields
)

# Initialize service
service = AutoApplyService(
    user_profile=profile,
    llm_provider="openai",  # or "anthropic"
    api_key="your-api-key"
)

# Fill application
results = service.auto_fill_application(
    url="https://company.com/careers/apply/123",
    review_before_submit=True
)

print(f"Fields filled: {results['fields_filled']}")
```

### 4. Using the Dashboard

```bash
# Launch Streamlit dashboard
streamlit run auto_apply_dashboard.py
```

## 📋 User Profile Fields

The `UserProfile` class supports comprehensive user information:

### Personal Information
- `first_name`, `last_name`, `email`, `phone`
- `address`, `city`, `state`, `zip_code`, `country`

### Professional Information
- `current_title`, `years_of_experience`
- `linkedin_url`, `portfolio_url`, `github_url`
- `salary_expectation`, `notice_period`

### Education
- `education_level`, `university`, `degree`
- `graduation_year`, `gpa`

### Skills & Experience
- `skills` (list of strings)
- `resume_text`, `cover_letter_template`

### Work Authorization
- `work_authorized`, `visa_status`
- `security_clearance`, `willing_to_relocate`

## 🔧 Configuration

### API Keys

Set your API keys in environment variables or pass directly:

```python
# Environment variables
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Or pass directly
service = AutoApplyService(profile, "openai", "your-key")
```

### Browser Settings

```python
# Headless mode (no visible browser)
service.setup_driver(headless=True)

# Custom wait time
service.setup_driver(wait_time=15)
```

## 🎯 How It Works

1. **Page Analysis**: Loads the job application page
2. **HTML Extraction**: Extracts form elements and structure
3. **LLM Analysis**: Sends HTML to LLM for field identification
4. **Smart Mapping**: Maps form fields to user profile data
5. **Automated Filling**: Uses Selenium to fill identified fields
6. **Review & Submit**: Optional manual review before submission

## 📊 Form Field Analysis

The LLM analyzes forms and returns structured data:

```json
{
  "element_id": "firstName",
  "element_type": "text",
  "label": "First Name",
  "suggested_value": "John",
  "confidence": 0.95
}
```

## 🛡️ Safety Features

- **Review Mode**: Always pause for manual review by default
- **Confidence Thresholds**: Only fill fields with high confidence
- **Error Handling**: Graceful failure handling
- **No Auto-Submit**: Never submits forms automatically

## 🎨 Dashboard Features

### Profile Setup
- Visual form for creating user profiles
- Resume upload for auto-profile generation
- Profile save/load functionality

### Auto Apply
- URL input for job applications
- Real-time progress tracking
- Detailed results display

### Results Tracking
- History of all application attempts
- Success/failure metrics
- Detailed field analysis

### Job Search Integration
- Integration with JobPortalService
- Search and auto-apply workflow

## 🔍 Example Applications

### Corporate Career Pages
- Company-specific application forms
- ATS (Applicant Tracking System) forms
- Custom job application portals

### Job Boards
- LinkedIn Easy Apply
- Indeed applications
- Glassdoor applications

## ⚠️ Important Notes

### Legal & Ethical Considerations
- Only use on applications you intend to submit
- Review all filled information before submitting
- Respect website terms of service
- Use responsibly and ethically

### Technical Limitations
- Requires ChromeDriver installation
- JavaScript-heavy sites may need additional handling
- CAPTCHA protection will require manual intervention
- Some complex forms may need manual completion

### Rate Limiting
- Implement delays between applications
- Respect website rate limits
- Monitor for IP blocking

## 🛠️ Troubleshooting

### ChromeDriver Issues
```bash
# Check ChromeDriver installation
chromedriver --version

# Download latest version
# https://chromedriver.chromium.org/
```

### API Errors
- Verify API key is correct
- Check API usage limits
- Ensure sufficient API credits

### Form Detection Issues
- Try with `headless=False` to see browser
- Check if site uses JavaScript for form loading
- Verify form elements are not in iframes

## 🔮 Future Enhancements

- PDF resume parsing
- CAPTCHA solving integration
- Multi-browser support
- Mobile application support
- Integration with more job boards
- Advanced form field detection
- Machine learning for better field mapping

## 📄 License

This project is for educational and personal use. Please use responsibly and in accordance with website terms of service.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example scripts
3. Open an issue on GitHub
