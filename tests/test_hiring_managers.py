#!/usr/bin/env python3
"""
Test script for hiring manager extraction functionality.
"""

import sys
import os
import pandas as pd

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from services.job_portal_service import JobPortalService


def test_hiring_manager_extraction():
    """Test the hiring manager extraction functionality."""
    
    print("🚀 Testing Hiring Manager Extraction")
    print("=" * 50)
    
    # Initialize service
    service = JobPortalService()
    
    # Test with a sample LinkedIn job URL (replace with actual URL)
    test_url = "https://www.linkedin.com/jobs/view/3234567890/"  # Replace with real URL
    
    print(f"📋 Testing URL: {test_url}")
    print("Note: Replace with an actual LinkedIn job URL for real testing")
    
    # Test single URL extraction
    print("\n🔍 Testing single URL extraction...")
    result = service.fetch_hiring_manager_details(test_url)
    
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Found {len(result['hiring_managers'])} hiring manager(s):")
        for i, manager in enumerate(result['hiring_managers'], 1):
            print(f"  {i}. Name: {manager.get('name', 'Unknown')}")
            print(f"     Title: {manager.get('title', 'Unknown')}")
            print(f"     Profile: {manager.get('profile_url', 'N/A')}")
            print(f"     Company: {manager.get('company', 'Unknown')}")
            print()
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Test with job scraping integration
    print("\n🔍 Testing integration with job scraping...")
    
    # Create sample DataFrame with LinkedIn jobs
    sample_jobs = pd.DataFrame({
        'title': ['AI Engineer', 'Data Scientist', 'Software Engineer'],
        'company': ['TechCorp', 'DataInc', 'SoftwareLabs'],
        'job_url': [
            'https://www.linkedin.com/jobs/view/1234567890/',
            'https://www.linkedin.com/jobs/view/1234567891/',
            'https://www.linkedin.com/jobs/view/1234567892/'
        ],
        'location': ['San Francisco', 'New York', 'Seattle']
    })
    
    print(f"📊 Sample DataFrame with {len(sample_jobs)} jobs:")
    print(sample_jobs[['title', 'company', 'location']].to_string(index=False))
    
    # Note about real testing
    print(f"\n💡 For real testing:")
    print(f"1. Replace test URLs with actual LinkedIn job URLs")
    print(f"2. Use the JobPortalService.scrape_jobs() method to get real job data")
    print(f"3. Call fetch_hiring_managers_for_jobs() on the resulting DataFrame")
    
    # Example of how to use with real data
    print(f"\n📝 Example usage with real job scraping:")
    print("""
# Scrape real jobs
jobs_df = service.scrape_jobs(
    site_name=["linkedin"],
    search_term="AI Engineer",
    location="San Francisco",
    results_wanted=10,
    linkedin_fetch_description=True
)

# Fetch hiring managers for all LinkedIn jobs
jobs_with_managers = service.fetch_hiring_managers_for_jobs(jobs_df)

# View results
print(jobs_with_managers[['title', 'company', 'hiring_managers_count', 'hiring_managers_names']].to_string())
""")


def demo_real_job_scraping_with_hiring_managers():
    """
    Demo function showing how to scrape jobs and fetch hiring managers.
    Uncomment and modify as needed for real testing.
    """
    print("\n🎯 Real Job Scraping Demo")
    print("=" * 30)
    
    service = JobPortalService()
    
    # Uncomment and modify for real testing
    """
    # Scrape LinkedIn jobs
    print("🔍 Scraping LinkedIn jobs...")
    jobs_df = service.scrape_jobs(
        site_name=["linkedin"],
        search_term="Software Engineer",
        location="San Francisco",
        results_wanted=5,  # Keep small for testing
        linkedin_fetch_description=True
    )
    
    print(f"Found {len(jobs_df)} jobs")
    
    # Fetch hiring managers
    print("🧑‍💼 Fetching hiring managers...")
    jobs_with_managers = service.fetch_hiring_managers_for_jobs(jobs_df)
    
    # Display results
    columns_to_show = [
        'title', 'company', 'location', 
        'hiring_managers_count', 'hiring_managers_names', 'hiring_managers_titles'
    ]
    
    print("\n📊 Results:")
    print(jobs_with_managers[columns_to_show].to_string(index=False))
    
    # Save results
    jobs_with_managers.to_csv('jobs_with_hiring_managers.csv', index=False)
    print("\n💾 Results saved to jobs_with_hiring_managers.csv")
    """
    
    print("💡 Uncomment the code above and run to test with real data")


if __name__ == "__main__":
    test_hiring_manager_extraction()
    
    print("\n" + "="*60)
    demo_real_job_scraping_with_hiring_managers()
