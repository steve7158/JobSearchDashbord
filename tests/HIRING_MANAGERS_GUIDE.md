# 🧑‍💼 Hiring Manager Extraction Feature

## Overview

The JobPortalService now includes functionality to extract hiring manager details from LinkedIn job pages. This feature can fetch information from the "Meet the hiring team" section of LinkedIn job postings.

## Features

- **Automatic extraction** of hiring manager names, titles, and LinkedIn profiles
- **Batch processing** for multiple LinkedIn jobs
- **Integration** with the existing job scraping dashboard
- **Progress tracking** and error handling
- **Detailed statistics** and reporting

## Prerequisites

### 1. Install ChromeDriver

The hiring manager extraction uses Selenium WebDriver with Chrome. You need to have Chrome and ChromeDriver installed.

**Option A: Install via package manager**
```bash
# macOS with Homebrew
brew install chromedriver

# Or install Chrome browser if not already installed
brew install --cask google-chrome
```

**Option B: Manual installation**
1. Download ChromeDriver from: https://chromedriver.chromium.org/
2. Extract and place in your PATH (e.g., `/usr/local/bin/`)
3. Make it executable: `chmod +x /usr/local/bin/chromedriver`

**Option C: Let Selenium manage it automatically**
```bash
# Install webdriver-manager for automatic ChromeDriver management
pip install webdriver-manager
```

### 2. Required Dependencies

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Basic Usage in Code

```python
from services.job_portal_service import JobPortalService

# Initialize service
service = JobPortalService()

# Scrape LinkedIn jobs
jobs_df = service.scrape_jobs(
    site_name=["linkedin"],
    search_term="Software Engineer",
    location="San Francisco",
    results_wanted=10,
    linkedin_fetch_description=True
)

# Fetch hiring managers for all LinkedIn jobs
jobs_with_managers = service.fetch_hiring_managers_for_jobs(jobs_df)

# View results
print(jobs_with_managers[['title', 'company', 'hiring_managers_count', 'hiring_managers_names']])
```

### 2. Single Job URL Testing

```python
# Test with a specific LinkedIn job URL
job_url = "https://www.linkedin.com/jobs/view/1234567890/"
result = service.fetch_hiring_manager_details(job_url)

if result['success']:
    print(f"Found {len(result['hiring_managers'])} hiring manager(s)")
    for manager in result['hiring_managers']:
        print(f"- {manager['name']} ({manager['title']})")
        if manager.get('profile_url'):
            print(f"  Profile: {manager['profile_url']}")
else:
    print(f"Error: {result['error']}")
```

### 3. Using the Dashboard

1. **Start the dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

2. **Search for jobs** using the sidebar controls

3. **Fetch hiring managers**:
   - After jobs are loaded, scroll down to the "🧑‍💼 Hiring Manager Details" section
   - Click "🔍 Fetch Hiring Managers" button
   - Wait for the process to complete (may take several minutes)

4. **View results**:
   - Hiring manager info will appear in job listings
   - Statistics will show in the hiring manager section
   - Use the expandable sections to see detailed manager information

## Data Structure

The hiring manager extraction adds the following columns to the jobs DataFrame:

- `hiring_managers_count`: Number of hiring managers found
- `hiring_managers_names`: Names separated by " | "
- `hiring_managers_titles`: Job titles separated by " | "
- `hiring_managers_profiles`: LinkedIn profile URLs separated by " | "
- `hiring_manager_fetch_success`: Boolean indicating if fetch was successful

## Example Output

```
Title: Senior Software Engineer
Company: TechCorp
Hiring Managers: 2 found
Hiring Team: John Smith (Engineering Manager) • Jane Doe (Senior Director)
```

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   ```
   Error: 'chromedriver' executable needs to be in PATH
   ```
   **Solution**: Install ChromeDriver using one of the methods above.

2. **LinkedIn blocking requests**
   ```
   Error: Could not access LinkedIn page
   ```
   **Solution**: The script includes delays and user-agent headers to minimize blocking. If issues persist, try running with longer delays between requests.

3. **No hiring managers found**
   ```
   Success: True, but hiring_managers: []
   ```
   **Solution**: Not all LinkedIn job postings have hiring manager information. This is normal.

### Rate Limiting

- The script includes built-in delays (2 seconds between requests)
- For large batches, consider running in smaller chunks
- LinkedIn may temporarily block requests if too many are made quickly

### Browser Issues

If you encounter browser-related errors:

1. **Update Chrome**: Ensure you have the latest version
2. **Update ChromeDriver**: Download the matching version for your Chrome
3. **Check permissions**: Ensure ChromeDriver has execution permissions

## Performance Notes

- **Processing time**: ~3-5 seconds per LinkedIn job
- **Success rate**: Typically 60-80% (depends on job postings having hiring team info)
- **Memory usage**: Minimal, as each browser session is closed after processing

## Privacy and Ethics

- This tool only extracts publicly available information from LinkedIn job postings
- No login credentials are required or stored
- Respects LinkedIn's rate limiting through built-in delays
- Only accesses the "Meet the hiring team" section of job postings

## Future Enhancements

Potential improvements for future versions:

- Support for other job platforms
- Enhanced extraction of additional hiring team details
- Export functionality for hiring manager contact information
- Integration with CRM systems
- Batch processing optimizations

## API Reference

### `fetch_hiring_manager_details(job_url, max_retries=3)`

Fetch hiring manager details from a single LinkedIn job URL.

**Parameters:**
- `job_url` (str): LinkedIn job URL
- `max_retries` (int): Maximum retry attempts

**Returns:**
```python
{
    'success': bool,
    'hiring_managers': [
        {
            'name': str,
            'title': str,
            'profile_url': str,
            'image_url': str,
            'company': str
        }
    ],
    'error': str  # Only if success is False
}
```

### `fetch_hiring_managers_for_jobs(jobs_df, job_urls_column='job_url')`

Fetch hiring managers for all LinkedIn jobs in a DataFrame.

**Parameters:**
- `jobs_df` (pd.DataFrame): DataFrame containing job data
- `job_urls_column` (str): Column name containing job URLs

**Returns:**
- `pd.DataFrame`: Original DataFrame with additional hiring manager columns

## Examples

See `test_hiring_managers.py` for complete examples and test cases.
