"""
AI-powered job tagging and search service using unified AI providers.

This service provides:
- AI-based job analysis and tagging
- Smart job search with natural language queries
- Job categorization and skills extraction
- Relevance scoring based on user queries
- Support for multiple AI providers (OpenAI, Groq, Llama)
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import unified AI service
from .ai_service import ai_service


class AITaggingService:
    """
    AI-powered job tagging and search service using unified AI providers.
    
    This service provides:
    - AI-based job analysis and tagging
    - Smart job search with natural language queries
    - Job categorization and skills extraction
    - Relevance scoring based on user queries
    """
    
    def __init__(self):
        """Initialize the AI Tagging Service with unified AI service."""
        self.ai_service = ai_service
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.ai_service.is_available()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get current AI provider information."""
        return self.ai_service.get_provider_info()
    
    def set_provider(self, provider_name: str, model: Optional[str] = None) -> bool:
        """Set the AI provider and model."""
        return self.ai_service.set_provider(provider_name, model)
    
    def tag_jobs(self, jobs_df: pd.DataFrame, progress_callback=None) -> pd.DataFrame:
        """
        Add AI-generated tags to jobs.
        
        Args:
            jobs_df: DataFrame containing job data
            progress_callback: Optional callback function for progress updates
            
        Returns:
            DataFrame with added AI tags
        """
        if not self.is_available():
            st.error("AI service not available. Please configure OpenAI API key.")
            return jobs_df
        
        if jobs_df.empty:
            st.warning("No jobs to process - DataFrame is empty.")
            return jobs_df
        
        st.info(f"🔧 Starting AI analysis for {len(jobs_df)} jobs...")
        
        tagged_df = jobs_df.copy()
        
        # Initialize AI columns
        tagged_df['ai_tags'] = ''
        tagged_df['ai_skills'] = ''
        tagged_df['ai_category'] = ''
        tagged_df['ai_seniority'] = ''
        tagged_df['ai_relevance_score'] = 0.0
        
        total_jobs = len(jobs_df)
        successful_tags = 0
        
        for idx, job in jobs_df.iterrows():
            try:
                if progress_callback:
                    progress_callback(idx + 1, total_jobs)
                
                # Prepare job text for analysis
                job_text = self._prepare_job_text(job)
                
                if not job_text.strip():
                    st.warning(f"Job {idx + 1}: Empty job text, skipping...")
                    continue
                
                # Get AI analysis
                ai_analysis = self._analyze_job_with_ai(job_text)
                
                if ai_analysis:
                    tagged_df.at[idx, 'ai_tags'] = ai_analysis.get('tags', '')
                    tagged_df.at[idx, 'ai_skills'] = ai_analysis.get('skills', '')
                    tagged_df.at[idx, 'ai_category'] = ai_analysis.get('category', '')
                    tagged_df.at[idx, 'ai_seniority'] = ai_analysis.get('seniority', '')
                    tagged_df.at[idx, 'ai_relevance_score'] = ai_analysis.get('relevance_score', 0.0)
                    successful_tags += 1
                else:
                    st.warning(f"Job {idx + 1}: AI analysis failed")
            
            except Exception as e:
                st.warning(f"Error processing job {idx + 1}: {str(e)}")
                continue
        
        st.info(f"🎯 Successfully processed {successful_tags} out of {total_jobs} jobs")
        return tagged_df
    
    def search_jobs_with_ai(self, jobs_df: pd.DataFrame, user_query: str) -> pd.DataFrame:
        """
        Perform AI-powered job search based on natural language query.
        
        Args:
            jobs_df: DataFrame containing job data
            user_query: Natural language search query
            
        Returns:
            Filtered and ranked DataFrame based on AI analysis
        """
        if not self.is_available():
            st.error("AI service not available. Please configure OpenAI API key.")
            return jobs_df
        
        if jobs_df.empty or not user_query.strip():
            return jobs_df
        
        # Analyze user query to extract intent and keywords
        query_analysis = self._analyze_user_query(user_query)
        
        if not query_analysis:
            return jobs_df
        
        # Score jobs based on relevance to query
        scored_jobs = []
        
        for idx, job in jobs_df.iterrows():
            try:
                job_text = self._prepare_job_text(job)
                relevance_score = self._calculate_relevance_score(job_text, query_analysis)
                
                if relevance_score > 0.3:  # Threshold for relevance
                    job_data = job.to_dict()
                    job_data['ai_search_score'] = relevance_score
                    job_data['ai_match_reasons'] = self._get_match_reasons(job_text, query_analysis)
                    scored_jobs.append(job_data)
            
            except Exception as e:
                continue
        
        if not scored_jobs:
            return pd.DataFrame()
        
        # Create result DataFrame and sort by relevance
        result_df = pd.DataFrame(scored_jobs)
        result_df = result_df.sort_values('ai_search_score', ascending=False)
        
        return result_df
    
    def _prepare_job_text(self, job: pd.Series) -> str:
        """Prepare job text for AI analysis."""
        text_parts = []
        
        # Add title
        if pd.notna(job.get('title')):
            text_parts.append(f"Title: {job['title']}")
        
        # Add company
        if pd.notna(job.get('company')):
            text_parts.append(f"Company: {job['company']}")
        
        # Add description
        if pd.notna(job.get('description')):
            description = str(job['description'])[:1000]  # Limit length
            text_parts.append(f"Description: {description}")
        
        # Add skills if available
        if pd.notna(job.get('skills')):
            text_parts.append(f"Skills: {job['skills']}")
        
        # Add job type and level
        if pd.notna(job.get('job_type')):
            text_parts.append(f"Job Type: {job['job_type']}")
        
        if pd.notna(job.get('job_level')):
            text_parts.append(f"Level: {job['job_level']}")
        
        return "\n".join(text_parts)
    
    def _analyze_job_with_ai(self, job_text: str) -> Optional[Dict[str, Any]]:
        """Analyze job with AI to extract tags and categorization."""
        if not self.is_available():
            return self._get_mock_analysis(job_text)
        
        try:
            prompt = f"""
            Analyze this job posting and provide structured information:

            Job Text:
            {job_text}

            Please provide a JSON response with:
            1. "tags": 5-10 relevant keywords/tags (comma-separated)
            2. "skills": Technical skills required (comma-separated)
            3. "category": Job category (e.g., Software Engineering, Data Science, Marketing)
            4. "seniority": Seniority level (Entry, Mid, Senior, Lead, Executive)
            5. "relevance_score": Overall job attractiveness score (0.0-1.0)

            Return only valid JSON format.
            """
            
            result = self.ai_service.generate_json_completion(
                prompt=prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            return result if result else self._get_mock_analysis(job_text)
        
        except Exception as e:
            st.warning(f"AI job analysis failed: {str(e)}")
            return self._get_mock_analysis(job_text)
        
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg:
                st.warning("🚫 OpenAI API quota exceeded. Using mock AI analysis for demonstration.")
                st.info("💡 Visit https://platform.openai.com/account/billing to add credits for real AI analysis.")
                return self._get_mock_ai_analysis(job_text)
            elif "rate_limit" in error_msg.lower():
                st.warning("⏱️ OpenAI API rate limit reached. Using mock AI analysis.")
                return self._get_mock_ai_analysis(job_text)
            elif "invalid_api_key" in error_msg.lower():
                st.error("🔑 Invalid OpenAI API key. Using mock AI analysis.")
                return self._get_mock_ai_analysis(job_text)
            else:
                st.warning(f"AI job analysis failed: {error_msg}. Using mock analysis.")
                return self._get_mock_ai_analysis(job_text)
    
    def _analyze_user_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Analyze user query to extract search intent and keywords."""
        if not self.is_available():
            return self._get_mock_query_analysis(query)
        
        try:
            prompt = f"""
            Analyze this job search query and extract search intent:

            User Query: "{query}"

            Please provide a JSON response with:
            1. "keywords": Important keywords for job matching (list)
            2. "job_titles": Relevant job titles (list)
            3. "skills": Technical skills mentioned (list)
            4. "seniority": Desired seniority level if mentioned
            5. "location": Location preference if mentioned
            6. "remote": Remote work preference (true/false/null)
            7. "intent": Primary search intent (e.g., "technical_role", "management", "specific_company")

            Return only valid JSON format.
            """
            
            result = self.ai_service.generate_json_completion(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3
            )
            
            return result if result else self._get_mock_query_analysis(query)
        
        except Exception as e:
            st.warning(f"AI query analysis failed: {str(e)}")
            return self._get_mock_query_analysis(query)
    
    def _calculate_relevance_score(self, job_text: str, query_analysis: Dict[str, Any]) -> float:
        """Calculate relevance score between job and query analysis."""
        if not self.is_available():
            return 0.75  # Mock score
        
        try:
            prompt = f"""
            Calculate how well this job matches the user's search criteria:

            Job:
            {job_text[:800]}

            User Search Criteria:
            {query_analysis}

            Provide a relevance score from 0.0 to 1.0 where:
            - 1.0 = Perfect match
            - 0.7-0.9 = Very good match
            - 0.5-0.6 = Good match
            - 0.3-0.4 = Partial match
            - 0.0-0.2 = Poor match

            Return only the numeric score (e.g., 0.85).
            """
            
            response = self.ai_service.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            if response:
                return float(response.strip())
            return 0.75
        
        except Exception as e:
            st.warning(f"AI relevance scoring failed: {str(e)}")
            return 0.75
    
    def _get_mock_analysis(self, job_text: str) -> Dict[str, Any]:
        """
        Generate mock AI analysis for testing when API is unavailable.
        This provides realistic sample data for development and testing.
        """
        import re
        
        # Extract basic information from job text
        title_match = re.search(r'Title: (.+)', job_text)
        title = title_match.group(1) if title_match else "Unknown"
        
        # Simple keyword-based analysis
        text_lower = job_text.lower()
        
        # Determine category based on keywords
        if any(word in text_lower for word in ['python', 'java', 'javascript', 'developer', 'engineer', 'software']):
            category = "Software Engineering"
            skills = "Python, JavaScript, SQL, Git"
            tags = "software-development, programming, backend, api"
        elif any(word in text_lower for word in ['data', 'analyst', 'science', 'machine learning', 'ml']):
            category = "Data Science"
            skills = "Python, SQL, Machine Learning, Statistics"
            tags = "data-science, analytics, machine-learning, python"
        elif any(word in text_lower for word in ['marketing', 'social media', 'content', 'campaign']):
            category = "Marketing"
            skills = "Digital Marketing, Analytics, Content Creation"
            tags = "marketing, digital-marketing, content, campaigns"
        elif any(word in text_lower for word in ['sales', 'account', 'business development']):
            category = "Sales"
            skills = "Sales, Communication, CRM, Negotiation"
            tags = "sales, business-development, client-relations"
        else:
            category = "General"
            skills = "Communication, Problem Solving, Teamwork"
            tags = "general, professional, teamwork"
        
        # Determine seniority
        if any(word in text_lower for word in ['senior', 'lead', 'principal', 'staff']):
            seniority = "Senior"
        elif any(word in text_lower for word in ['junior', 'entry', 'graduate', 'intern']):
            seniority = "Entry"
        elif any(word in text_lower for word in ['manager', 'director', 'head']):
            seniority = "Lead"
        else:
            seniority = "Mid"
        
        return {
            "tags": tags,
            "skills": skills,
            "category": category,
            "seniority": seniority,
            "relevance_score": 0.75  # Default good score
        }
    
    def _get_mock_query_analysis(self, query: str) -> Dict[str, Any]:
        """Generate mock query analysis for testing."""
        query_lower = query.lower()
        
        # Extract basic info from query
        keywords = []
        job_titles = []
        skills = []
        seniority = None
        remote = None
        
        # Simple keyword extraction
        if 'python' in query_lower:
            skills.append('Python')
            job_titles.append('Python Developer')
        if 'senior' in query_lower:
            seniority = 'Senior'
        if 'remote' in query_lower:
            remote = True
        if 'data' in query_lower:
            keywords.extend(['data', 'analysis'])
            job_titles.append('Data Analyst')
        
        return {
            'keywords': keywords or ['development', 'programming'],
            'job_titles': job_titles or ['Software Developer'],
            'skills': skills or ['Programming'],
            'seniority': seniority,
            'location': None,
            'remote': remote,
            'intent': 'technical_role'
        }
    
    def _get_match_reasons(self, job_text: str, query_analysis: Dict[str, Any]) -> str:
        """Get reasons why a job matches the user query."""
        if not self.is_available():
            return "Mock AI: Job matches based on keywords and requirements."
        
        try:
            prompt = f"""
            Explain briefly why this job matches the user's search criteria:

            Job: {job_text[:500]}
            Search Criteria: {query_analysis}

            Provide 2-3 brief bullet points explaining the match.
            """
            
            response = self.ai_service.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
            
            return response if response else "AI analysis unavailable"
        
        except Exception as e:
            st.warning(f"AI match reason analysis failed: {str(e)}")
            return "AI analysis unavailable"


# Global instance for easy access
ai_tagging_service = AITaggingService()
ai_tagging_service = AITaggingService()