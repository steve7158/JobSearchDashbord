#!/usr/bin/env python3
"""
Example demonstrating LinkedIn authentication with hiring manager extraction.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from services.job_portal_service import JobPortalService
from services.linkedin_auth_service import LinkedInAuthService, LinkedInCredentials


def example_with_linkedin_auth():
    """Example using LinkedIn authentication for hiring manager extraction."""
    
    print("🔐 LinkedIn Authentication Example")
    print("=" * 50)
    
    # Get LinkedIn credentials from environment or input
    linkedin_email = os.getenv('LINKEDIN_EMAIL')
    linkedin_password = os.getenv('LINKEDIN_PASSWORD')
    
    if not linkedin_email or not linkedin_password:
        print("⚠️ LinkedIn credentials not found in environment variables")
        print("💡 Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in your .env file")
        print("\nFor manual input (not recommended for security):")
        
        # Uncomment below for manual input (not recommended for production)
        """
        linkedin_email = input("Enter LinkedIn email: ")
        linkedin_password = getpass.getpass("Enter LinkedIn password: ")
        """
        
        print("Example using placeholder credentials...")
        linkedin_email = "your.email@example.com"
        linkedin_password = "your_password"
    
    # Initialize JobPortalService with LinkedIn credentials
    print("🚀 Initializing JobPortalService with LinkedIn authentication...")
    
    try:
        service = JobPortalService(
            linkedin_email=linkedin_email,
            linkedin_password=linkedin_password
        )
        
        # Example 1: Search for jobs
        print("\n📋 Step 1: Searching for LinkedIn jobs...")
        jobs_df = service.scrape_jobs(
            site_name=["linkedin"],
            search_term="Software Engineer",
            location="San Francisco",
            results_wanted=3,  # Keep small for demo
            linkedin_fetch_description=True
        )
        
        print(f"✅ Found {len(jobs_df)} jobs")
        
        # Example 2: Fetch hiring managers with authentication
        print("\n🧑‍💼 Step 2: Fetching hiring managers (with LinkedIn auth)...")
        jobs_with_managers = service.fetch_hiring_managers_for_jobs(jobs_df)
        
        # Display results
        print("\n📊 Results:")
        for idx, job in jobs_with_managers.iterrows():
            print(f"\n{idx + 1}. {job.get('title', 'Unknown')}")
            print(f"   Company: {job.get('company', 'Unknown')}")
            
            if job.get('hiring_managers_count', 0) > 0:
                print(f"   👥 Hiring Managers: {int(job['hiring_managers_count'])}")
                print(f"   Method: {job.get('hiring_manager_method', 'unknown')}")
                
                managers = job.get('hiring_managers_names', '').split(' | ')
                for manager in managers[:2]:  # Show first 2
                    if manager.strip():
                        print(f"      • {manager}")
            else:
                print(f"   👥 No hiring managers found")
                print(f"   Method: {job.get('hiring_manager_method', 'unknown')}")
        
        # Save results
        output_file = "jobs_with_linkedin_auth.csv"
        jobs_with_managers.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check LinkedIn credentials")
        print("2. Ensure ChromeDriver is installed")
        print("3. Check network connection")


def example_manual_linkedin_auth():
    """Example using manual LinkedIn authentication."""
    
    print("\n🔧 Manual LinkedIn Authentication Example")
    print("=" * 50)
    
    # Example credentials (replace with real ones)
    email = "your.email@example.com"
    password = "your_password"
    
    print("💡 To test manual authentication:")
    print("1. Replace email and password with real LinkedIn credentials")
    print("2. Uncomment the code below")
    print("3. Run the script")
    
    # Uncomment below to test manual authentication
    """
    try:
        # Create LinkedIn auth service
        linkedin_auth = LinkedInAuthService(headless=False)  # Use headless=False to see the browser
        
        # Create credentials
        credentials = LinkedInCredentials(email=email, password=password)
        
        # Login
        if linkedin_auth.login(credentials):
            print("✅ LinkedIn login successful!")
            
            # Test navigation to a job
            test_job_url = "https://www.linkedin.com/jobs/view/1234567890/"  # Replace with real URL
            
            if linkedin_auth.navigate_to_job(test_job_url):
                print("✅ Successfully navigated to job page")
                
                # Get the authenticated driver for further processing
                driver = linkedin_auth.get_authenticated_driver()
                
                # Here you could extract hiring manager details
                print("🔍 Ready to extract hiring manager details...")
                
                # Keep browser open for inspection
                input("Press Enter to close browser...")
                
            else:
                print("❌ Failed to navigate to job page")
        else:
            print("❌ LinkedIn login failed")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        # Clean up
        if 'linkedin_auth' in locals():
            linkedin_auth.close()
    """


def setup_environment_example():
    """Example of setting up environment variables for LinkedIn auth."""
    
    print("\n📝 Environment Setup Example")
    print("=" * 35)
    
    print("To use LinkedIn authentication, add these to your .env file:")
    print()
    print("# LinkedIn credentials for hiring manager extraction")
    print("LINKEDIN_EMAIL=your.email@example.com")
    print("LINKEDIN_PASSWORD=your_secure_password")
    print()
    print("Then use JobPortalService like this:")
    
    code_example = '''
import os
from dotenv import load_dotenv
from services.job_portal_service import JobPortalService

load_dotenv()

service = JobPortalService(
    linkedin_email=os.getenv('LINKEDIN_EMAIL'),
    linkedin_password=os.getenv('LINKEDIN_PASSWORD')
)

# Now hiring manager extraction will use authenticated LinkedIn sessions
jobs_df = service.scrape_jobs(site_name=["linkedin"], search_term="AI Engineer")
jobs_with_managers = service.fetch_hiring_managers_for_jobs(jobs_df)
'''
    
    print(code_example)


if __name__ == "__main__":
    print("🎯 LinkedIn Authentication Examples")
    print("=" * 60)
    
    try:
        # Run examples
        example_with_linkedin_auth()
        example_manual_linkedin_auth()
        setup_environment_example()
        
        print("\n" + "=" * 60)
        print("✅ Examples completed!")
        print("\n🔐 Security Notes:")
        print("- Store credentials in .env file, not in code")
        print("- Never commit credentials to version control")
        print("- Use environment variables for production")
        print("- LinkedIn may require 2FA/email verification")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed: {str(e)}")
        print("\nTroubleshooting:")
        print("- Verify LinkedIn credentials")
        print("- Check ChromeDriver installation")
        print("- Review network connectivity")
        print("- See documentation for detailed setup")
