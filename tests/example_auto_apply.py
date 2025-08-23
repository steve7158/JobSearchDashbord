#!/usr/bin/env python3
"""
Example script demonstrating how to use the AutoApplyService
"""

import os
import sys
from services.auto_apply_service import AutoApplyService, UserProfile

def main():
    print("🤖 AutoApplyService Example")
    print("=" * 50)
    
    # Check for ChromeDriver
    print("📋 Pre-flight checks:")
    print("1. ChromeDriver: Run 'chromedriver --version' to verify installation")
    print("2. API Key: Make sure you have OpenAI or Anthropic API key")
    print("3. Job URL: Have a job application URL ready")
    print()
    
    # Create sample user profile
    sample_profile = UserProfile(
        first_name="John",
        last_name="Doe", 
        email="john.doe@email.com",
        phone="+1-555-123-4567",
        address="123 Tech Street",
        city="San Francisco",
        state="CA",
        zip_code="94105",
        country="USA",
        current_title="Senior Software Engineer",
        years_of_experience="5",
        linkedin_url="https://linkedin.com/in/johndoe",
        github_url="https://github.com/johndoe",
        education_level="Bachelor's",
        university="Stanford University", 
        degree="Computer Science",
        graduation_year="2018",
        skills=["Python", "JavaScript", "React", "AWS", "Machine Learning"],
        work_authorized=True,
        salary_expectation="120000",
        notice_period="2 weeks",
        willing_to_relocate=True
    )
    
    print("👤 Sample User Profile Created:")
    print(f"   Name: {sample_profile.full_name}")
    print(f"   Email: {sample_profile.email}")
    print(f"   Title: {sample_profile.current_title}")
    print(f"   Experience: {sample_profile.years_of_experience} years")
    print(f"   Skills: {', '.join(sample_profile.skills[:3])}...")
    print()
    
    # Get user input
    print("🔧 Configuration:")
    
    # LLM Provider
    while True:
        llm_provider = input("Choose LLM provider (openai/anthropic): ").strip().lower()
        if llm_provider in ['openai', 'anthropic']:
            break
        print("Please enter 'openai' or 'anthropic'")
    
    # API Key
    api_key = input(f"Enter your {llm_provider.upper()} API key: ").strip()
    if not api_key:
        print("❌ API key is required")
        return
    
    # Job Application URL
    job_url = input("Enter job application URL: ").strip()
    if not job_url:
        print("❌ Job URL is required")
        return
    
    # Headless mode
    headless = input("Run in headless mode? (y/n): ").strip().lower() == 'y'
    
    print("\n🚀 Starting AutoApply Process...")
    print("=" * 50)
    
    try:
        # Initialize service
        service = AutoApplyService(
            user_profile=sample_profile,
            llm_provider=llm_provider,
            api_key=api_key
        )
        
        # Setup browser
        print("🌐 Setting up browser...")
        service.setup_driver(headless=headless)
        
        # Fill application
        print("🤖 Analyzing and filling application...")
        results = service.auto_fill_application(
            url=job_url,
            review_before_submit=True
        )
        
        # Display results
        print("\n📊 Results:")
        print("=" * 30)
        print(f"✅ Success: {results['success']}")
        print(f"📋 Fields analyzed: {results['fields_analyzed']}")
        print(f"✅ Fields filled: {results['fields_filled']}")
        print(f"❌ Fields failed: {results['fields_failed']}")
        
        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"   • {error}")
        
        if results['form_fields']:
            print(f"\n📝 Form Analysis:")
            for field in results['form_fields']:
                if field['confidence'] > 0.3:
                    print(f"   ✅ {field['label']}: {field['suggested_value']} (confidence: {field['confidence']:.2f})")
                else:
                    print(f"   ⚠️  {field['label']}: Low confidence ({field['confidence']:.2f})")
        
        print(f"\n🎉 AutoApply process completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        # Cleanup
        try:
            service.close_driver()
        except:
            pass
        print("🔒 Browser closed")

if __name__ == "__main__":
    main()
