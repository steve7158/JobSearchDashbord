from services.job_portal_service import JobPortalService


# Example usage
if __name__ == "__main__":
    # Create an instance of JobPortalService
    job_service = JobPortalService()
    
    # Scrape jobs with the specified parameters
    jobs = job_service.scrape_jobs(
        site_name=["linkedin"],  # "glassdoor", "bayt", "naukri", "bdjobs"
        search_term="Gen Ai",
        google_search_term="Gen Ai jobs near India since yesterday",
        location="India",
        results_wanted=20,
        hours_old=72,
        country_indeed='USA',
        linkedin_fetch_description=True
    )
    
    # Display basic info about the scraped jobs
    print(f"Found {len(jobs)} jobs")
    if not jobs.empty:
        print("\nFirst few jobs:")
        print(jobs.head())
        
        # Get summary statistics
        summary = job_service.get_job_summary(jobs)
        print(f"\nJob Summary: {summary}")
        
        # Save to CSV
        job_service.save_jobs_to_csv(jobs, "scraped_jobs.csv")