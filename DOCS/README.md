# JobSearchSidebar UI Component

A reusable Streamlit UI component class for job search configuration and LinkedIn authentication.

## Overview

The `JobSearchSidebar` class encapsulates all the sidebar functionality for job search configuration, making it easy to reuse across different parts of your application.

## Features

- **LinkedIn Authentication**: Secure credential management with environment variable support
- **Job Search Configuration**: Comprehensive search parameter setup
- **Advanced Settings**: Additional configuration options for power users
- **Modular Design**: Easy to integrate and customize
- **Type Hints**: Full type annotation support

## Usage

### Basic Usage

```python
from UI.ui_sidebar import JobSearchSidebar
from services.job_portal_service import JobPortalService

# Create a factory function for job service
def get_job_service(linkedin_email=None, linkedin_password=None):
    return JobPortalService(linkedin_email=linkedin_email, linkedin_password=linkedin_password)

# Initialize the sidebar component
sidebar = JobSearchSidebar(get_job_service_func=get_job_service)

# Render the sidebar and get configuration
search_config, search_button_pressed, job_service = sidebar.render()

# Use the configuration
if search_button_pressed:
    # Process the search with the collected configuration
    print(f"Searching for: {search_config['search_term']}")
    print(f"Location: {search_config['location']}")
    print(f"Sites: {search_config['selected_sites']}")
```

### Configuration Options

The `render()` method returns a tuple containing:

1. **search_config** (Dict): Complete search configuration
2. **search_button_pressed** (bool): Whether the search button was clicked
3. **job_service**: Initialized JobPortalService instance

#### Search Configuration Dictionary

```python
{
    'selected_sites': ['linkedin', 'glassdoor'],      # List of selected job sites
    'search_term': 'Software Engineer',               # Job search keywords
    'location': 'San Francisco',                      # Job location
    'results_wanted': 20,                             # Number of results to fetch
    'hours_old': 72,                                  # Maximum job age in hours
    'linkedin_description': True,                     # Whether to fetch detailed descriptions
    'google_search_term': 'Software Engineer jobs...', # Custom Google search query
    'country_indeed': 'USA',                         # Indeed country selection
    'linkedin_email': 'user@example.com',            # LinkedIn email (if provided)
    'linkedin_password': '...'                       # LinkedIn password (if provided)
}
```

### LinkedIn Authentication

The component supports multiple authentication methods:

1. **Environment Variables** (Recommended):
   ```bash
   # In your .env file
   LINKEDIN_EMAIL=your-email@example.com
   LINKEDIN_PASSWORD=your-password
   ```

2. **Manual Input** (Less secure):
   - Users can enter credentials directly in the UI
   - Credentials are not stored persistently

### Customization

You can customize default values by modifying the class properties:

```python
sidebar = JobSearchSidebar(get_job_service_func=get_job_service)

# Customize defaults
sidebar.default_search_term = "Data Scientist"
sidebar.default_location = "New York"
sidebar.default_results = 50
sidebar.available_sites = ["linkedin", "glassdoor", "indeed"]

# Render with custom defaults
search_config, search_button_pressed, job_service = sidebar.render()
```

## Class Methods

### `__init__(self, get_job_service_func)`
Initialize the sidebar component.

**Parameters:**
- `get_job_service_func`: Function that returns a JobPortalService instance

### `render(self) -> Tuple[Dict[str, Any], bool, Any]`
Render the complete sidebar UI and return configuration.

**Returns:**
- `search_config`: Dictionary containing all search parameters
- `search_button_pressed`: Boolean indicating if search was triggered
- `job_service`: Initialized JobPortalService instance

### Private Methods

- `_render_linkedin_auth_section()`: Handles LinkedIn authentication UI
- `_render_auth_status_indicator()`: Shows authentication status
- `_render_search_configuration()`: Renders main search parameters
- `_render_advanced_settings()`: Renders advanced configuration options

## Integration Example

Here's how to integrate the sidebar into an existing Streamlit application:

```python
import streamlit as st
from UI.ui_sidebar import JobSearchSidebar

def main():
    st.set_page_config(page_title="Job Dashboard", layout="wide")
    
    # Initialize sidebar
    sidebar = JobSearchSidebar(get_job_service_func=get_job_service)
    search_config, search_pressed, job_service = sidebar.render()
    
    # Main content
    st.title("Job Search Dashboard")
    
    if search_pressed and search_config['selected_sites']:
        # Perform job search
        results = job_service.scrape_jobs(
            site_name=search_config['selected_sites'],
            search_term=search_config['search_term'],
            location=search_config['location'],
            results_wanted=search_config['results_wanted']
        )
        
        # Display results
        st.dataframe(results)
    else:
        st.info("Configure search parameters and click Search Jobs")

if __name__ == "__main__":
    main()
```

## Error Handling

The component includes built-in error handling for:
- Missing environment variables
- Invalid credential formats
- Network connection issues (handled by JobPortalService)

## Security Considerations

1. **Environment Variables**: Always use `.env` files for credentials
2. **Session State**: Credentials are not stored in Streamlit session state
3. **Input Validation**: User inputs are validated before processing
4. **Secure Defaults**: Secure authentication methods are preferred

## Dependencies

- `streamlit`: Web UI framework
- `os`: Environment variable access
- `typing`: Type hints support

## Best Practices

1. **Use Environment Variables**: Store sensitive credentials in `.env` files
2. **Factory Pattern**: Use factory functions for service initialization
3. **Type Hints**: Leverage type annotations for better code clarity
4. **Modular Design**: Keep UI components separate from business logic
5. **Error Handling**: Implement proper error handling and user feedback
