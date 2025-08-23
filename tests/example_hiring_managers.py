#!/usr/bin/env python3
"""
Simple example demonstrating hiring manager extraction.
This example shows how to use the feature with real LinkedIn job URLs.
"""

from services.job_portal_service import JobPortalService
import pandas as pd


def example_search_and_extract():
    """Example: Search for jobs and extract hiring managers."""
    
    print("🚀 Job Search & Hiring Manager Extraction Demo")
    print("=" * 50)
    
    # Initialize service
    service = JobPortalService()
    
    # Step 1: Search for jobs
    print("📋 Step 1: Searching for LinkedIn jobs...")
    
    try:
        jobs_df = service.scrape_jobs(
            site_name=["linkedin"],
            search_term="Software Engineer",
            location="San Francisco",
            results_wanted=5,  # Keep small for demo
            linkedin_fetch_description=True
        )
        
        print(f"✅ Found {len(jobs_df)} jobs")
        
        # Step 2: Extract hiring managers
        print("\n🧑‍💼 Step 2: Extracting hiring managers...")
        print("⏳ This may take a few minutes...")
        
        jobs_with_managers = service.fetch_hiring_managers_for_jobs(jobs_df)
        
        # Step 3: Display results
        print("\n📊 Step 3: Results Summary")
        
        total_jobs = len(jobs_with_managers)
        jobs_with_managers_count = (jobs_with_managers['hiring_managers_count'] > 0).sum() if 'hiring_managers_count' in jobs_with_managers.columns else 0
        total_managers = jobs_with_managers['hiring_managers_count'].sum() if 'hiring_managers_count' in jobs_with_managers.columns else 0
        
        print(f"Total jobs processed: {total_jobs}")
        print(f"Jobs with hiring managers: {jobs_with_managers_count}")
        print(f"Total hiring managers found: {int(total_managers)}")
        print(f"Success rate: {(jobs_with_managers_count/total_jobs)*100:.1f}%")
        
        # Step 4: Show detailed results
        print("\n📋 Step 4: Detailed Results")
        print("-" * 50)
        
        for idx, job in jobs_with_managers.iterrows():
            print(f"\n{idx + 1}. {job.get('title', 'Unknown Title')}")
            print(f"   Company: {job.get('company', 'Unknown')}")
            print(f"   Location: {job.get('location', 'Unknown')}")
            
            if job.get('hiring_managers_count', 0) > 0:
                managers = job.get('hiring_managers_names', '').split(' | ')
                titles = job.get('hiring_managers_titles', '').split(' | ')
                profiles = job.get('hiring_managers_profiles', '').split(' | ')
                
                print(f"   👥 Hiring Managers ({int(job['hiring_managers_count'])}):")
                
                for i, manager in enumerate(managers):
                    if manager.strip():
                        title = titles[i] if i < len(titles) and titles[i].strip() else "Unknown Title"
                        profile = profiles[i] if i < len(profiles) and profiles[i].strip() else ""
                        
                        print(f"      • {manager} - {title}")
                        if profile:
                            print(f"        LinkedIn: {profile}")
            else:
                print("   👥 No hiring managers found")
        
        # Step 5: Save results
        output_file = "jobs_with_hiring_managers.csv"
        jobs_with_managers.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to: {output_file}")
        
        return jobs_with_managers
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure ChromeDriver is installed and in PATH")
        print("2. Check your internet connection")
        print("3. Try with a smaller number of jobs first")
        return None


def example_single_job():
    """Example: Extract hiring managers from a single job URL."""
    
    print("\n🔍 Single Job URL Demo")
    print("=" * 30)
    
    # Replace this with a real LinkedIn job URL for testing
    example_url = "https://www.linkedin.com/jobs/view/3234567890/"
    
    print(f"Testing URL: {example_url}")
    print("⚠️ Note: Replace with a real LinkedIn job URL for actual testing")
    
    service = JobPortalService()
    
    try:
        result = service.fetch_hiring_manager_details(example_url)
        
        if result['success']:
            managers = result['hiring_managers']
            print(f"✅ Success! Found {len(managers)} hiring manager(s)")
            
            for i, manager in enumerate(managers, 1):
                print(f"\n{i}. {manager.get('name', 'Unknown')}")
                print(f"   Title: {manager.get('title', 'Unknown')}")
                print(f"   Company: {manager.get('company', 'Unknown')}")
                if manager.get('profile_url'):
                    print(f"   Profile: {manager.get('profile_url')}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def example_with_existing_data():
    """Example: Use hiring manager extraction with existing job data."""
    
    print("\n📊 Existing Data Demo")
    print("=" * 25)
    
    # Create sample job data (replace with real data)
    sample_jobs = pd.DataFrame({
        'title': [
            'Senior Software Engineer',
            'Data Scientist',
            'Product Manager',
            'Frontend Developer'
        ],
        'company': [
            'TechCorp',
            'DataScience Inc',
            'ProductCo',
            'WebDev Studios'
        ],
        'location': [
            'San Francisco, CA',
            'New York, NY',
            'Seattle, WA',
            'Austin, TX'
        ],
        'job_url': [
            'https://www.linkedin.com/jobs/view/1111111111/',
            'https://www.linkedin.com/jobs/view/2222222222/',
            'https://www.linkedin.com/jobs/view/3333333333/',
            'https://www.linkedin.com/jobs/view/4444444444/'
        ]
    })
    
    print(f"Sample DataFrame with {len(sample_jobs)} LinkedIn jobs:")
    print(sample_jobs[['title', 'company', 'location']].to_string(index=False))
    
    print("\n💡 To use with real data:")
    print("1. Replace the sample URLs with real LinkedIn job URLs")
    print("2. Run the following code:")
    
    code_example = '''
service = JobPortalService()
jobs_with_managers = service.fetch_hiring_managers_for_jobs(sample_jobs)
print(jobs_with_managers[['title', 'company', 'hiring_managers_count', 'hiring_managers_names']])
'''
    
    print(code_example)


if __name__ == "__main__":
    print("🎯 LinkedIn Hiring Manager Extraction Examples")
    print("=" * 60)
    
    # Run examples
    try:
        # Uncomment the example you want to run:
        
        # Full search and extraction demo
        # example_search_and_extract()
        
        # Single job URL demo
        example_single_job()
        
        # Existing data demo
        example_with_existing_data()
        
        print("\n" + "=" * 60)
        print("✅ Examples completed!")
        print("\nTo run the full demo:")
        print("1. Ensure ChromeDriver is installed")
        print("2. Uncomment example_search_and_extract() above")
        print("3. Run this script again")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("\nTroubleshooting:")
        print("- Check ChromeDriver installation")
        print("- Verify internet connection")
        print("- See HIRING_MANAGERS_GUIDE.md for detailed setup")
