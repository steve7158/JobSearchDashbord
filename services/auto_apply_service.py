import json
import time
import re
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import openai
import anthropic
import html2text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Workday service for specialized handling
try:
    from .workday_apply_service import apply_to_workday_job
    WORKDAY_SERVICE_AVAILABLE = True
except ImportError:
    WORKDAY_SERVICE_AVAILABLE = False
    print("⚠️ WorkdayApplyService not available - falling back to standard processing")


@dataclass
class UserProfile:
    """User profile containing all personal and professional information."""
    # Personal Information
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = ""
    
    # Professional Information
    current_title: str = ""
    years_of_experience: str = ""
    linkedin_url: str = ""
    portfolio_url: str = ""
    github_url: str = ""
    
    # Education
    education_level: str = ""
    university: str = ""
    degree: str = ""
    graduation_year: str = ""
    gpa: str = ""
    
    # Skills and Experience
    skills: List[str] = None
    resume_text: str = ""
    cover_letter_template: str = ""
    
    # Work Authorization
    work_authorized: bool = True
    visa_status: str = ""
    security_clearance: str = ""
    
    # Preferences
    salary_expectation: str = ""
    notice_period: str = ""
    willing_to_relocate: bool = False
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if not self.full_name and self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"


@dataclass
class FormField:
    """Represents a form field that needs to be filled."""
    element_id: str = ""
    element_name: str = ""
    element_type: str = ""
    label: str = ""
    placeholder: str = ""
    required: bool = False
    options: List[str] = None
    suggested_value: str = ""
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.options is None:
            self.options = []


