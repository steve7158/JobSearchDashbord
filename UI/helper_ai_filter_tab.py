"""
AI Filter Helper Module for Job Portal Dashboard

This module contains all AI-related functionality for the Filter Tab UI.
It provides methods for AI search, tagging, filtering, and UI rendering components.

Key Features:
- AI-powered job search with natural language queries
- Automated job tagging with skills, categories, and seniority levels
- AI-based filtering capabilities (category, seniority, tags, match scores)
- Progress tracking and result caching for better user experience
- Graceful fallbacks when OpenAI API is not available

Usage:
    from UI.helper_ai_filter_tab import AIFilterHelper
    
    # Initialize with session key prefix
    ai_helper = AIFilterHelper("filter_tab_")
    
    # Use in FilterTabUI class
    filtered_df = ai_helper.render_ai_search_section(jobs_df)
    ai_helper.render_ai_filters(jobs_df, advanced_filters)
    filtered_df = ai_helper.apply_ai_filters(filtered_df, filters)

Dependencies:
    - services.perform_ai_tagging: OpenAI integration service
    - streamlit: UI rendering
    - pandas: Data manipulation
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, Callable

# Import AI tagging service
try:
    from services.perform_ai_tagging import ai_tagging_service
    AI_SERVICE_AVAILABLE = True
except ImportError:
    AI_SERVICE_AVAILABLE = False
    ai_tagging_service = None


class AIFilterHelper:
    """
    Helper class for AI-related functionality in the Filter Tab.
    
    This class provides methods for:
    - AI-powered job search and ranking
    - AI job tagging and analysis
    - AI-based filter rendering and application
    - AI search result caching and management
    """
    
    def __init__(self, session_key_prefix: str):
        """
        Initialize the AI Filter Helper.
        
        Args:
            session_key_prefix: Prefix for session state keys to avoid conflicts
        """
        self.session_key_prefix = session_key_prefix
    
    @staticmethod
    def is_ai_available() -> bool:
        """Check if AI service is available."""
        return AI_SERVICE_AVAILABLE and ai_tagging_service is not None and ai_tagging_service.is_available()
    
    def render_ai_search_section(self, jobs_df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Render AI-powered search section with search input, tagging buttons, and result caching.
        
        Args:
            jobs_df: DataFrame containing job data
            
        Returns:
            Optional[pd.DataFrame]: AI-filtered results if available, None otherwise
        """
        if not self.is_ai_available():
            with st.expander("🤖 AI-Powered Search (Unavailable)", expanded=False):
                st.warning("AI service is not available. Please configure API keys to enable AI features.")
                
                # Show provider info
                from services.ai_service import ai_service
                provider_info = ai_service.get_provider_info()
                
                if len(provider_info['available_providers']) > 0:
                    st.info(f"Available providers: {', '.join(provider_info['available_providers'])}")
                    st.info("Current provider has API issues. Check your API key and quota.")
                else:
                    st.info("No AI providers configured. Set up API keys in .env file:")
                    st.code("""
# Add to .env file:
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
LLAMA_API_KEY=your_llama_api_key_here
                    """)
            return None
        
        st.markdown("### 🤖 AI-Powered Job Search & Tagging")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # AI search query input
            ai_query = st.text_input(
                "🔍 Describe your ideal job in natural language",
                placeholder="e.g., 'Senior Python developer with machine learning experience in a remote-friendly startup'",
                key=f"{self.session_key_prefix}ai_query",
                help="Use natural language to describe what you're looking for. AI will find relevant jobs and rank them by match quality."
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            search_button = st.button(
                "🔍 AI Search",
                use_container_width=True,
                type="primary",
                help="Perform AI-powered search based on your query"
            )
        
        # AI Tagging section
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tag_button = st.button(
                "🏷️ Add AI Tags",
                use_container_width=True,
                help="Analyze all jobs and add AI-generated tags, skills, and categories"
            )
        
        with col2:
            if 'ai_tags' in jobs_df.columns and not jobs_df['ai_tags'].isna().all():
                st.info(f"✅ {len(jobs_df[jobs_df['ai_tags'].notna()])} jobs already have AI tags")
            else:
                st.info("No AI tags found")
        
        with col3:
            # Clear AI results button
            if st.button("🔄 Clear AI Results", help="Reset to show all jobs"):
                if f"{self.session_key_prefix}ai_search_results" in st.session_state:
                    del st.session_state[f"{self.session_key_prefix}ai_search_results"]
                st.rerun()
        
        # Handle AI search
        if search_button and ai_query.strip():
            return self.perform_ai_search(jobs_df, ai_query)
        
        # Handle AI tagging
        if tag_button:
            return self.perform_ai_tagging(jobs_df)
        
        # Return cached AI search results if available
        if f"{self.session_key_prefix}ai_search_results" in st.session_state:
            cached_results = st.session_state[f"{self.session_key_prefix}ai_search_results"]
            if not cached_results.empty:
                st.success(f"🤖 Showing {len(cached_results)} AI-filtered results from previous search")
                return cached_results
        
        return None
    
    def perform_ai_search(self, jobs_df: pd.DataFrame, query: str) -> Optional[pd.DataFrame]:
        """
        Perform AI-powered job search with progress tracking and result caching.
        
        Args:
            jobs_df: DataFrame containing job data
            query: Natural language search query
            
        Returns:
            Optional[pd.DataFrame]: AI-filtered and ranked results if successful, None otherwise
        """
        try:
            with st.spinner("🤖 Analyzing jobs with AI... This may take a moment."):
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Analyzing your query with AI...")
                progress_bar.progress(20)
                
                # Perform AI search
                ai_results = ai_tagging_service.search_jobs_with_ai(jobs_df, query)
                progress_bar.progress(100)
                
                if ai_results.empty:
                    st.warning("No jobs found matching your AI search criteria. Try adjusting your query.")
                    return None
                
                # Cache results
                st.session_state[f"{self.session_key_prefix}ai_search_results"] = ai_results
                
                # Show success message with details
                avg_score = ai_results['ai_search_score'].mean()
                st.success(f"🎯 Found {len(ai_results)} relevant jobs! Average match score: {avg_score:.2f}")
                
                # Show top match reasons
                if 'ai_match_reasons' in ai_results.columns:
                    with st.expander("🔍 Why these jobs match your search", expanded=True):
                        top_job = ai_results.iloc[0]
                        st.markdown(f"**Top Match:** {top_job.get('title', 'Unknown')} at {top_job.get('company', 'Unknown')}")
                        st.markdown(f"**Match Score:** {top_job.get('ai_search_score', 0):.2f}")
                        st.markdown(f"**Reasons:** {top_job.get('ai_match_reasons', 'N/A')}")
                
                return ai_results
        
        except Exception as e:
            st.error(f"AI search failed: {str(e)}")
            return None
        
        finally:
            # Clean up progress indicators
            try:
                progress_bar.empty()
                status_text.empty()
            except:
                pass
    
    def perform_ai_tagging(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform AI tagging on all jobs with progress tracking and result display.
        
        Args:
            jobs_df: DataFrame containing job data
            
        Returns:
            pd.DataFrame: Jobs dataframe with AI tags added
        """
        try:
            # Check if jobs already have AI tags
            if 'ai_tags' in jobs_df.columns and not jobs_df['ai_tags'].isna().all():
                if not st.checkbox("🔄 Re-tag jobs that already have AI tags", key=f"{self.session_key_prefix}retag"):
                    st.info("Skipping jobs that already have AI tags. Check the box above to re-tag all jobs.")
                    return jobs_df
            
            # Verify AI service is available
            if not ai_tagging_service.is_available():
                st.error("❌ AI service is not available. Please check your OpenAI API key configuration.")
                st.info("💡 Set your OpenAI API key in environment variables: `OPENAI_API_KEY`")
                return jobs_df
            
            # Show initial info
            st.info(f"🤖 Starting AI analysis for {len(jobs_df)} jobs...")
            
            # Test API with a single job first to catch quota issues early
            if len(jobs_df) > 0:
                test_job = jobs_df.iloc[0]
                test_job_text = ai_tagging_service._prepare_job_text(test_job)
                test_result = ai_tagging_service._analyze_job_with_ai(test_job_text)
                
                if test_result is None:
                    st.error("❌ AI API test failed. Cannot proceed with tagging.")
                    st.info("📋 Common issues:")
                    st.info("• OpenAI API quota exceeded - add credits to your account")
                    st.info("• Rate limits - wait a few minutes and try again")
                    st.info("• Invalid API key - check your configuration")
                    return jobs_df
                else:
                    st.success("✅ AI API test successful. Proceeding with bulk tagging...")
            
            with st.spinner("🏷️ Adding AI tags to jobs... This will take a few minutes."):
                # Create progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(current, total):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"Processing job {current} of {total}...")
                
                # Perform AI tagging
                tagged_df = ai_tagging_service.tag_jobs(jobs_df, progress_callback)
                
                # Show completion message
                tagged_count = len(tagged_df[tagged_df['ai_tags'].notna()])
                
                if tagged_count > 0:
                    st.success(f"✅ Successfully added AI tags to {tagged_count} jobs!")
                    
                    # Show sample tags
                    with st.expander("🔍 Sample AI Analysis", expanded=True):
                        sample_job = tagged_df[tagged_df['ai_tags'].notna()].iloc[0]
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Job:** {sample_job.get('title', 'Unknown')}")
                            st.markdown(f"**Tags:** {sample_job.get('ai_tags', 'N/A')}")
                            st.markdown(f"**Category:** {sample_job.get('ai_category', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"**Skills:** {sample_job.get('ai_skills', 'N/A')}")
                            st.markdown(f"**Seniority:** {sample_job.get('ai_seniority', 'N/A')}")
                            st.markdown(f"**Score:** {sample_job.get('ai_relevance_score', 0):.2f}")
                else:
                    st.warning("⚠️ No AI tags were added. This might be due to API issues.")
                    st.info("💡 Common causes:")
                    st.info("• OpenAI API quota exceeded")
                    st.info("• Rate limiting from too many requests")
                    st.info("• Network connectivity issues")
                    st.info("• Empty or invalid job descriptions")
                
                return tagged_df
        
        except Exception as e:
            st.error(f"❌ AI tagging failed: {str(e)}")
            st.info("💡 This could be due to API rate limits, invalid API key, or network issues.")
            return jobs_df
        
        finally:
            # Clean up progress indicators
            try:
                progress_bar.empty()
                status_text.empty()
            except:
                pass
    
    def render_ai_filters(self, jobs_df: pd.DataFrame, advanced_filters: Dict[str, Any]) -> None:
        """
        Render AI-based filter controls if AI analysis data is available.
        
        Args:
            jobs_df: DataFrame containing job data
            advanced_filters: Dictionary to store filter values
        """
        # Check if AI tags are available
        has_ai_tags = 'ai_tags' in jobs_df.columns and not jobs_df['ai_tags'].isna().all()
        has_ai_categories = 'ai_category' in jobs_df.columns and not jobs_df['ai_category'].isna().all()
        has_ai_seniority = 'ai_seniority' in jobs_df.columns and not jobs_df['ai_seniority'].isna().all()
        has_ai_scores = 'ai_search_score' in jobs_df.columns and not jobs_df['ai_search_score'].isna().all()
        
        if not any([has_ai_tags, has_ai_categories, has_ai_seniority, has_ai_scores]):
            st.info("🤖 No AI analysis available. Use 'Add AI Tags' or 'AI Search' above to enable AI filters.")
            return
        
        st.markdown("**🤖 AI-Based Filters**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # AI Category filter
            if has_ai_categories:
                categories = ['All'] + sorted(jobs_df['ai_category'].dropna().unique().tolist())
                advanced_filters['ai_category'] = st.selectbox(
                    "🎯 AI Job Category",
                    categories,
                    key=f"{self.session_key_prefix}ai_category",
                    help="Categories determined by AI analysis"
                )
            
            # AI Seniority filter
            if has_ai_seniority:
                seniority_levels = ['All'] + sorted(jobs_df['ai_seniority'].dropna().unique().tolist())
                advanced_filters['ai_seniority'] = st.selectbox(
                    "📊 AI Seniority Level",
                    seniority_levels,
                    key=f"{self.session_key_prefix}ai_seniority",
                    help="Seniority levels determined by AI analysis"
                )
        
        with col2:
            # AI Relevance Score filter (if from AI search)
            if has_ai_scores:
                score_df = jobs_df[jobs_df['ai_search_score'].notna()]
                if len(score_df) > 0:
                    min_score = float(score_df['ai_search_score'].min())
                    max_score = float(score_df['ai_search_score'].max())
                    
                    advanced_filters['min_ai_score'] = st.slider(
                        "🎯 Minimum AI Match Score",
                        min_value=min_score,
                        max_value=max_score,
                        value=min_score,
                        step=0.05,
                        key=f"{self.session_key_prefix}min_ai_score",
                        help="Filter by AI-calculated relevance score"
                    )
            
            # AI Tags search
            if has_ai_tags:
                advanced_filters['ai_tags_search'] = st.text_input(
                    "🏷️ Search AI Tags",
                    placeholder="e.g., machine-learning, senior, startup",
                    key=f"{self.session_key_prefix}ai_tags_search",
                    help="Search within AI-generated tags"
                )
    
    def apply_ai_filters(self, filtered_df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply AI-based filters to the dataframe.
        
        Args:
            filtered_df: DataFrame to filter
            filters: Dictionary containing filter criteria
            
        Returns:
            pd.DataFrame: Filtered dataframe
        """
        # AI Category filter
        if filters.get('ai_category') and filters['ai_category'] != 'All' and 'ai_category' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['ai_category'] == filters['ai_category']]
        
        # AI Seniority filter
        if filters.get('ai_seniority') and filters['ai_seniority'] != 'All' and 'ai_seniority' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['ai_seniority'] == filters['ai_seniority']]
        
        # AI Score filter
        if 'min_ai_score' in filters and 'ai_search_score' in filtered_df.columns:
            score_mask = filtered_df['ai_search_score'] >= filters['min_ai_score']
            filtered_df = filtered_df[score_mask]
        
        # AI Tags search filter
        if filters.get('ai_tags_search') and 'ai_tags' in filtered_df.columns:
            tags_mask = filtered_df['ai_tags'].str.contains(
                filters['ai_tags_search'], case=False, na=False
            )
            filtered_df = filtered_df[tags_mask]
        
        return filtered_df
    
    def has_ai_data(self, jobs_df: pd.DataFrame) -> Dict[str, bool]:
        """
        Check what types of AI data are available in the dataframe.
        
        Args:
            jobs_df: DataFrame to check
            
        Returns:
            Dict[str, bool]: Dictionary indicating what AI data is available
        """
        return {
            'tags': 'ai_tags' in jobs_df.columns and not jobs_df['ai_tags'].isna().all(),
            'categories': 'ai_category' in jobs_df.columns and not jobs_df['ai_category'].isna().all(),
            'seniority': 'ai_seniority' in jobs_df.columns and not jobs_df['ai_seniority'].isna().all(),
            'scores': 'ai_search_score' in jobs_df.columns and not jobs_df['ai_search_score'].isna().all(),
            'skills': 'ai_skills' in jobs_df.columns and not jobs_df['ai_skills'].isna().all(),
            'match_reasons': 'ai_match_reasons' in jobs_df.columns and not jobs_df['ai_match_reasons'].isna().all()
        }
    
    def clear_ai_cache(self) -> None:
        """Clear all AI-related cached data from session state."""
        keys_to_clear = [
            f"{self.session_key_prefix}ai_search_results",
            f"{self.session_key_prefix}ai_query",
            f"{self.session_key_prefix}retag"
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_ai_summary_stats(self, jobs_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics about AI analysis in the dataframe.
        
        Args:
            jobs_df: DataFrame to analyze
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        ai_data = self.has_ai_data(jobs_df)
        stats = {
            'total_jobs': len(jobs_df),
            'tagged_jobs': 0,
            'categorized_jobs': 0,
            'scored_jobs': 0,
            'avg_score': 0.0,
            'categories': [],
            'seniority_levels': []
        }
        
        if ai_data['tags']:
            stats['tagged_jobs'] = len(jobs_df[jobs_df['ai_tags'].notna()])
        
        if ai_data['categories']:
            stats['categorized_jobs'] = len(jobs_df[jobs_df['ai_category'].notna()])
            stats['categories'] = jobs_df['ai_category'].dropna().unique().tolist()
        
        if ai_data['scores']:
            score_df = jobs_df[jobs_df['ai_search_score'].notna()]
            stats['scored_jobs'] = len(score_df)
            if len(score_df) > 0:
                stats['avg_score'] = float(score_df['ai_search_score'].mean())
        
        if ai_data['seniority']:
            stats['seniority_levels'] = jobs_df['ai_seniority'].dropna().unique().tolist()
        
        return stats
