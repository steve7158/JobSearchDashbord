"""
LinkedIn Authentication Service
Handles LinkedIn login and maintains authenticated session for hiring manager scraping.
"""

import time
import json
import os
from typing import Dict, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dataclasses import dataclass


@dataclass
class LinkedInCredentials:
    """LinkedIn login credentials."""
    email: str
    password: str


class LinkedInAuthService:
    """
    Service for managing LinkedIn authentication and maintaining logged-in sessions.
    """
    
    def __init__(self, headless: bool = True, session_file: str = "linkedin_session.json"):
        """
        Initialize LinkedIn authentication service.
        
        Args:
            headless: Whether to run browser in headless mode
            session_file: File to store session cookies
        """
        self.headless = headless
        self.session_file = session_file
        self.driver = None
        self.is_authenticated = False
        self.credentials = None
        
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with LinkedIn-optimized settings."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Essential arguments for LinkedIn
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to avoid detection
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        chrome_options.add_argument(f"--user-agent={user_agent}")
        
        # Additional stealth options
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Faster loading
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            raise Exception(f"Failed to setup Chrome driver: {str(e)}")
    
    def save_session(self) -> None:
        """Save current session cookies to file."""
        if not self.driver:
            return
            
        try:
            cookies = self.driver.get_cookies()
            session_data = {
                'cookies': cookies,
                'current_url': self.driver.current_url,
                'timestamp': time.time()
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            print(f"✅ Session saved to {self.session_file}")
            
        except Exception as e:
            print(f"⚠️ Failed to save session: {str(e)}")
    
    def load_session(self) -> bool:
        """Load session cookies from file."""
        if not os.path.exists(self.session_file):
            print(f"📄 No session file found at {self.session_file}")
            return False
            
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is not too old (24 hours)
            if time.time() - session_data.get('timestamp', 0) > 86400:
                print("⏰ Session expired (older than 24 hours)")
                return False
            
            if not self.driver:
                self.driver = self.setup_driver()
            
            # Navigate to LinkedIn first
            self.driver.get("https://www.linkedin.com")
            time.sleep(2)
            
            # Load cookies
            for cookie in session_data['cookies']:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as cookie_error:
                    print(f"⚠️ Failed to add cookie: {cookie_error}")
                    continue
            
            # Navigate to a LinkedIn page to test authentication
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Check if we're logged in by looking for profile elements
            if self.is_logged_in():
                print("✅ Session restored successfully")
                self.is_authenticated = True
                return True
            else:
                print("❌ Session restoration failed")
                return False
                
        except Exception as e:
            print(f"❌ Failed to load session: {str(e)}")
            return False
    
    def is_logged_in(self) -> bool:
        """Check if currently logged into LinkedIn."""
        if not self.driver:
            return False
            
        try:
            # Look for elements that only appear when logged in
            login_indicators = [
                "//button[contains(@class, 'global-nav__me')]",  # Profile button
                "//div[contains(@class, 'feed-identity-module')]",  # Feed identity
                "//nav[contains(@class, 'global-nav')]//button",  # Navigation buttons
                "//a[contains(@href, '/me')]"  # Profile link
            ]
            
            for selector in login_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        return True
                except:
                    continue
            
            # Check if we're on login page (indicates not logged in)
            current_url = self.driver.current_url
            if any(path in current_url for path in ['/login', '/uas/login', '/checkpoint']):
                return False
                
            return False
            
        except Exception:
            return False
    
    def login(self, credentials: LinkedInCredentials, force_login: bool = False) -> bool:
        """
        Login to LinkedIn.
        
        Args:
            credentials: LinkedIn login credentials
            force_login: Force login even if session exists
            
        Returns:
            bool: True if login successful, False otherwise
        """
        self.credentials = credentials
        
        # Try to load existing session first (unless force_login is True)
        if not force_login and self.load_session():
            return True
        
        print("🔐 Starting LinkedIn login process...")
    
    def start_interactive_login(self, credentials: LinkedInCredentials) -> bool:
        """
        Start interactive LinkedIn login process - opens browser for user interaction.
        
        Args:
            credentials: LinkedIn login credentials
            
        Returns:
            bool: True if browser opened successfully, False otherwise
        """
        self.credentials = credentials
        
        print("🔐 Starting interactive LinkedIn login process...")
        print("🌐 Opening browser for manual authentication...")
        
        try:
            # Always use non-headless mode for interactive login
            if not self.driver:
                self.headless = False  # Force non-headless for interactive login
                self.driver = self.setup_driver()
            
            # Navigate to LinkedIn login page
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Wait for login form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Pre-fill credentials if available
            if credentials.email:
                print("📝 Pre-filling email...")
                username_field = self.driver.find_element(By.ID, "username")
                username_field.clear()
                username_field.send_keys(credentials.email)
            
            if credentials.password:
                print("📝 Pre-filling password...")
                password_field = self.driver.find_element(By.ID, "password")
                password_field.clear()
                password_field.send_keys(credentials.password)
            
            print("\n" + "="*70)
            print("🔐 LINKEDIN AUTHENTICATION REQUIRED")
            print("="*70)
            print("A browser window has opened with LinkedIn's login page.")
            print("Please:")
            print("1. Verify/complete your credentials")
            print("2. Click 'Sign in'")
            print("3. Complete any security challenges (email verification, etc.)")
            print("4. Wait until you see the LinkedIn feed/homepage")
            print("5. Click 'Authentication Complete' button in the dashboard")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting interactive login: {str(e)}")
            return False
        
        try:
            if not self.driver:
                self.driver = self.setup_driver()
            
            # Navigate to LinkedIn login page
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Wait for login form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Fill in credentials
            print("📝 Entering credentials...")
            
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.clear()
            username_field.send_keys(credentials.email)
            
            password_field.clear()
            password_field.send_keys(credentials.password)
            
            # Submit login form
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            print("⏳ Waiting for login to complete...")
            
            # Wait for login to complete (or for potential challenges)
            time.sleep(5)
            
            # Handle potential security challenges
            if self.handle_security_challenges():
                print("🔐 Security challenge handled")
            
            # Check if login was successful
            if self.is_logged_in():
                print("✅ LinkedIn login successful!")
                self.is_authenticated = True
                self.save_session()
                return True
            else:
                print("❌ LinkedIn login failed")
                current_url = self.driver.current_url
                print(f"Current URL: {current_url}")
                
                # Check for specific error messages
                self.check_login_errors()
                return False
                
        except TimeoutException:
            print("❌ Login timeout - page took too long to load")
            return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def handle_security_challenges(self) -> bool:
        """Handle LinkedIn security challenges like email verification."""
        try:
            current_url = self.driver.current_url
            
            # Check for email verification challenge
            if "/challenge/verify" in current_url or "checkpoint" in current_url:
                print("🔒 Security challenge detected")
                
                # Look for challenge description
                try:
                    challenge_text = self.driver.find_element(By.XPATH, "//div[contains(@class, 'challenge')]//p | //div[contains(@class, 'checkpoint')]//p")
                    print(f"Challenge: {challenge_text.text}")
                except:
                    print("Security challenge required - please check the browser")
                
                if not self.headless:
                    print("\n" + "="*60)
                    print("🔒 SECURITY CHALLENGE DETECTED")
                    print("="*60)
                    print("LinkedIn has presented a security challenge.")
                    print("Please complete the challenge in the browser window.")
                    print("This may include:")
                    print("- Email verification")
                    print("- Phone verification") 
                    print("- Captcha solving")
                    print("\nPress Enter after completing the challenge...")
                    input()
                    
                    # Check if challenge was completed
                    if self.is_logged_in():
                        return True
                else:
                    print("⚠️ Security challenge detected in headless mode")
                    print("💡 Run with headless=False to complete challenges manually")
                    return False
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error handling security challenges: {str(e)}")
            return False
    
    def check_login_errors(self) -> None:
        """Check for and report specific login errors."""
        try:
            # Look for error messages
            error_selectors = [
                "//div[contains(@class, 'alert')]",
                "//div[contains(@class, 'error')]",
                "//span[contains(@class, 'error')]",
                "//div[@role='alert']"
            ]
            
            for selector in error_selectors:
                try:
                    error_element = self.driver.find_element(By.XPATH, selector)
                    if error_element.is_displayed():
                        print(f"❌ Login error: {error_element.text}")
                        break
                except:
                    continue
                    
        except Exception:
            pass
    
    def confirm_authentication_complete(self) -> bool:
        """
        Confirm that user has completed authentication manually.
        Call this after user indicates they've completed login in the browser.
        
        Returns:
            bool: True if authentication confirmed successful, False otherwise
        """
        print("🔍 Checking authentication status...")
        
        try:
            if not self.driver:
                print("❌ No browser session found")
                return False
            
            # Check if user is now logged in
            if self.is_logged_in():
                print("✅ LinkedIn authentication confirmed!")
                self.is_authenticated = True
                self.save_session()
                return True
            else:
                print("❌ Authentication not complete - still on login page")
                current_url = self.driver.current_url
                print(f"Current URL: {current_url}")
                
                # Provide helpful feedback
                if "/login" in current_url:
                    print("💡 Please complete the login process in the browser")
                elif "/checkpoint" in current_url or "/challenge" in current_url:
                    print("💡 Please complete the security challenge in the browser")
                else:
                    print("💡 Please navigate to LinkedIn homepage after login")
                
                return False
                
        except Exception as e:
            print(f"❌ Error confirming authentication: {str(e)}")
            return False
    
    def get_authenticated_driver(self) -> Optional[webdriver.Chrome]:
        """
        Get the authenticated Chrome driver instance.
        
        Returns:
            webdriver.Chrome: Authenticated driver or None if not authenticated
        """
        if self.is_authenticated and self.driver:
            return self.driver
        return None
    
    def navigate_to_job(self, job_url: str) -> bool:
        """
        Navigate to a LinkedIn job page using the authenticated session.
        
        Args:
            job_url: LinkedIn job URL
            
        Returns:
            bool: True if navigation successful
        """
        if not self.is_authenticated or not self.driver:
            print("❌ Not authenticated. Please login first.")
            return False
        
        try:
            print(f"🌐 Navigating to job: {job_url}")
            self.driver.get(job_url)
            time.sleep(3)
            
            # Verify we're on the job page
            if "linkedin.com/jobs" in self.driver.current_url:
                print("✅ Successfully navigated to job page")
                return True
            else:
                print(f"⚠️ Unexpected URL after navigation: {self.driver.current_url}")
                return False
                
        except Exception as e:
            print(f"❌ Navigation error: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the browser and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                print("🔒 Browser closed")
            except Exception as e:
                print(f"⚠️ Error closing browser: {str(e)}")
            finally:
                self.driver = None
                self.is_authenticated = False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Helper functions for easy usage
def create_linkedin_session(email: str, password: str, headless: bool = True) -> LinkedInAuthService:
    """
    Create and authenticate a LinkedIn session.
    
    Args:
        email: LinkedIn email
        password: LinkedIn password
        headless: Whether to run in headless mode
        
    Returns:
        LinkedInAuthService: Authenticated service instance
    """
    credentials = LinkedInCredentials(email=email, password=password)
    service = LinkedInAuthService(headless=headless)
    
    if service.login(credentials):
        return service
    else:
        service.close()
        raise Exception("Failed to authenticate with LinkedIn")


# Example usage
if __name__ == "__main__":
    print("🔐 LinkedIn Authentication Service Demo")
    print("=" * 50)
    
    # Example credentials (replace with real ones)
    email = "your.email@example.com"
    password = "your_password"
    
    print("💡 To use this service:")
    print("1. Replace email and password with your LinkedIn credentials")
    print("2. Run the script")
    print("3. Complete any security challenges if prompted")
    
    # Uncomment below to test (after adding real credentials)
    """
    try:
        with create_linkedin_session(email, password, headless=False) as linkedin:
            # Test navigation to a job
            job_url = "https://www.linkedin.com/jobs/view/1234567890/"
            if linkedin.navigate_to_job(job_url):
                print("✅ Ready to scrape hiring managers!")
                
                # Your hiring manager scraping code would go here
                driver = linkedin.get_authenticated_driver()
                # ... scraping logic ...
                
            else:
                print("❌ Failed to navigate to job")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    """
