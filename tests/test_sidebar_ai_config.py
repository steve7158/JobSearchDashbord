#!/usr/bin/env python3
"""
Test script for AI configuration in sidebar
"""

import streamlit as st
from UI.ui_sidebar import JobSearchSidebar
from services.ai_service import ai_service

def mock_job_service(email=None, password=None):
    """Mock job service for testing"""
    return {'status': 'mock_service', 'email': email}

def test_ai_configuration():
    """Test AI configuration functionality"""
    print("🧪 Testing AI Configuration in Sidebar")
    print("=" * 50)
    
    # Test provider info
    info = ai_service.get_provider_info()
    print(f"Current Provider: {info['current_provider']}")
    print(f"Current Model: {info['current_model']}")
    print(f"Available Providers: {info['available_providers']}")
    print(f"Available Models: {info['available_models']}")
    
    # Test provider switching
    print("\n🔄 Testing Provider Switching:")
    
    # Test setting OpenAI with different model
    if 'openai' in info['available_providers']:
        openai_models = ai_service.get_available_models('openai')
        if len(openai_models) > 1:
            test_model = openai_models[1]  # Get second model
            success = ai_service.set_provider('openai', test_model)
            print(f"   Switch to OpenAI {test_model}: {'✅' if success else '❌'}")
    
    # Test setting Groq if available
    if 'groq' in info['available_providers']:
        groq_models = ai_service.get_available_models('groq')
        if groq_models:
            test_model = groq_models[0]
            success = ai_service.set_provider('groq', test_model)
            print(f"   Switch to Groq {test_model}: {'✅' if success else '❌'}")
    
    # Test sidebar creation
    print("\n🎛️ Testing Sidebar:")
    sidebar = JobSearchSidebar(mock_job_service)
    print("   ✅ Sidebar created successfully")
    
    # Test AI status
    print(f"\n🤖 AI Service Available: {'✅' if ai_service.is_available() else '❌'}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_ai_configuration()
