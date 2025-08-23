from Utils.constants import COVER_LETTER_TEMPLATE, USER_DATA, COVER_LETTER_DATA_TEMPLATE
from Utils.prompt import COVER_LETTER_EXTRACTION_PROMPT, COVER_LETTER_COMPANY_ANALYSIS_PROMPT, COVER_LETTER_PERSONALIZATION_PROMPT
from services.ai_service import ai_service
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
import tempfile

class CoverLetterGenerator:
    def __init__(self):
        """Initialize the AI-powered cover letter generator."""
        self.user_data = USER_DATA
        self.ai_service = ai_service
    
    def generate_cover_letter_from_job(self, job_description: str, 
                                     output_file: Optional[str] = None) -> Tuple[str, Dict]:
        """
        Generate a cover letter from job description using AI
        
        Args:
            job_description: The job posting description
            output_file: Optional output file path. If None, creates temp file
            
        Returns:
            Tuple of (file_path, cover_letter_data)
        """
        # Extract cover letter data using AI
        cover_letter_data = self._extract_cover_letter_data(job_description)
        
        if not cover_letter_data:
            raise Exception("Failed to generate cover letter data from job description")
        
        # Generate the HTML file
        html_file = self.generate_cover_letter(cover_letter_data, output_file)
        
        return html_file, cover_letter_data
    
    def _extract_cover_letter_data(self, job_description: str) -> Optional[Dict]:
        """
        Extract cover letter data from job description using AI
        
        Args:
            job_description: The job posting description
            
        Returns:
            Dictionary containing cover letter data or None if failed
        """
        if not self.ai_service.is_available():
            raise Exception("AI service is not available. Please check your API keys.")
        
        try:
            # Prepare user profile summary for the AI
            user_profile = self._format_user_profile()
            
            # Create the extraction prompt
            prompt = COVER_LETTER_EXTRACTION_PROMPT.format(
                job_description=job_description,
                user_profile=user_profile
            )
            
            # Get AI response
            response = self.ai_service.get_chatcompletion(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )
            
            if not response:
                raise Exception("AI service returned empty response")
            
            # Parse JSON response
            extracted_data = self._parse_ai_response(response)
            
            if not extracted_data:
                raise Exception("Failed to parse AI response")
            
            # Merge with user data and template
            cover_letter_data = self._merge_cover_letter_data(extracted_data)
            
            return cover_letter_data
            
        except Exception as e:
            print(f"Error extracting cover letter data: {e}")
            return None
    
    def _format_user_profile(self) -> str:
        """Format user profile for AI prompt"""
        profile_text = f"""
Name: {self.user_data['applicant_name']}
Email: {self.user_data['email']}
Phone: {self.user_data['phone']}
LinkedIn: {self.user_data['linkedin']}
Portfolio: {self.user_data['portfolio']}

Work Experience:
"""
        
        for exp in self.user_data['work_experiences']:
            profile_text += f"- {exp['position']} at {exp['company']} ({exp['duration']}): {exp['description']}\n"
        
        profile_text += f"\nKey Skills: {', '.join(self.user_data['skills'])}"
        
        return profile_text
    
    def _parse_ai_response(self, response: str) -> Optional[Dict]:
        """Parse AI response to extract JSON data"""
        try:
            # Try to parse as direct JSON
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # Look for JSON in code blocks
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_content = response[json_start:json_end].strip()
                return json.loads(json_content)
            
            # Look for JSON in any code block
            if '```' in response:
                json_start = response.find('```') + 3
                json_end = response.find('```', json_start)
                json_content = response[json_start:json_end].strip()
                return json.loads(json_content)
            
            # Try to find JSON-like content between braces
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_content = response[start_idx:end_idx]
                return json.loads(json_content)
            
            return None
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return None
    
    def _merge_cover_letter_data(self, ai_data: Dict) -> Dict:
        """Merge AI-generated data with user data and template"""
        # Start with template data
        merged_data = COVER_LETTER_DATA_TEMPLATE.copy()
        
        # Update with user data
        merged_data.update({
            'applicant_name': self.user_data['applicant_name'],
            'phone': self.user_data['phone'],
            'email': self.user_data['email'],
            'address': self.user_data['address'],
            'linkedin': self.user_data['linkedin'],
            'portfolio': self.user_data['portfolio'],
            'date': datetime.now().strftime('%B %d, %Y')
        })
        
        # Update with AI-generated content
        merged_data.update(ai_data)
        
        return merged_data
    
    def analyze_company_from_job(self, job_description: str) -> Optional[str]:
        """
        Analyze company information from job description
        
        Args:
            job_description: The job posting description
            
        Returns:
            Company analysis or None if failed
        """
        if not self.ai_service.is_available():
            return None
        
        try:
            prompt = COVER_LETTER_COMPANY_ANALYSIS_PROMPT.format(
                job_description=job_description
            )
            
            response = self.ai_service.get_chatcompletion(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            print(f"Error analyzing company: {e}")
            return None
    
    def generate_cover_letter(self, data: Dict[str, str], output_file: Optional[str] = None) -> str:
        """
        Generate a cover letter HTML file
        
        Args:
            data: Dictionary containing all the cover letter data
            output_file: Optional output file path. If None, creates temp file
            
        Returns:
            Path to the generated HTML file
        """
        html_content = COVER_LETTER_TEMPLATE.format(**data)
        
        if output_file is None:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                output_file = f.name
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return output_file