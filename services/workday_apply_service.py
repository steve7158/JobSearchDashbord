# Workday Application Service - Enhanced for AutoApply Integration
# Prerequisites:
# pip install playwright
# playwright install

import time
import os
from typing import Dict, Any, Optional, Tuple
from playwright.sync_api import sync_playwright, Page
from dataclasses import dataclass
from .auto_apply_service import UserProfile


@dataclass
class WorkdayApplicationResult:
    """Result of Workday application process."""
    success: bool = False
    steps_completed: list = None
    errors: list = None
    final_url: str = ""
    
    def __post_init__(self):
        if self.steps_completed is None:
            self.steps_completed = []
        if self.errors is None:
            self.errors = []


class WorkdayApplyService:
    """
    Specialized service for applying to jobs on Workday portals.
    Integrates with the AutoApply system and UserProfile.
    """
    
    # Common Workday selectors
    SELECTORS = {
        # Navigation
        'next_button': 'button[data-automation-id="bottom-navigation-next-button"]',
        'continue_button': 'button[data-automation-id="continueButton"]',
        'submit_button': 'button[data-automation-id="bottom-navigation-next-button"]',
        
        # Initial application options
        'adventure_button': 'a[data-automation-id="adventureButton"]',
        'apply_manually': 'a[data-automation-id="applyManually"]',
        'create_account_link': 'button[data-automation-id="createAccountLink"]',
        'sign_in_link': 'button[data-automation-id="signInLink"]',
        
        # Account creation/login
        'email_input': 'input[data-automation-id="email"]',
        'password_input': 'input[data-automation-id="password"]',
        'verify_password_input': 'input[data-automation-id="verifyPassword"]',
        'create_account_checkbox': 'input[data-automation-id="createAccountCheckbox"]',
        'create_account_submit': 'button[data-automation-id="createAccountSubmitButton"]',
        'sign_in_submit': 'button[data-automation-id="signInSubmitButton"]',
        
        # Personal information
        'first_name': 'input[data-automation-id="legalNameSection_firstName"]',
        'last_name': 'input[data-automation-id="legalNameSection_lastName"]',
        'suffix_dropdown': 'button[data-automation-id="legalNameSection_social"]',
        
        # Address
        'address_line1': 'input[data-automation-id="addressSection_addressLine1"]',
        'city': 'input[data-automation-id="addressSection_city"]',
        'state_dropdown': 'button[data-automation-id="addressSection_countryRegion"]',
        'postal_code': 'input[data-automation-id="addressSection_postalCode"]',
        
        # Phone
        'phone_type_dropdown': 'button[data-automation-id="phone-device-type"]',
        'phone_number': 'input[data-automation-id="phone-number"]',
        
        # Education
        'add_education': 'div[data-automation-id="educationSection"] button[data-automation-id="Add"]',
        'school': 'input[data-automation-id="school"]',
        'field_of_study': 'div[data-automation-id="formField-field-of-study"] input',
        'gpa': 'input[data-automation-id="gpa"]',
        'degree_dropdown': 'button[data-automation-id="degree"]',
        'start_date': 'div[data-automation-id="formField-startDate"] input',
        'end_date': 'div[data-automation-id="formField-endDate"] input',
        
        # Resume and links
        'resume_upload': 'input[data-automation-id="file-upload-input-ref"]',
        'linkedin_input': 'input[data-automation-id="linkedinQuestion"]',
        'website_add': 'div[data-automation-id="websiteSection"] button[data-automation-id="Add"]',
        'website_add_another': 'div[data-automation-id="websiteSection"] button[data-automation-id="Add Another"]',
        
        # Voluntary disclosures
        'gender_dropdown': 'button[data-automation-id="gender"]',
        'hispanic_dropdown': 'button[data-automation-id="hispanicOrLatino"]',
        'ethnicity_dropdown': 'button[data-automation-id="ethnicityDropdown"]',
        'veteran_dropdown': 'button[data-automation-id="veteranStatus"]',
        'agreement_checkbox': 'input[data-automation-id="agreementCheckbox"]',
        
        # Self-identification
        'self_id_name': 'input[data-automation-id="name"]',
        'date_icon': 'div[data-automation-id="dateIcon"]',
        'date_today': 'button[data-automation-id="datePickerSelectedToday"]',
        
        # Error handling
        'error_message': 'div[data-automation-id="errorMessage"]'
    }
    
    def __init__(self, user_profile: UserProfile, headless: bool = False, timeout: int = 30000):
        """
        Initialize the Workday apply service.
        
        Args:
            user_profile: User profile with all necessary information
            headless: Whether to run browser in headless mode
            timeout: Default timeout for page operations (ms)
        """
        self.user_profile = user_profile
        self.headless = headless
        self.timeout = timeout
        self.browser = None
        self.page = None
        self.playwright = None
    
    def setup_browser(self) -> bool:
        """Setup Playwright browser."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.page = self.browser.new_page()
            
            # Set default timeout
            self.page.set_default_timeout(self.timeout)
            
            print("✅ Playwright browser initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing browser: {str(e)}")
            return False
    
    def close_browser(self):
        """Close browser and cleanup."""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            print("🔒 Browser closed")
        except Exception as e:
            print(f"⚠️ Error closing browser: {str(e)}")
    
    def selector_exists(self, selector: str, timeout: int = 2000) -> bool:
        """Check if a selector exists on the page."""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False
    
    def safe_click(self, selector: str, description: str = "") -> bool:
        """Safely click an element with error handling."""
        try:
            if self.selector_exists(selector):
                self.page.click(selector)
                print(f"✅ Clicked: {description or selector}")
                time.sleep(1)  # Small delay for stability
                return True
            else:
                print(f"⚠️ Element not found: {description or selector}")
                return False
        except Exception as e:
            print(f"❌ Error clicking {description or selector}: {str(e)}")
            return False
    
    def safe_fill(self, selector: str, value: str, description: str = "") -> bool:
        """Safely fill an input field with error handling."""
        try:
            if not value:
                print(f"⚠️ No value provided for: {description or selector}")
                return False
                
            if self.selector_exists(selector):
                self.page.fill(selector, value)
                print(f"✅ Filled {description or selector}: {value}")
                return True
            else:
                print(f"⚠️ Input field not found: {description or selector}")
                return False
        except Exception as e:
            print(f"❌ Error filling {description or selector}: {str(e)}")
            return False
    
    def safe_select_dropdown(self, selector: str, value: str, description: str = "") -> bool:
        """Safely select from dropdown with typing."""
        try:
            if not value:
                print(f"⚠️ No value provided for dropdown: {description or selector}")
                return False
                
            if self.selector_exists(selector):
                self.page.click(selector)
                time.sleep(0.5)
                self.page.keyboard.type(value, delay=100)
                self.page.keyboard.press("Enter")
                print(f"✅ Selected from dropdown {description or selector}: {value}")
                return True
            else:
                print(f"⚠️ Dropdown not found: {description or selector}")
                return False
        except Exception as e:
            print(f"❌ Error selecting from dropdown {description or selector}: {str(e)}")
            return False
    
    def navigate_to_application(self, url: str) -> bool:
        """Navigate to the Workday application URL."""
        try:
            print(f"🌐 Navigating to: {url}")
            self.page.goto(url)
            time.sleep(3)  # Wait for page load
            return True
        except Exception as e:
            print(f"❌ Error navigating to URL: {str(e)}")
            return False
    
    def handle_initial_application_choice(self) -> bool:
        """Handle the initial application method selection."""
        try:
            print("🔧 Handling initial application choice...")
            
            # Try to find and click "Apply Manually" or similar
            manual_apply_selectors = [
                self.SELECTORS['apply_manually'],
                'a[data-automation-id="applyManually"]',
                'button[data-automation-id="applyManually"]',
                '//*[contains(text(), "Apply Manually")]'
            ]
            
            for selector in manual_apply_selectors:
                if self.safe_click(selector, "Apply Manually"):
                    time.sleep(2)
                    return True
            
            # If no manual apply found, try adventure button
            if self.safe_click(self.SELECTORS['adventure_button'], "Start Application"):
                time.sleep(2)
                # Then try manual apply
                if self.safe_click(self.SELECTORS['apply_manually'], "Apply Manually"):
                    return True
            
            print("⚠️ Could not find application method selection")
            return False
            
        except Exception as e:
            print(f"❌ Error in initial application choice: {str(e)}")
            return False
    
    def handle_account_creation_or_login(self) -> bool:
        """Handle account creation or login process."""
        try:
            print("👤 Handling account creation/login...")
            
            # Check if we need to create account or sign in
            if self.safe_click(self.SELECTORS['create_account_link'], "Create Account"):
                return self.create_account()
            elif self.selector_exists(self.SELECTORS['error_message']):
                print("Account exists, attempting sign in...")
                return self.sign_in()
            else:
                print("⚠️ Unclear account state, attempting to proceed...")
                return True
                
        except Exception as e:
            print(f"❌ Error in account handling: {str(e)}")
            return False
    
    def create_account(self) -> bool:
        """Create a new Workday account."""
        try:
            print("📝 Creating new account...")
            
            success = True
            success &= self.safe_fill(self.SELECTORS['email_input'], self.user_profile.email, "Email")
            
            # Use a default password if not provided
            password = getattr(self.user_profile, 'password', 'TempPassword123!')
            success &= self.safe_fill(self.SELECTORS['password_input'], password, "Password")
            success &= self.safe_fill(self.SELECTORS['verify_password_input'], password, "Verify Password")
            
            # Check agreement checkbox if exists
            if self.selector_exists(self.SELECTORS['create_account_checkbox']):
                self.safe_click(self.SELECTORS['create_account_checkbox'], "Agreement Checkbox")
            
            success &= self.safe_click(self.SELECTORS['create_account_submit'], "Create Account Submit")
            
            if success:
                print("✅ Account creation submitted")
                time.sleep(3)
            
            return success
            
        except Exception as e:
            print(f"❌ Error creating account: {str(e)}")
            return False
    
    def sign_in(self) -> bool:
        """Sign in to existing Workday account."""
        try:
            print("🔑 Signing in to existing account...")
            
            success = True
            success &= self.safe_click(self.SELECTORS['sign_in_link'], "Sign In Link")
            success &= self.safe_fill(self.SELECTORS['email_input'], self.user_profile.email, "Email")
            
            password = getattr(self.user_profile, 'password', 'TempPassword123!')
            success &= self.safe_fill(self.SELECTORS['password_input'], password, "Password")
            success &= self.safe_click(self.SELECTORS['sign_in_submit'], "Sign In Submit")
            
            if success:
                print("✅ Sign in submitted")
                time.sleep(3)
            
            return success
            
        except Exception as e:
            print(f"❌ Error signing in: {str(e)}")
            return False

    def fill_basic_info(self) -> bool:
        """Fill basic personal information."""
        try:
            print("📝 Filling basic personal information...")
            
            success = True
            
            # Handle previous worker question (usually "No")
            previous_worker_selector = 'div[data-automation-id="previousWorker"] input[id="2"]'
            if self.selector_exists(previous_worker_selector):
                self.safe_click(previous_worker_selector, "Previous Worker: No")
            
            # Name fields
            success &= self.safe_fill(self.SELECTORS['first_name'], self.user_profile.first_name, "First Name")
            success &= self.safe_fill(self.SELECTORS['last_name'], self.user_profile.last_name, "Last Name")
            
            # Suffix (optional)
            if hasattr(self.user_profile, 'suffix') and self.user_profile.suffix:
                self.safe_select_dropdown(self.SELECTORS['suffix_dropdown'], self.user_profile.suffix, "Suffix")
            
            # Address information
            success &= self.safe_fill(self.SELECTORS['address_line1'], self.user_profile.address, "Address")
            success &= self.safe_fill(self.SELECTORS['city'], self.user_profile.city, "City")
            
            # State/Region
            if self.user_profile.state:
                self.safe_select_dropdown(self.SELECTORS['state_dropdown'], self.user_profile.state, "State")
            
            success &= self.safe_fill(self.SELECTORS['postal_code'], self.user_profile.zip_code, "ZIP Code")
            
            # Phone information
            phone_type = getattr(self.user_profile, 'phone_type', 'Mobile')
            self.safe_select_dropdown(self.SELECTORS['phone_type_dropdown'], phone_type, "Phone Type")
            success &= self.safe_fill(self.SELECTORS['phone_number'], self.user_profile.phone, "Phone Number")
            
            # Click next
            success &= self.safe_click(self.SELECTORS['next_button'], "Next Button")
            
            if success:
                print("✅ Basic information filled successfully")
            
            return success
            
        except Exception as e:
            print(f"❌ Error filling basic info: {str(e)}")
            return False
    
    def fill_experience(self) -> bool:
        """Fill experience and education information."""
        try:
            print("🎓 Filling experience and education...")
            
            success = True
            
            # Education section
            if self.safe_click(self.SELECTORS['add_education'], "Add Education"):
                success &= self.safe_fill(self.SELECTORS['school'], self.user_profile.university, "School")
                success &= self.safe_fill(self.SELECTORS['field_of_study'], self.user_profile.degree, "Field of Study")
                
                # Press Enter twice for field of study (Workday requirement)
                self.page.keyboard.press("Enter")
                self.page.keyboard.press("Enter")
                
                # GPA (optional)
                if hasattr(self.user_profile, 'gpa') and self.user_profile.gpa:
                    self.safe_fill(self.SELECTORS['gpa'], self.user_profile.gpa, "GPA")
                
                # Degree type
                if self.user_profile.education_level:
                    self.safe_select_dropdown(self.SELECTORS['degree_dropdown'], self.user_profile.education_level, "Degree")
                
                # Dates (if available)
                if hasattr(self.user_profile, 'education_start_date'):
                    self.safe_fill(self.SELECTORS['start_date'], self.user_profile.education_start_date, "Start Date")
                if self.user_profile.graduation_year:
                    end_date = f"12/2023" if self.user_profile.graduation_year == "2023" else f"05/{self.user_profile.graduation_year}"
                    self.safe_fill(self.SELECTORS['end_date'], end_date, "End Date")
            
            # Resume upload
            resume_path = getattr(self.user_profile, 'resume_file_path', None)
            if resume_path and os.path.exists(resume_path):
                try:
                    self.page.set_input_files(self.SELECTORS['resume_upload'], resume_path)
                    print(f"✅ Resume uploaded: {resume_path}")
                except Exception as e:
                    print(f"⚠️ Could not upload resume: {str(e)}")
            else:
                print("⚠️ No resume file path provided or file not found")
            
            # LinkedIn and GitHub links
            if self.user_profile.linkedin_url:
                if self.safe_fill(self.SELECTORS['linkedin_input'], self.user_profile.linkedin_url, "LinkedIn"):
                    # If LinkedIn field exists, add GitHub as additional website
                    if self.user_profile.github_url:
                        self.safe_click(self.SELECTORS['website_add'], "Add Website")
                        github_input = 'div[data-automation-id="websitePanelSet-1"] input'
                        self.safe_fill(github_input, self.user_profile.github_url, "GitHub")
                else:
                    # LinkedIn field doesn't exist, add both as websites
                    self.safe_click(self.SELECTORS['website_add'], "Add Website")
                    linkedin_input = 'div[data-automation-id="websitePanelSet-1"] input'
                    self.safe_fill(linkedin_input, self.user_profile.linkedin_url, "LinkedIn")
                    
                    if self.user_profile.github_url:
                        self.safe_click(self.SELECTORS['website_add_another'], "Add Another Website")
                        github_input = 'div[data-automation-id="websitePanelSet-2"] input'
                        self.safe_fill(github_input, self.user_profile.github_url, "GitHub")
            
            # Click next
            success &= self.safe_click(self.SELECTORS['next_button'], "Next Button")
            
            if success:
                print("✅ Experience information filled successfully")
            
            return success
            
        except Exception as e:
            print(f"❌ Error filling experience: {str(e)}")
            return False
    
    def fill_voluntary_disclosures(self) -> bool:
        """Fill voluntary disclosure information."""
        try:
            print("📋 Filling voluntary disclosures...")
            
            success = True
            
            # Gender (optional)
            gender = getattr(self.user_profile, 'gender', 'Prefer not to answer')
            self.safe_select_dropdown(self.SELECTORS['gender_dropdown'], gender, "Gender")
            
            # Hispanic/Latino status (optional)
            hispanic_status = getattr(self.user_profile, 'hispanic_or_latino', 'Prefer not to answer')
            if self.selector_exists(self.SELECTORS['hispanic_dropdown']):
                self.safe_select_dropdown(self.SELECTORS['hispanic_dropdown'], hispanic_status, "Hispanic/Latino")
            
            # Ethnicity (optional)
            ethnicity = getattr(self.user_profile, 'ethnicity', 'Prefer not to answer')
            self.safe_select_dropdown(self.SELECTORS['ethnicity_dropdown'], ethnicity, "Ethnicity")
            
            # Veteran status (optional)
            veteran_status = getattr(self.user_profile, 'veteran_status', 'I am not a protected veteran')
            self.safe_select_dropdown(self.SELECTORS['veteran_dropdown'], veteran_status, "Veteran Status")
            
            # Agreement checkbox
            success &= self.safe_click(self.SELECTORS['agreement_checkbox'], "Agreement Checkbox")
            
            # Click next
            success &= self.safe_click(self.SELECTORS['next_button'], "Next Button")
            
            if success:
                print("✅ Voluntary disclosures filled successfully")
            
            return success
            
        except Exception as e:
            print(f"❌ Error filling voluntary disclosures: {str(e)}")
            return False
    
    def fill_self_identify(self) -> bool:
        """Fill self-identification/disability information."""
        try:
            print("♿ Filling self-identification information...")
            
            success = True
            
            # Name field
            success &= self.safe_fill(self.SELECTORS['self_id_name'], self.user_profile.full_name, "Full Name")
            
            # Date field (usually today's date)
            if self.safe_click(self.SELECTORS['date_icon'], "Date Icon"):
                self.safe_click(self.SELECTORS['date_today'], "Today's Date")
            
            # Disability status (usually "I do not wish to answer")
            disability_checkbox = 'input[id="64cbff5f364f10000ae7a421cf210000"]'
            if self.selector_exists(disability_checkbox):
                self.safe_click(disability_checkbox, "Disability Status")
            
            # Click next/submit
            success &= self.safe_click(self.SELECTORS['next_button'], "Next/Submit Button")
            
            if success:
                print("✅ Self-identification filled successfully")
            
            return success
            
        except Exception as e:
            print(f"❌ Error filling self-identification: {str(e)}")
            return False
    
    def wait_for_page(self, page_selector: str, description: str, timeout: int = 10000) -> bool:
        """Wait for a specific page to load."""
        try:
            print(f"⏳ Waiting for {description}...")
            self.page.wait_for_selector(page_selector, timeout=timeout)
            print(f"✅ {description} loaded")
            return True
        except Exception as e:
            print(f"⚠️ Timeout waiting for {description}: {str(e)}")
            return False
    
    def apply_to_job(self, url: str) -> WorkdayApplicationResult:
        """
        Complete end-to-end Workday job application process.
        
        Args:
            url: Workday job application URL
            
        Returns:
            WorkdayApplicationResult with success status and details
        """
        result = WorkdayApplicationResult()
        
        try:
            # Setup browser
            if not self.setup_browser():
                result.errors.append("Failed to setup browser")
                return result
            
            # Step 1: Navigate to application
            if not self.navigate_to_application(url):
                result.errors.append("Failed to navigate to application URL")
                return result
            
            result.steps_completed.append("Navigated to application URL")
            
            # Step 2: Handle initial application choice
            if not self.handle_initial_application_choice():
                result.errors.append("Failed to handle initial application choice")
                return result
            
            result.steps_completed.append("Selected application method")
            
            # Step 3: Handle account creation/login
            if not self.handle_account_creation_or_login():
                result.errors.append("Failed to handle account creation/login")
                return result
            
            result.steps_completed.append("Handled account creation/login")
            
            # Step 4: Fill basic information
            if not self.fill_basic_info():
                result.errors.append("Failed to fill basic information")
                return result
            
            result.steps_completed.append("Filled basic information")
            
            # Step 5: Wait for and fill experience page
            if self.wait_for_page('div[data-automation-id="myExperiencePage"]', "Experience Page"):
                if not self.fill_experience():
                    result.errors.append("Failed to fill experience information")
                    return result
                result.steps_completed.append("Filled experience information")
            
            # Step 6: Wait for and fill voluntary disclosures
            if self.wait_for_page('div[data-automation-id="voluntaryDisclosuresPage"]', "Voluntary Disclosures Page"):
                if not self.fill_voluntary_disclosures():
                    result.errors.append("Failed to fill voluntary disclosures")
                    return result
                result.steps_completed.append("Filled voluntary disclosures")
            
            # Step 7: Wait for and fill self-identification
            if self.wait_for_page('div[data-automation-id="selfIdentificationPage"]', "Self-Identification Page"):
                if not self.fill_self_identify():
                    result.errors.append("Failed to fill self-identification")
                    return result
                result.steps_completed.append("Filled self-identification")
            
            # Success!
            result.success = True
            result.final_url = self.page.url
            print("🎉 Workday application completed successfully!")
            
        except Exception as e:
            error_msg = f"Unexpected error during application: {str(e)}"
            result.errors.append(error_msg)
            print(f"❌ {error_msg}")
        
        finally:
            # Keep browser open for review if not headless
            if not self.headless:
                print("\n🔍 REVIEW MODE - Browser left open for review")
                print("Close the browser window when you're done reviewing.")
                input("Press Enter to close browser and continue...")
            
            self.close_browser()
        
        return result


# Integration function for AutoApply system
def apply_to_workday_job(user_profile: UserProfile, url: str, headless: bool = False) -> Dict[str, Any]:
    """
    Integration function for applying to Workday jobs from the AutoApply system.
    
    Args:
        user_profile: UserProfile object with user information
        url: Workday job application URL
        headless: Whether to run in headless mode
        
    Returns:
        Dictionary with application results compatible with AutoApply system
    """
    service = WorkdayApplyService(user_profile, headless=headless)
    workday_result = service.apply_to_job(url)
    
    # Convert to AutoApply format
    return {
        "success": workday_result.success,
        "url": url,
        "final_url": workday_result.final_url,
        "steps_completed": workday_result.steps_completed,
        "errors": workday_result.errors,
        "service_used": "WorkdayApplyService",
        "fields_filled": len(workday_result.steps_completed),
        "fields_failed": len(workday_result.errors)
    }
