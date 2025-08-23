# AI Services Documentation

## Overview

The application now supports multiple AI providers through a unified interface:

- **OpenAI** - GPT models (primary)
- **Groq** - Fast inference with Llama, Mixtral, and Gemma models

## Architecture

### Core Components

1. **`services/ai_service.py`** - Unified AI service with provider abstraction
2. **`services/perform_ai_tagging.py`** - Job analysis and tagging service
3. **`services/ai_config_ui.py`** - Configuration UI components
4. **`UI/helper_ai_filter_tab.py`** - AI-powered filtering interface

### Provider Classes

- `BaseAIProvider` - Abstract base for all providers
- `OpenAIProvider` - OpenAI GPT models
- `GroqProvider` - Groq fast inference with Llama, Mixtral, and Gemma models

## Setup and Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# Edit your existing .env file or create a new one
nano .env
```

Add your API keys:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Groq Configuration (Optional - includes Llama models)
GROQ_API_KEY=your_groq_api_key_here

# Defaults
DEFAULT_AI_PROVIDER=openai
DEFAULT_MODEL=gpt-3.5-turbo
```

### 2. Install Dependencies

```bash
# Basic requirements (already in requirements.txt)
pip install openai python-dotenv

# Optional: For Groq support (includes Llama models)
pip install groq
```

### 3. Provider Priority

The system automatically selects providers in this order:
1. OpenAI (if API key available)
2. Groq (if API key available, includes Llama models)

## Usage

### Basic AI Service Usage

```python
from services.ai_service import ai_service

# Check availability
if ai_service.is_available():
    # Generate completion
    response = ai_service.generate_completion(
        messages=[{"role": "user", "content": "Hello AI!"}],
        max_tokens=100,
        temperature=0.7
    )
    
    # Generate JSON response
    json_response = ai_service.generate_json_completion(
        prompt="Analyze this job: {job_text}",
        max_tokens=200
    )

# Get provider info
info = ai_service.get_provider_info()
print(f"Current provider: {info['current_provider']}")
print(f"Available models: {info['available_models']}")

# Switch provider
ai_service.set_provider("groq", "llama3-8b-8192")
```

### AI Tagging Service

```python
from services.perform_ai_tagging import ai_tagging_service
import pandas as pd

# Create job data
jobs_df = pd.DataFrame({
    'title': ['Python Developer'],
    'company': ['TechCorp'],
    'description': ['Python development role...']
})

# Add AI tags
tagged_df = ai_tagging_service.tag_jobs(jobs_df)

# AI-powered search
results = ai_tagging_service.search_jobs_with_ai(
    jobs_df, 
    "Senior Python developer with ML experience"
)
```

### UI Configuration

```python
from services.ai_config_ui import ai_config_ui

# In your Streamlit app
def render_ai_tab():
    ai_config_ui.render_ai_config_tab()

# In sidebar
def render_sidebar():
    ai_config_ui.render_ai_status_sidebar()
```

## Provider Details

### OpenAI Provider

**Models Available:**
- `gpt-3.5-turbo` (default)
- `gpt-3.5-turbo-16k`
- `gpt-4`
- `gpt-4-turbo-preview`
- `gpt-4o`
- `gpt-4o-mini`

**Setup:**
1. Get API key from https://platform.openai.com/
2. Add to `.env`: `OPENAI_API_KEY=sk-...`

### Groq Provider

**Models Available:**
- **Llama Models:**
  - `llama-3.1-8b-instant` (default)
  - `llama-3.1-70b-versatile`
  - `llama-3.1-405b-reasoning`
  - `llama3-8b-8192`
  - `llama3-70b-8192`
- **Mixtral Models:**
  - `mixtral-8x7b-32768`
- **Gemma Models:**
  - `gemma-7b-it`
  - `gemma2-9b-it`

**Features:**
- Fast inference (much faster than OpenAI)
- Free tier available
- Good for development and testing
- Includes all Llama model variants

**Setup:**
1. Get API key from https://console.groq.com/
2. Install: `pip install groq`
3. Add to `.env`: `GROQ_API_KEY=gsk_...`

## Error Handling and Fallbacks

### Automatic Fallbacks

1. **API Quota Exceeded**: Falls back to mock analysis
2. **Network Issues**: Retries with exponential backoff
3. **Provider Unavailable**: Switches to next available provider
4. **Invalid Response**: Uses mock data with warnings

### Mock Analysis

When AI services are unavailable, the system provides mock analysis:

```python
# Mock job analysis
{
    "tags": "software-development, programming, backend",
    "skills": "Python, JavaScript, SQL, Git", 
    "category": "Software Engineering",
    "seniority": "Senior",
    "relevance_score": 0.85
}
```

## Performance Optimization

### Caching

- Search results cached in session state
- Provider initialization cached
- Model responses cached for identical prompts

### Rate Limiting

- Built-in retry logic with exponential backoff
- Request queuing for high-volume operations
- Progress tracking for long operations

### Model Selection

**For Speed:**
- Groq: `llama-3.1-8b-instant` (fastest)
- OpenAI: `gpt-3.5-turbo` (fast, good quality)

**For Quality:**
- OpenAI: `gpt-4o` (best quality)
- Groq: `llama-3.1-405b-reasoning` (high quality, fast)

**For Cost:**
- Groq: Any model (free tier, includes Llama)
- OpenAI: `gpt-3.5-turbo` (cheapest OpenAI)

## Monitoring and Debugging

### Status Monitoring

```python
# Check service status
status = ai_config_ui.get_ai_status_info()
print(f"Status: {status['status']}")
print(f"Provider: {status['provider']}")
```

### Debug Mode

Set environment variable for detailed logging:
```bash
export AI_DEBUG=true
```

### Common Issues

1. **"No AI providers available"**
   - Check API keys in `.env`
   - Verify internet connection
   - Check provider status pages

2. **"API quota exceeded"**
   - Check billing/usage on provider dashboard
   - Try different provider
   - Use mock mode for development

3. **"Invalid JSON response"**
   - Usually temporary API issue
   - System automatically retries
   - Falls back to mock data

## Integration Examples

### Adding New Provider

```python
class NewAIProvider(BaseAIProvider):
    def _initialize_client(self):
        # Initialize your provider's client
        pass
    
    def is_available(self):
        # Check if provider is ready
        return True
    
    def generate_completion(self, messages, max_tokens, temperature, model):
        # Implement completion generation
        pass
    
    def get_default_model(self):
        return "your-default-model"

# Add to UnifiedAIService.__init__
new_provider = NewAIProvider()
if new_provider.is_available():
    self.providers['new_provider'] = new_provider
```

### Custom Analysis

```python
def custom_job_analysis(job_text):
    prompt = f"""
    Custom analysis prompt for: {job_text}
    Return specific format...
    """
    
    return ai_service.generate_json_completion(
        prompt=prompt,
        max_tokens=300,
        temperature=0.3
    )
```

## API Reference

See individual service files for detailed API documentation:

- `services/ai_service.py` - Core AI service methods
- `services/perform_ai_tagging.py` - Job analysis methods  
- `services/ai_config_ui.py` - UI component methods

## Troubleshooting

### Check Service Status
1. Open AI Configuration tab in dashboard
2. View provider status and available models
3. Test AI functionality with test prompt

### Reset Configuration
```python
# Clear all AI cache
ai_service._initialize_providers()
ai_service._select_best_provider()
```

### Manual Provider Selection
```python
# Force specific provider (use Groq for Llama models)
ai_service.set_provider("groq", "llama-3.1-8b-instant")
```
