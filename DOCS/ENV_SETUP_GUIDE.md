# Environment Setup Guide

## Overview
This project uses a single `.env` file for all configuration. This simplifies setup and reduces confusion.

## Quick Setup

### 1. Environment File
The project uses **only** the `.env` file for configuration. If you don't have one, create it:

```bash
# Create .env file from template
cp .env.example .env
```

### 2. Required Environment Variables

Edit your `.env` file with these variables:

```bash
# LinkedIn Credentials (for authenticated scraping)
LINKEDIN_EMAIL=your_linkedin_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password

# AI Provider Configuration
OPENAI_API_KEY=sk-your-actual-openai-key-here
GROQ_API_KEY=gsk-your-actual-groq-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here

# AI Defaults
DEFAULT_AI_PROVIDER=openai
DEFAULT_MODEL=gpt-3.5-turbo

# Basic Configuration
REQUEST_TIMEOUT=10
DEFAULT_LIMIT=25
MAX_LIMIT=100
HEADLESS_MODE=false
BROWSER_WAIT_TIME=10
DEBUG_MODE=false
```

### 3. API Key Setup

#### OpenAI (Required)
1. Visit https://platform.openai.com/
2. Create account and get API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

#### Groq (Optional - Free)
1. Visit https://console.groq.com/
2. Create account and get API key  
3. Add to `.env`: `GROQ_API_KEY=gsk-...`

#### Anthropic (Optional)
1. Visit https://console.anthropic.com/
2. Create account and get API key
3. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

### 4. Test Configuration

```bash
# Test your setup
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('OpenAI:', '✅' if os.getenv('OPENAI_API_KEY') else '❌')
print('Groq:', '✅' if os.getenv('GROQ_API_KEY') else '❌')
print('LinkedIn:', '✅' if os.getenv('LINKEDIN_EMAIL') else '❌')
"
```

## File Structure

```
.env                    # Main configuration file (DO NOT COMMIT)
.env.example           # Template file (safe to commit)
.gitignore             # Ensures .env is not committed
```

## Security

- ✅ `.env` is in `.gitignore` (never committed)
- ✅ `.env.example` contains template values only
- ✅ All sensitive data stays local

## Troubleshooting

### "No AI providers available"
- Check that `OPENAI_API_KEY` is set in `.env`
- Verify API key is valid (not expired)
- Try testing with a simple OpenAI API call

### "LinkedIn authentication failed"
- Check `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` in `.env`
- Ensure credentials are correct
- Try manual login to verify account status

### "Environment variables not loading"
- Ensure `.env` file is in project root
- Check file has proper format (no quotes around values)
- Restart application after changes

## Migration from Multiple .env Files

If you had multiple .env files before:

```bash
# Backup existing files
mv .env.example .env.example.backup
mv .env.template .env.template.backup

# Use only .env going forward
# (The project now uses a single .env file)
```
