import csv
import pandas as pd
import requests
import time
from jobspy import scrape_jobs
from typing import List, Optional, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Import LinkedIn auth service
try:
    from .linkedin_auth_service import LinkedInAuthService, LinkedInCredentials
    LINKEDIN_AUTH_AVAILABLE = True
except ImportError:
    LINKEDIN_AUTH_AVAILABLE = False
    print("⚠️ LinkedIn auth service not available - using basic authentication")


class JobPortalService:
    """
    A service class for scraping jobs from various job portals using jobspy.
    """
    
    def __init__(self, linkedin_email: str = None, linkedin_password: str = None):
        """
        Initialize the JobPortalService.
        
        Args:
            linkedin_email: LinkedIn email for authenticated scraping (optional)
            linkedin_password: LinkedIn password for authenticated scraping (optional)
        """
        self.supported_sites = ["linkedin", "glassdoor", "bayt", "naukri", "bdjobs"]
        self.linkedin_email = linkedin_email
        self.linkedin_password = linkedin_password
        self.linkedin_auth_service = None
        self.linkedin_credentials = None
        
        # Setup LinkedIn authentication if credentials provided
        if linkedin_email and linkedin_password and LINKEDIN_AUTH_AVAILABLE:
            self.linkedin_credentials = LinkedInCredentials(
                email=linkedin_email,
                password=linkedin_password
            )
            print("✅ LinkedIn credentials configured for authenticated scraping")
        elif linkedin_email and linkedin_password:
            print("⚠️ LinkedIn credentials provided but auth service not available")
        else:
            print("💡 No LinkedIn credentials provided - using non-authenticated scraping")

    def scrape_jobs(
        self,
        site_name: List[str] = None,
        search_term: str = "Gen Ai",
        google_search_term: str = "Gen Ai jobs near India since yesterday",
        location: str = "India",
        results_wanted: int = 20,
        hours_old: int = 72,
        country_indeed: str = 'USA',
        linkedin_fetch_description: bool = True,
        proxies: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Scrape jobs from specified job portals.
        
        Args:
            site_name: List of job sites to scrape from. Defaults to ["linkedin"]
            search_term: Job search term
            google_search_term: Google search term for job searches
            location: Location to search for jobs
            results_wanted: Number of job results wanted
            hours_old: Maximum age of job postings in hours
            country_indeed: Country for Indeed searches
            linkedin_fetch_description: Whether to fetch full job descriptions from LinkedIn
            proxies: Optional list of proxy servers to use
            
        Returns:
            pd.DataFrame: DataFrame containing job data with columns:
            id, site, job_url, job_url_direct, title, company, location, date_posted,
            job_type, salary_source, interval, min_amount, max_amount, currency,
            is_remote, job_level, job_function, listing_type, emails, description,
            company_industry, company_url, company_logo, company_url_direct,
            company_addresses, company_num_employees, company_revenue,
            company_description, skills, experience_range, company_rating,
            company_reviews_count, vacancy_count, work_from_home_type
        """
        
        if site_name is None:
            site_name = ["linkedin"]
        
        # Validate site names
        invalid_sites = [site for site in site_name if site not in self.supported_sites]
        if invalid_sites:
            print(f"Warning: Unsupported sites: {invalid_sites}")
            site_name = [site for site in site_name if site in self.supported_sites]
        
        if not site_name:
            raise ValueError("No valid sites specified for scraping")
        
        try:
            # Prepare scraping parameters
            scrape_params = {
                "site_name": site_name,
                "search_term": search_term,
                "google_search_term": google_search_term,
                "location": location,
                "results_wanted": results_wanted,
                "hours_old": hours_old,
                "country_indeed": country_indeed,
                "linkedin_fetch_description": linkedin_fetch_description
            }
            
            # Add proxies if provided
            if proxies:
                scrape_params["proxies"] = proxies
            
            # Scrape jobs
            jobs_df = scrape_jobs(**scrape_params)
            
            print(f"Found {len(jobs_df)} jobs")
            
            return jobs_df
            
        except Exception as e:
            print(f"Error occurred while scraping jobs: {str(e)}")
            raise
    
    def save_jobs_to_csv(self, jobs_df: pd.DataFrame, filename: str = "jobs.csv") -> None:
        """
        Save jobs DataFrame to CSV file.
        
        Args:
            jobs_df: DataFrame containing job data
            filename: Name of the CSV file to save
        """
        try:
            jobs_df.to_csv(filename, index=False)
            print(f"Jobs saved to {filename}")
        except Exception as e:
            print(f"Error saving jobs to CSV: {str(e)}")
            raise
    
    def filter_jobs(
        self,
        jobs_df: pd.DataFrame,
        min_salary: Optional[float] = None,
        max_salary: Optional[float] = None,
        job_type: Optional[str] = None,
        is_remote: Optional[bool] = None,
        company: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Filter jobs based on specified criteria.
        
        Args:
            jobs_df: DataFrame containing job data
            min_salary: Minimum salary filter
            max_salary: Maximum salary filter
            job_type: Job type filter
            is_remote: Remote work filter
            company: Company name filter
            
        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        filtered_df = jobs_df.copy()
        
        if min_salary is not None:
            filtered_df = filtered_df[filtered_df['min_amount'] >= min_salary]
        
        if max_salary is not None:
            filtered_df = filtered_df[filtered_df['max_amount'] <= max_salary]
        
        if job_type is not None:
            filtered_df = filtered_df[filtered_df['job_type'].str.contains(job_type, case=False, na=False)]
        
        if is_remote is not None:
            filtered_df = filtered_df[filtered_df['is_remote'] == is_remote]
        
        if company is not None:
            filtered_df = filtered_df[filtered_df['company'].str.contains(company, case=False, na=False)]
        
        return filtered_df
    
    def get_job_summary(self, jobs_df: pd.DataFrame) -> dict:
        """
        Get summary statistics of the scraped jobs.
        
        Args:
            jobs_df: DataFrame containing job data
            
        Returns:
            dict: Summary statistics
        """
        summary = {
            "total_jobs": len(jobs_df),
            "unique_companies": jobs_df['company'].nunique() if 'company' in jobs_df.columns else 0,
            "sites_scraped": jobs_df['site'].unique().tolist() if 'site' in jobs_df.columns else [],
            "remote_jobs": jobs_df['is_remote'].sum() if 'is_remote' in jobs_df.columns else 0,
            "avg_salary_min": jobs_df['min_amount'].mean() if 'min_amount' in jobs_df.columns else None,
            "avg_salary_max": jobs_df['max_amount'].mean() if 'max_amount' in jobs_df.columns else None,
            "job_types": jobs_df['job_type'].value_counts().to_dict() if 'job_type' in jobs_df.columns else {}
        }
        
        return summary
    
    def setup_linkedin_auth(self, force_login: bool = False) -> bool:
        """
        Setup LinkedIn authentication session.
        
        Args:
            force_login: Force new login even if session exists
            
        Returns:
            bool: True if authentication successful
        """
        if not self.linkedin_credentials or not LINKEDIN_AUTH_AVAILABLE:
            print("❌ LinkedIn credentials not configured or auth service unavailable")
            return False
        
        try:
            if not self.linkedin_auth_service:
                self.linkedin_auth_service = LinkedInAuthService(headless=True)
            
            success = self.linkedin_auth_service.login(self.linkedin_credentials, force_login=force_login)
            
            if success:
                print("✅ LinkedIn authentication successful")
                return True
            else:
                print("❌ LinkedIn authentication failed")
                return False
                
        except Exception as e:
            print(f"❌ LinkedIn authentication error: {str(e)}")
            return False
    
    def start_linkedin_interactive_auth(self) -> bool:
        """
        Start interactive LinkedIn authentication - opens browser for user to complete login.
        
        Returns:
            bool: True if browser opened successfully for authentication
        """
        if not self.linkedin_credentials or not LINKEDIN_AUTH_AVAILABLE:
            print("❌ LinkedIn credentials not configured or auth service unavailable")
            return False
        
        try:
            if not self.linkedin_auth_service:
                self.linkedin_auth_service = LinkedInAuthService(headless=False)
            
            success = self.linkedin_auth_service.start_interactive_login(self.linkedin_credentials)
            
            if success:
                print("🌐 Browser opened for LinkedIn authentication")
                return True
            else:
                print("❌ Failed to open browser for authentication")
                return False
                
        except Exception as e:
            print(f"❌ Error starting interactive authentication: {str(e)}")
            return False
    
    def confirm_linkedin_auth_complete(self) -> bool:
        """
        Confirm that user has completed LinkedIn authentication in the browser.
        
        Returns:
            bool: True if authentication confirmed successful
        """
        if not self.linkedin_auth_service:
            print("❌ No LinkedIn authentication session found")
            return False
        
        try:
            success = self.linkedin_auth_service.confirm_authentication_complete()
            return success
                
        except Exception as e:
            print(f"❌ Error confirming authentication: {str(e)}")
            return False
    
    def close_linkedin_auth(self):
        """Close LinkedIn authentication session."""
        if self.linkedin_auth_service:
            self.linkedin_auth_service.close()
            self.linkedin_auth_service = None
            print("🔒 LinkedIn session closed")
    
    def setup_selenium_driver(self, headless: bool = True) -> webdriver.Chrome:
        """
        Setup Chrome driver for web scraping.
        
        Args:
            headless: Whether to run in headless mode
            
        Returns:
            webdriver.Chrome: Configured Chrome driver
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        return driver
    
    def fetch_hiring_manager_details(self, job_url: str, max_retries: int = 1) -> Dict[str, any]:
        """
        Fetch hiring manager details from LinkedIn job page.
        
        Args:
            job_url: LinkedIn job URL
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict containing hiring manager information:
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
                'error': str (if success is False)
            }
        """
        if not job_url or 'linkedin.com' not in job_url:
            return {
                'success': False,
                'hiring_managers': [],
                'error': 'Invalid LinkedIn job URL'
            }
        
        # Try to use authenticated LinkedIn session first
        if self.linkedin_credentials and LINKEDIN_AUTH_AVAILABLE:
            try:
                return self._fetch_with_linkedin_auth(job_url, max_retries)
            except Exception as e:
                print(f"⚠️ LinkedIn auth method failed: {str(e)}")
                print("🔄 Falling back to non-authenticated method...")
        
        # Fallback to non-authenticated method
        return self._fetch_without_auth(job_url, max_retries)
    
    def _fetch_with_linkedin_auth(self, job_url: str, max_retries: int) -> Dict[str, any]:
        """Fetch hiring managers using authenticated LinkedIn session."""
        
        # Setup LinkedIn authentication if not already done
        if not self.linkedin_auth_service or not self.linkedin_auth_service.is_authenticated:
            if not self.setup_linkedin_auth():
                raise Exception("Failed to setup LinkedIn authentication")
        
        driver = self.linkedin_auth_service.get_authenticated_driver()
        if not driver:
            raise Exception("No authenticated driver available")
        
        for attempt in range(max_retries):
            try:
                print(f"🔍 Fetching hiring manager details (authenticated): {job_url}")
                print(f"Attempt {attempt + 1}/{max_retries}")
                
                # Navigate to job page using authenticated session
                if not self.linkedin_auth_service.navigate_to_job(job_url):
                    if attempt == max_retries - 1:
                        return {
                            'success': False,
                            'hiring_managers': [],
                            'error': 'Failed to navigate to job page'
                        }
                    continue
                
                # Extract hiring manager information
                hiring_managers = self._extract_hiring_manager_info_from_driver(driver)
                
                return {
                    'success': True,
                    'hiring_managers': hiring_managers,
                    'total_found': len(hiring_managers),
                    'method': 'authenticated'
                }
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'hiring_managers': [],
                        'error': f"Failed after {max_retries} attempts: {str(e)}"
                    }
                time.sleep(2)  # Wait before retry
        
        return {
            'success': False,
            'hiring_managers': [],
            'error': 'Max retries exceeded'
        }
    
    def _fetch_without_auth(self, job_url: str, max_retries: int) -> Dict[str, any]:
        """Fetch hiring managers using non-authenticated session (fallback)."""
        
        driver = None
        for attempt in range(max_retries):
            try:
                print(f"🔍 Fetching hiring manager details (non-authenticated): {job_url}")
                print(f"Attempt {attempt + 1}/{max_retries}")
                
                # Setup driver
                driver = self.setup_selenium_driver(headless=True)
                driver.implicitly_wait(10)
                
                # Navigate to job page
                driver.get(job_url)
                time.sleep(3)
                
                # Wait for page to load
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Extract hiring manager information
                hiring_managers = self._extract_hiring_manager_info_from_driver(driver)
                
                return {
                    'success': True,
                    'hiring_managers': hiring_managers,
                    'total_found': len(hiring_managers),
                    'method': 'non-authenticated'
                }
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'hiring_managers': [],
                        'error': f"Failed after {max_retries} attempts: {str(e)}"
                    }
                time.sleep(2)  # Wait before retry
                
            finally:
                if driver:
                    driver.quit()
        
        return {
            'success': False,
            'hiring_managers': [],
            'error': 'Max retries exceeded'
        }
    
    def _extract_hiring_manager_info_from_driver(self, driver) -> List[Dict[str, str]]:
        """Extract hiring manager information from the current page using provided driver."""
        hiring_managers = []
        
        try:
            # Look for "Meet the hiring team" section
            hiring_team_selectors = [
                "//section[contains(.//h2, 'Meet the hiring team')]",
                "//div[contains(.//h3, 'Meet the hiring team')]",
                "//div[contains(.//span, 'Meet the hiring team')]",
                "//section[contains(@class, 'hiring-team')]",
                "//div[contains(@class, 'hiring-team')]"
            ]
            
            hiring_team_section = None
            for selector in hiring_team_selectors:
                try:
                    hiring_team_section = driver.find_element(By.XPATH, selector)
                    print("✅ Found 'Meet the hiring team' section")
                    break
                except:
                    continue
            
            if not hiring_team_section:
                # Try alternative approach - look for any hiring manager cards
                print("🔍 Searching for hiring manager cards...")
                hiring_manager_selectors = [
                    "//div[contains(@class, 'hirer-card')]",
                    "//div[contains(@class, 'hiring-manager')]",
                    "//div[contains(@class, 'recruiter-card')]",
                    "//li[contains(@class, 'hirer-card')]"
                ]
                
                for selector in hiring_manager_selectors:
                    try:
                        hiring_team_section = driver.find_element(By.XPATH, f"//section[{selector}]")
                        break
                    except:
                        continue
            
            if hiring_team_section:
                # Extract hiring manager information
                hiring_managers = self._extract_hiring_manager_info(hiring_team_section, driver)
            else:
                print("⚠️ No hiring team section found")
            
        except Exception as e:
            print(f"❌ Error extracting hiring manager info: {str(e)}")
        
        return hiring_managers
    
    def _extract_hiring_manager_info(self, section_element, driver) -> List[Dict[str, str]]:
        """
        Extract hiring manager information from the hiring team section.
        
        Args:
            section_element: WebElement containing the hiring team section
            driver: Selenium WebDriver instance
            
        Returns:
            List of dictionaries containing hiring manager information
        """
        hiring_managers = []
        
        try:
            # Look for individual hiring manager cards
            manager_card_selectors = [
                ".//div[contains(@class, 'hirer-card')]",
                ".//li[contains(@class, 'hirer-card')]",
                ".//div[contains(@class, 'hiring-manager')]",
                ".//div[contains(@class, 'recruiter-card')]",
                ".//div[contains(@data-test-id, 'hirer')]"
            ]
            
            manager_cards = []
            for selector in manager_card_selectors:
                try:
                    cards = section_element.find_elements(By.XPATH, selector)
                    if cards:
                        manager_cards.extend(cards)
                        break
                except:
                    continue
            
            print(f"🔍 Found {len(manager_cards)} potential hiring manager cards")
            
            for card in manager_cards:
                try:
                    manager_info = {}
                    
                    # Extract name
                    name_selectors = [
                        ".//span[contains(@class, 'hirer-card__hirer-information-name')]",
                        ".//a[contains(@class, 'hirer-card__hirer-information-name')]",
                        ".//h3",
                        ".//h4",
                        ".//span[contains(@aria-label, 'name')]"
                    ]
                    
                    for name_selector in name_selectors:
                        try:
                            name_element = card.find_element(By.XPATH, name_selector)
                            manager_info['name'] = name_element.text.strip()
                            break
                        except:
                            continue
                    
                    # Extract title/position
                    title_selectors = [
                        ".//span[contains(@class, 'hirer-card__hirer-information-position')]",
                        ".//div[contains(@class, 'hirer-card__hirer-information-position')]",
                        ".//p[contains(@class, 'title')]",
                        ".//span[contains(@class, 'job-title')]"
                    ]
                    
                    for title_selector in title_selectors:
                        try:
                            title_element = card.find_element(By.XPATH, title_selector)
                            manager_info['title'] = title_element.text.strip()
                            break
                        except:
                            continue
                    
                    # Extract profile URL
                    profile_selectors = [
                        ".//a[contains(@href, '/in/')]",
                        ".//a[contains(@class, 'hirer-card__hirer-information-name')]",
                        ".//a[contains(@href, 'linkedin.com')]"
                    ]
                    
                    for profile_selector in profile_selectors:
                        try:
                            profile_element = card.find_element(By.XPATH, profile_selector)
                            profile_url = profile_element.get_attribute('href')
                            if profile_url and '/in/' in profile_url:
                                manager_info['profile_url'] = profile_url
                                break
                        except:
                            continue
                    
                    # Extract image URL
                    image_selectors = [
                        ".//img[contains(@class, 'hirer-card__image')]",
                        ".//img[contains(@alt, 'headshot')]",
                        ".//img"
                    ]
                    
                    for image_selector in image_selectors:
                        try:
                            image_element = card.find_element(By.XPATH, image_selector)
                            image_url = image_element.get_attribute('src')
                            if image_url:
                                manager_info['image_url'] = image_url
                                break
                        except:
                            continue
                    
                    # Extract company (fallback from page title or job details)
                    try:
                        company_element = driver.find_element(By.XPATH, "//h1[contains(@class, 'job-title')]//a | //span[contains(@class, 'company-name')]")
                        manager_info['company'] = company_element.text.strip()
                    except:
                        manager_info['company'] = "Unknown"
                    
                    # Only add if we have at least a name
                    if manager_info.get('name'):
                        hiring_managers.append(manager_info)
                        print(f"✅ Found hiring manager: {manager_info.get('name', 'Unknown')} - {manager_info.get('title', 'Unknown title')}")
                    
                except Exception as e:
                    print(f"⚠️ Error extracting manager info: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"❌ Error in _extract_hiring_manager_info: {str(e)}")
        
        return hiring_managers
    
    def fetch_hiring_managers_for_jobs(self, jobs_df: pd.DataFrame, job_urls_column: str = 'job_url') -> pd.DataFrame:
        """
        Fetch hiring manager details for all LinkedIn jobs in the DataFrame.
        
        Args:
            jobs_df: DataFrame containing job data
            job_urls_column: Column name containing job URLs
            
        Returns:
            pd.DataFrame: Original DataFrame with additional hiring manager columns
        """
        if job_urls_column not in jobs_df.columns:
            print(f"❌ Column '{job_urls_column}' not found in DataFrame")
            return jobs_df
        
        # Add new columns for hiring manager data
        jobs_df['hiring_managers_count'] = 0
        jobs_df['hiring_managers_names'] = ''
        jobs_df['hiring_managers_titles'] = ''
        jobs_df['hiring_managers_profiles'] = ''
        jobs_df['hiring_manager_fetch_success'] = False
        jobs_df['hiring_manager_method'] = ''
        
        linkedin_jobs = jobs_df[jobs_df[job_urls_column].str.contains('linkedin.com', na=False)]
        print(f"🔍 Found {len(linkedin_jobs)} LinkedIn jobs to process")
        
        # Setup LinkedIn authentication for batch processing
        auth_setup_success = False
        if self.linkedin_credentials and LINKEDIN_AUTH_AVAILABLE:
            print("🔐 Setting up LinkedIn authentication for batch processing...")
            auth_setup_success = self.setup_linkedin_auth()
            if auth_setup_success:
                print("✅ LinkedIn authentication ready for batch processing")
            else:
                print("⚠️ LinkedIn authentication failed, using non-authenticated method")
        
        try:
            for index, row in linkedin_jobs.iterrows():
                job_url = row[job_urls_column]
                print(f"\n📋 Processing job {index + 1}/{len(linkedin_jobs)}: {row.get('title', 'Unknown Title')}")
                
                # Fetch hiring manager details
                result = self.fetch_hiring_manager_details(job_url)
                
                if result['success'] and result['hiring_managers']:
                    managers = result['hiring_managers']
                    
                    # Update DataFrame with hiring manager information
                    jobs_df.loc[index, 'hiring_managers_count'] = len(managers)
                    jobs_df.loc[index, 'hiring_managers_names'] = ' | '.join([m.get('name', '') for m in managers])
                    jobs_df.loc[index, 'hiring_managers_titles'] = ' | '.join([m.get('title', '') for m in managers])
                    jobs_df.loc[index, 'hiring_managers_profiles'] = ' | '.join([m.get('profile_url', '') for m in managers])
                    jobs_df.loc[index, 'hiring_manager_fetch_success'] = True
                    jobs_df.loc[index, 'hiring_manager_method'] = result.get('method', 'unknown')
                    
                    print(f"✅ Found {len(managers)} hiring manager(s)")
                    for manager in managers:
                        print(f"   • {manager.get('name', 'Unknown')} - {manager.get('title', 'Unknown title')}")
                else:
                    print(f"❌ No hiring managers found: {result.get('error', 'Unknown error')}")
                    jobs_df.loc[index, 'hiring_manager_fetch_success'] = False
                    jobs_df.loc[index, 'hiring_manager_method'] = result.get('method', 'unknown')
                
                # Add delay to avoid being rate-limited
                time.sleep(2)
        
        finally:
            # Clean up LinkedIn authentication session
            if auth_setup_success:
                self.close_linkedin_auth()
        
        success_count = jobs_df['hiring_manager_fetch_success'].sum()
        auth_method_count = (jobs_df['hiring_manager_method'] == 'authenticated').sum()
        
        print(f"\n📊 Summary: Successfully fetched hiring managers for {success_count}/{len(linkedin_jobs)} LinkedIn jobs")
        if auth_method_count > 0:
            print(f"🔐 {auth_method_count} jobs processed with LinkedIn authentication")
        
        return jobs_df
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if hasattr(self, 'linkedin_auth_service') and self.linkedin_auth_service:
            self.close_linkedin_auth()