class AutoApplyService:
    """
    Service for automatically filling job application forms using LLM analysis.
    """
    
    def __init__(self, user_profile: UserProfile, llm_provider: str = "openai", api_key: str = ""):
        """
        Initialize the AutoApplyService.
        
        Args:
            user_profile: User's personal and professional information
            llm_provider: LLM provider ("openai" or "anthropic")
            api_key: API key for the LLM provider (optional if set in .env)
        """
        self.user_profile = user_profile
        self.llm_provider = llm_provider.lower()
        
        # Get API key from parameter or environment variable
        if api_key:
            self.api_key = api_key
        else:
            if self.llm_provider == "openai":
                self.api_key = os.getenv('OPENAI_API_KEY', '')
            elif self.llm_provider == "anthropic":
                self.api_key = os.getenv('ANTHROPIC_API_KEY', '')
            else:
                self.api_key = ''
        
        if not self.api_key:
            raise ValueError(f"API key not provided. Set {self.llm_provider.upper()}_API_KEY environment variable or pass api_key parameter")
        
        # Initialize LLM client
        if self.llm_provider == "openai":
            openai.api_key = self.api_key
            self.llm_client = openai
        elif self.llm_provider == "anthropic":
            self.llm_client = anthropic.Anthropic(api_key=self.api_key)
        else:
            raise ValueError("Supported LLM providers: 'openai', 'anthropic'")
        
        # Initialize web driver (headless by default)
        self.driver = None
        self.wait = None
        
        # HTML to text converter
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
    
    def setup_driver(self, headless: bool = True, wait_time: int = 10):
        """Setup Chrome WebDriver."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, wait_time)
            print("✅ WebDriver initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing WebDriver: {str(e)}")
            print("💡 Please install ChromeDriver: https://chromedriver.chromium.org/")
            raise
    
    def close_driver(self):
        """Close the web driver."""
        if self.driver:
            self.driver.quit()
            print("🔒 WebDriver closed")
    
    def analyze_form_with_llm(self, html_content: str) -> List[FormField]:
        """
        Analyze HTML form content using LLM to identify fields and suggest values.
        
        Args:
            html_content: HTML content of the form
            
        Returns:
            List of FormField objects with suggested values
        """
        # Convert HTML to text for better LLM processing
        text_content = self.html_converter.handle(html_content)
        
        # Prepare user profile data for LLM
        profile_data = asdict(self.user_profile)
        
        prompt = f"""
        You are an expert at analyzing job application forms. Given the HTML form content below, identify all input fields and suggest appropriate values based on the user profile.

        User Profile:
        {json.dumps(profile_data, indent=2)}

        HTML Form Content:
        {text_content}

        Analyze the form and return a JSON array of form fields with the following structure:
        [
            {{
                "element_id": "field_id_or_name",
                "element_name": "field_name",
                "element_type": "input_type (text, email, select, etc.)",
                "label": "field_label_or_description",
                "placeholder": "placeholder_text",
                "required": true/false,
                "options": ["option1", "option2"] (for select fields),
                "suggested_value": "suggested_value_from_profile",
                "confidence": 0.0-1.0 (confidence in the suggestion)
            }}
        ]

        Rules:
        1. Map form fields to user profile data intelligently
        2. For name fields, use appropriate name parts
        3. For email, use the profile email
        4. For phone, format appropriately
        5. For address fields, split address data as needed
        6. For experience/skills, use relevant profile data
        7. For yes/no questions, suggest reasonable defaults
        8. Set confidence based on how certain you are about the mapping
        9. Only include fields that actually exist in the form
        10. For dropdown/select fields, suggest the best matching option

        Return only the JSON array, no additional text.
        """
        
        try:
            if self.llm_provider == "openai":
                response = self.llm_client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert form analysis assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                llm_response = response.choices[0].message.content
            
            elif self.llm_provider == "anthropic":
                response = self.llm_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                llm_response = response.content[0].text
            
            # Parse JSON response
            try:
                # Clean response to extract JSON
                json_start = llm_response.find('[')
                json_end = llm_response.rfind(']') + 1
                if json_start != -1 and json_end != 0:
                    json_str = llm_response[json_start:json_end]
                    form_fields_data = json.loads(json_str)
                    
                    # Convert to FormField objects
                    form_fields = []
                    for field_data in form_fields_data:
                        form_field = FormField(**field_data)
                        form_fields.append(form_field)
                    
                    return form_fields
                else:
                    print("❌ Could not find valid JSON in LLM response")
                    return []
            
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing LLM response JSON: {str(e)}")
                print(f"LLM Response: {llm_response[:500]}...")
                return []
        
        except Exception as e:
            print(f"❌ Error calling LLM API: {str(e)}")
            return []
    
    def detect_and_click_apply_button(self, url: str) -> Tuple[bool, str]:
        """
        Detect and click apply button on job listing pages.
        
        Args:
            url: URL of the job listing page
            
        Returns:
            Tuple of (success, current_url)
        """
        if not self.driver:
            raise ValueError("WebDriver not initialized. Call setup_driver() first.")
        
        try:
            print(f"🌐 Loading job listing page: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            # Common apply button selectors and text patterns
            apply_selectors = [
                # LinkedIn selectors
                "button[aria-label*='Apply']",
                "button[data-control-name*='apply']",
                "a[data-control-name*='apply']",
                ".jobs-apply-button",
                ".jobs-s-apply",
                
                # Indeed selectors
                "button[data-jk*='apply']",
                ".np[title*='Apply']",
                "a[title*='Apply']",
                
                # Glassdoor selectors
                "button[data-test='apply-btn']",
                ".apply-btn",
                
                # Generic selectors
                "button[class*='apply']",
                "a[class*='apply']",
                "input[value*='Apply']",
                "[role='button'][aria-label*='Apply']"
            ]
            
            # Text patterns to look for
            apply_text_patterns = [
                "Apply Now", "Apply", "Easy Apply", "Quick Apply",
                "Apply for this job", "Submit Application", "Apply Today"
            ]
            
            print("🔍 Looking for apply buttons...")
            
            # Try CSS selectors first
            for selector in apply_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            print(f"✅ Found apply button with selector: {selector}")
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1)
                            element.click()
                            time.sleep(3)
                            return True, self.driver.current_url
                except Exception as e:
                    continue
            
            # Try text-based search
            for text_pattern in apply_text_patterns:
                try:
                    # Look for buttons with specific text
                    xpath_queries = [
                        f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text_pattern.lower()}')]",
                        f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text_pattern.lower()}')]",
                        f"//input[@value[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text_pattern.lower()}')]]",
                        f"//*[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text_pattern.lower()}')]"
                    ]
                    
                    for xpath in xpath_queries:
                        try:
                            element = self.driver.find_element(By.XPATH, xpath)
                            if element.is_displayed() and element.is_enabled():
                                print(f"✅ Found apply button with text: {text_pattern}")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                time.sleep(1)
                                element.click()
                                time.sleep(3)
                                return True, self.driver.current_url
                        except Exception:
                            continue
                except Exception:
                    continue
            
            print("⚠️ No apply button found on this page")
            return False, self.driver.current_url
            
        except Exception as e:
            print(f"❌ Error detecting apply button: {str(e)}")
            return False, url

    def handle_workday_portal(self) -> bool:
        """
        Handle Workday-specific application flow.
        
        Returns:
            True if successfully handled, False otherwise
        """
        try:
            current_url = self.driver.current_url
            print(f"🏢 Detected potential Workday portal: {current_url}")
            
            # Check if we're on a Workday page
            if "workday" not in current_url.lower():
                # Check page content for Workday indicators
                page_source = self.driver.page_source.lower()
                workday_indicators = ["workday", "myworkdayjobs", "workdaycdn"]
                if not any(indicator in page_source for indicator in workday_indicators):
                    return False
            
            print("✅ Confirmed Workday portal")
            
            # Wait for page to load
            time.sleep(5)
            
            # Look for Workday application method selection
            workday_selectors = [
                # Apply Manually options
                "button[data-automation-id*='Apply_Manually']",
                "button[aria-label*='Apply Manually']",
                "button[title*='Apply Manually']",
                "//*[contains(text(), 'Apply Manually')]",
                
                # Alternative selectors
                "button[data-automation-id*='manualApplication']",
                "div[data-automation-id*='Apply_Manually']//button",
                
                # Generic manual apply selectors
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply manually')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'manual application')]"
            ]
            
            print("🔍 Looking for 'Apply Manually' option...")
            
            # Try to find and click "Apply Manually"
            for selector in workday_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS selector
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            print("✅ Found 'Apply Manually' button")
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1)
                            element.click()
                            time.sleep(3)
                            print("✅ Clicked 'Apply Manually'")
                            return True
                except Exception as e:
                    continue
            
            # If "Apply Manually" not found, look for other proceed options
            print("🔍 Looking for other proceed options...")
            
            proceed_selectors = [
                "button[data-automation-id*='continueButton']",
                "button[data-automation-id*='submitButton']",
                "button[aria-label*='Continue']",
                "button[aria-label*='Next']",
                "button[aria-label*='Proceed']",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'continue')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'proceed')]"
            ]
            
            for selector in proceed_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            print(f"✅ Found proceed button")
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1)
                            element.click()
                            time.sleep(3)
                            print("✅ Clicked proceed button")
                            return True
                except Exception:
                    continue
            
            print("⚠️ Could not find apply options on Workday portal")
            return False
            
        except Exception as e:
            print(f"❌ Error handling Workday portal: {str(e)}")
            return False

    def navigate_to_application_form(self, url: str) -> Tuple[bool, str]:
        """
        Navigate from job listing to actual application form.
        
        Args:
            url: Initial job listing URL
            
        Returns:
            Tuple of (success, final_application_url)
        """
        try:
            print("🧭 Navigating to application form...")
            
            # Step 1: Try to find and click apply button
            apply_success, current_url = self.detect_and_click_apply_button(url)
            
            if not apply_success:
                print("⚠️ Could not find apply button, proceeding with current page")
                return False, url
            
            print(f"✅ Successfully clicked apply button, now at: {current_url}")
            
            # Step 2: Check if we're on a Workday portal
            if self.handle_workday_portal():
                print("✅ Successfully handled Workday portal navigation")
                final_url = self.driver.current_url
                print(f"📍 Final application URL: {final_url}")
                return True, final_url
            
            # Step 3: Handle other common redirects or multi-step processes
            # Wait for any redirects to complete
            time.sleep(5)
            
            # Check for common application form indicators
            form_indicators = [
                "form", "application", "apply", "submit", "personal information",
                "contact information", "resume", "cover letter"
            ]
            
            page_source = self.driver.page_source.lower()
            has_form_content = any(indicator in page_source for indicator in form_indicators)
            
            if has_form_content:
                print("✅ Application form detected")
                return True, self.driver.current_url
            else:
                print("⚠️ Application form not detected, but proceeding")
                return True, self.driver.current_url
                
        except Exception as e:
            print(f"❌ Error navigating to application form: {str(e)}")
            return False, url
        """
        Extract form elements from a web page.
        
        Args:
            url: URL of the job application page
            
        Returns:
            Tuple of (HTML content, list of form elements)
        """
        if not self.driver:
            raise ValueError("WebDriver not initialized. Call setup_driver() first.")
        
        try:
            print(f"🌐 Loading page: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Get page HTML
            html_content = self.driver.page_source
            
            # Find all form elements
            form_elements = []
            
            # Input fields
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            form_elements.extend(inputs)
            
            # Select dropdowns
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            form_elements.extend(selects)
            
            # Textareas
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            form_elements.extend(textareas)
            
            print(f"📋 Found {len(form_elements)} form elements")
            
            return html_content, form_elements
        
        except Exception as e:
            print(f"❌ Error extracting form elements: {str(e)}")
            return "", []
    
    def fill_form_field(self, element, suggested_value: str, field_type: str) -> bool:
        """
        Fill a single form field with the suggested value.
        
        Args:
            element: Selenium WebElement
            suggested_value: Value to fill
            field_type: Type of the field
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not suggested_value:
                return False
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            if field_type == "select":
                # Handle dropdown
                select = Select(element)
                try:
                    select.select_by_visible_text(suggested_value)
                except:
                    try:
                        select.select_by_value(suggested_value)
                    except:
                        # Try partial match
                        options = [option.text for option in select.options]
                        for option in options:
                            if suggested_value.lower() in option.lower():
                                select.select_by_visible_text(option)
                                break
            
            elif field_type in ["text", "email", "tel", "number", "password"]:
                # Handle input fields
                element.clear()
                element.send_keys(suggested_value)
            
            elif field_type == "textarea":
                # Handle textarea
                element.clear()
                element.send_keys(suggested_value)
            
            elif field_type in ["checkbox", "radio"]:
                # Handle checkboxes and radio buttons
                if suggested_value.lower() in ["true", "yes", "1"]:
                    if not element.is_selected():
                        element.click()
                elif suggested_value.lower() in ["false", "no", "0"]:
                    if element.is_selected():
                        element.click()
            
            return True
        
        except Exception as e:
            print(f"❌ Error filling field: {str(e)}")
            return False
    
    def auto_fill_application(self, url: str, review_before_submit: bool = True) -> Dict[str, Any]:
        """
        Automatically fill a job application form.
        
        Args:
            url: URL of the job application page or job listing page
            review_before_submit: Whether to pause for user review before submitting
            
        Returns:
            Dictionary with results and statistics
        """
        # Quick check for Workday portal
        is_workday_url = any(indicator in url.lower() for indicator in ["workday", "myworkdayjobs"])
        
        # If this is a Workday URL and we have the specialized service, use it
        if is_workday_url and WORKDAY_SERVICE_AVAILABLE:
            print("🏢 Detected Workday URL - using specialized WorkdayApplyService")
            try:
                # Use the dedicated Workday service
                workday_result = apply_to_workday_job(
                    user_profile=self.user_profile,
                    url=url,
                    headless=False if review_before_submit else True
                )
                
                # Convert result to standard format
                return {
                    "url": url,
                    "success": workday_result["success"],
                    "final_url": workday_result.get("final_url", url),
                    "fields_analyzed": workday_result.get("fields_filled", 0),
                    "fields_filled": workday_result.get("fields_filled", 0),
                    "fields_failed": workday_result.get("fields_failed", 0),
                    "form_fields": [],
                    "errors": workday_result.get("errors", []),
                    "navigation_steps": workday_result.get("steps_completed", []),
                    "service_used": "WorkdayApplyService",
                    "workday_specialized": True
                }
                
            except Exception as e:
                print(f"⚠️ Workday service failed, falling back to standard processing: {str(e)}")
                # Continue with standard processing below
        
        # Standard processing for non-Workday sites or when Workday service fails
        if not self.driver:
            self.setup_driver(headless=False)  # Use visible browser for review
        
        results = {
            "url": url,
            "success": False,
            "fields_analyzed": 0,
            "fields_filled": 0,
            "fields_failed": 0,
            "form_fields": [],
            "errors": [],
            "navigation_steps": [],
            "service_used": "AutoApplyService",
            "workday_specialized": False
        }
        
        try:
            # Step 1: Navigate to the actual application form
            print("🧭 Step 1: Navigating to application form...")
            nav_success, final_url = self.navigate_to_application_form(url)
            
            if nav_success:
                results["navigation_steps"].append(f"Successfully navigated from {url} to {final_url}")
                results["final_url"] = final_url
            else:
                results["navigation_steps"].append(f"Could not navigate to application form, using original URL: {url}")
                results["final_url"] = url
            
            # Step 2: Extract form elements and HTML from the final URL
            print("📋 Step 2: Analyzing application form...")
            html_content, form_elements = self.extract_form_elements(results["final_url"])
            
            if not form_elements:
                results["errors"].append("No form elements found on the application page")
                return results
            
            # Step 3: Analyze form with LLM
            print("🤖 Step 3: Analyzing form with AI...")
            suggested_fields = self.analyze_form_with_llm(html_content)
            
            results["fields_analyzed"] = len(suggested_fields)
            results["form_fields"] = [asdict(field) for field in suggested_fields]
            
            if not suggested_fields:
                results["errors"].append("LLM could not analyze form fields")
                return results
            
            # Step 4: Fill form fields
            print("✍️ Step 4: Filling form fields...")
            
            # Check if this is a Workday portal and handle specific elements
            current_url = self.driver.current_url
            is_workday = "workday" in current_url.lower()
            
            if is_workday:
                print("🏢 Detected Workday portal - applying fallback handling")
                results["workday_specialized"] = False  # Using fallback, not specialized
                
                # Get Workday-specific fields
                workday_fields = self.detect_workday_fields()
                
                # Merge with LLM-detected fields
                all_fields = suggested_fields + workday_fields
                
                # Handle Workday-specific elements
                workday_filled = self.handle_workday_specific_elements()
                results["fields_filled"] += workday_filled
                
                print(f"🏢 Filled {workday_filled} Workday-specific fields")
            else:
                all_fields = suggested_fields
            
            # Fill regular form fields
            for field in all_fields:
                if field.confidence < 0.3:  # Skip low confidence suggestions
                    continue
                
                try:
                    # Find the element
                    element = None
                    
                    if field.element_id:
                        try:
                            element = self.driver.find_element(By.ID, field.element_id)
                        except:
                            pass
                    
                    if not element and field.element_name:
                        try:
                            element = self.driver.find_element(By.NAME, field.element_name)
                        except:
                            pass
                    
                    if not element:
                        # Try to find by label text or placeholder
                        try:
                            xpath_queries = [
                                f"//input[@placeholder='{field.placeholder}']",
                                f"//input[following-sibling::label[contains(text(), '{field.label}')]]",
                                f"//label[contains(text(), '{field.label}')]/following-sibling::input",
                                f"//label[contains(text(), '{field.label}')]/..//input",
                                f"//textarea[following-sibling::label[contains(text(), '{field.label}')]]",
                                f"//label[contains(text(), '{field.label}')]/following-sibling::textarea"
                            ]
                            
                            for xpath in xpath_queries:
                                if field.placeholder or field.label:
                                    try:
                                        element = self.driver.find_element(By.XPATH, xpath)
                                        break
                                    except:
                                        continue
                        except:
                            pass
                    
                    if element:
                        success = self.fill_form_field(element, field.suggested_value, field.element_type)
                        if success:
                            results["fields_filled"] += 1
                            print(f"✅ Filled {field.label}: {field.suggested_value}")
                        else:
                            results["fields_failed"] += 1
                            print(f"❌ Failed to fill {field.label}")
                    else:
                        results["fields_failed"] += 1
                        print(f"❌ Could not find element for {field.label}")
                
                except Exception as e:
                    results["fields_failed"] += 1
                    results["errors"].append(f"Error filling {field.label}: {str(e)}")
            
            # Handle multi-page Workday forms
            if is_workday:
                print("🏢 Checking for Workday next/continue buttons...")
                self.handle_workday_navigation()
            
            # Step 5: Pause for review if requested
            if review_before_submit:
                print("\n🔍 REVIEW MODE")
                print("=" * 50)
                print(f"📍 Application URL: {results.get('final_url', url)}")
                print(f"✅ Successfully filled: {results['fields_filled']} fields")
                print(f"❌ Failed to fill: {results['fields_failed']} fields")
                print(f"📊 Total analyzed: {results['fields_analyzed']} fields")
                
                if results["navigation_steps"]:
                    print("\n🧭 Navigation Steps:")
                    for step in results["navigation_steps"]:
                        print(f"   • {step}")
                
                print("\nPlease review the form in the browser window.")
                print("Press Enter to continue or 'q' to quit without submitting...")
                
                user_input = input().strip().lower()
                if user_input == 'q':
                    print("🛑 Application filling cancelled by user")
                    return results
            
            results["success"] = True
            print(f"🎉 Application form filled successfully!")
            
        except Exception as e:
            results["errors"].append(f"General error: {str(e)}")
            print(f"❌ Error in auto_fill_application: {str(e)}")
        
        return results
    
    def detect_workday_fields(self) -> List[FormField]:
        """
        Detect Workday-specific form fields that may not be captured by standard analysis.
        
        Returns:
            List of additional FormField objects for Workday-specific elements
        """
        workday_fields = []
        
        try:
            # Common Workday field patterns
            workday_field_mapping = {
                # Personal Information
                "input[data-automation-id*='firstName']": ("first_name", "First Name"),
                "input[data-automation-id*='lastName']": ("last_name", "Last Name"),
                "input[data-automation-id*='email']": ("email", "Email Address"),
                "input[data-automation-id*='phone']": ("phone", "Phone Number"),
                
                # Address fields
                "input[data-automation-id*='addressLine1']": ("address", "Address Line 1"),
                "input[data-automation-id*='city']": ("city", "City"),
                "input[data-automation-id*='state']": ("state", "State"),
                "input[data-automation-id*='postalCode']": ("zip_code", "ZIP Code"),
                
                # Work Authorization
                "select[data-automation-id*='legallyAuthorized']": ("work_authorized", "Work Authorization"),
                "select[data-automation-id*='sponsorship']": ("visa_status", "Visa Sponsorship"),
                
                # Experience
                "input[data-automation-id*='experience']": ("years_of_experience", "Years of Experience"),
                "textarea[data-automation-id*='coverLetter']": ("cover_letter", "Cover Letter"),
                
                # LinkedIn
                "input[data-automation-id*='linkedIn']": ("linkedin_url", "LinkedIn Profile"),
            }
            
            for selector, (profile_field, label) in workday_field_mapping.items():
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            field_value = getattr(self.user_profile, profile_field, "")
                            
                            # Convert boolean values for work authorization
                            if profile_field == "work_authorized":
                                field_value = "Yes" if field_value else "No"
                            
                            workday_field = FormField(
                                element_id=element.get_attribute("id") or "",
                                element_name=element.get_attribute("name") or "",
                                element_type=element.tag_name,
                                label=label,
                                suggested_value=str(field_value),
                                confidence=0.9  # High confidence for Workday-specific selectors
                            )
                            workday_fields.append(workday_field)
                            break  # Only take the first matching element
                            
                except Exception as e:
                    continue
            
            print(f"🏢 Detected {len(workday_fields)} Workday-specific fields")
            return workday_fields
            
        except Exception as e:
            print(f"❌ Error detecting Workday fields: {str(e)}")
            return []

    def handle_workday_specific_elements(self) -> int:
        """
        Handle Workday-specific form elements that may need special treatment.
        
        Returns:
            Number of fields successfully filled
        """
        filled_count = 0
        
        try:
            # Handle file upload for resume
            resume_upload_selectors = [
                "input[data-automation-id*='file-upload']",
                "input[data-automation-id*='resume']",
                "input[type='file'][accept*='pdf']",
                "input[type='file'][accept*='doc']"
            ]
            
            print("📄 Looking for resume upload fields...")
            for selector in resume_upload_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            print("📄 Found resume upload field (manual action required)")
                            # Note: File upload requires manual action or pre-uploaded file path
                            break
                except Exception:
                    continue
            
            # Handle dropdown selections
            dropdown_mappings = {
                "select[data-automation-id*='country']": self.user_profile.country,
                "select[data-automation-id*='legallyAuthorized']": "Yes" if self.user_profile.work_authorized else "No",
                "select[data-automation-id*='sponsorship']": "No" if self.user_profile.work_authorized else "Yes",
            }
            
            for selector, value in dropdown_mappings.items():
                if not value:
                    continue
                    
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            select = Select(element)
                            try:
                                select.select_by_visible_text(value)
                                filled_count += 1
                                print(f"✅ Selected '{value}' in dropdown")
                                break
                            except:
                                # Try selecting by value
                                try:
                                    select.select_by_value(value.lower())
                                    filled_count += 1
                                    print(f"✅ Selected '{value}' in dropdown (by value)")
                                    break
                                except:
                                    pass
                except Exception:
                    continue
            
            # Handle checkboxes for work authorization
            checkbox_selectors = [
                "input[data-automation-id*='legallyAuthorized'][type='checkbox']",
                "input[data-automation-id*='workAuthorization'][type='checkbox']"
            ]
            
            for selector in checkbox_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            if self.user_profile.work_authorized and not element.is_selected():
                                element.click()
                                filled_count += 1
                                print("✅ Checked work authorization checkbox")
                            elif not self.user_profile.work_authorized and element.is_selected():
                                element.click()
                                filled_count += 1
                                print("✅ Unchecked work authorization checkbox")
                            break
                except Exception:
                    continue
            
            return filled_count
            
        except Exception as e:
            print(f"❌ Error handling Workday elements: {str(e)}")
            return 0

    def handle_workday_navigation(self) -> bool:
        """
        Handle navigation through multi-page Workday application forms.
        
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            # Look for Next/Continue buttons in Workday
            navigation_selectors = [
                "button[data-automation-id*='bottom-navigation']",
                "button[data-automation-id*='next']",
                "button[data-automation-id*='continue']",
                "button[aria-label*='Next']",
                "button[aria-label*='Continue']",
                "button[title*='Next']",
                "button[title*='Continue']",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]",
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'continue')]"
            ]
            
            for selector in navigation_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Check if this is actually a navigation button (not submit)
                            button_text = element.text.lower()
                            if any(word in button_text for word in ['next', 'continue', 'proceed']):
                                print(f"🔄 Found Workday navigation button: {button_text}")
                                print("⚠️ Multi-page form detected - manual navigation may be required")
                                return True
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ Error in Workday navigation: {str(e)}")
            return False
        """
        Create a user profile by extracting information from resume text using LLM.
        
        Args:
            resume_text: Text content of the resume
            
        Returns:
            UserProfile object with extracted information
        """
        prompt = f"""
        Extract personal and professional information from the following resume text and return it as JSON:

        Resume Text:
        {resume_text}

        Extract the following information and return as JSON:
        {{
            "first_name": "",
            "last_name": "",
            "email": "",
            "phone": "",
            "address": "",
            "city": "",
            "state": "",
            "current_title": "",
            "years_of_experience": "",
            "linkedin_url": "",
            "github_url": "",
            "portfolio_url": "",
            "education_level": "",
            "university": "",
            "degree": "",
            "graduation_year": "",
            "skills": ["skill1", "skill2"],
            "work_authorized": true,
            "visa_status": ""
        }}

        Rules:
        1. Extract only information that is clearly present in the resume
        2. For years_of_experience, calculate based on work history
        3. For skills, extract technical skills mentioned
        4. Leave fields empty if information is not found
        5. Return only valid JSON, no additional text
        """
        
        try:
            if self.llm_provider == "openai":
                response = self.llm_client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert resume parser."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                llm_response = response.choices[0].message.content
            
            elif self.llm_provider == "anthropic":
                response = self.llm_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                llm_response = response.content[0].text
            
            # Parse JSON response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = llm_response[json_start:json_end]
                profile_data = json.loads(json_str)
                
                # Create UserProfile object
                profile = UserProfile(**profile_data)
                profile.resume_text = resume_text
                
                return profile
            else:
                print("❌ Could not extract profile from resume")
                return UserProfile()
        
        except Exception as e:
            print(f"❌ Error creating profile from resume: {str(e)}")
            return UserProfile()
    
    def save_profile(self, profile: UserProfile, filename: str = "user_profile.json"):
        """Save user profile to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(asdict(profile), f, indent=2)
            print(f"💾 Profile saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving profile: {str(e)}")
    
    def load_profile(self, filename: str = "user_profile.json") -> UserProfile:
        """Load user profile from JSON file."""
        try:
            with open(filename, 'r') as f:
                profile_data = json.load(f)
            profile = UserProfile(**profile_data)
            print(f"📂 Profile loaded from {filename}")
            return profile
        except Exception as e:
            print(f"❌ Error loading profile: {str(e)}")
            return UserProfile()


# Example usage and testing
if __name__ == "__main__":
    # Example user profile
    sample_profile = UserProfile(
        first_name="John",
        last_name="Doe",
        email="john.doe@email.com",
        phone="+1-555-123-4567",
        address="123 Main St",
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
        willing_to_relocate=True
    )
    
    print("🚀 AutoApplyService Example")
    print("=" * 40)
    print("Sample User Profile:")
    print(json.dumps(asdict(sample_profile), indent=2))
    
    # Note: To use this service, you'll need:
    # 1. ChromeDriver installed
    # 2. OpenAI or Anthropic API key
    # 3. Valid job application URL
    
    # Example initialization (uncomment to use):
    # service = AutoApplyService(
    #     user_profile=sample_profile,
    #     llm_provider="openai",
    #     api_key="your-api-key-here"
    # )
    # 
    # # Fill application
    # results = service.auto_fill_application(
    #     url="https://example-job-application.com",
    #     review_before_submit=True
    # )
    # 
    # print("Results:", results)
    # service.close_driver()
