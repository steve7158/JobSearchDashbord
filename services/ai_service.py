"""
Unified AI Service for OpenAI, Groq, and Llama models.

This service provides a unified interface for different AI providers:
- OpenAI (GPT models)
- Groq (Fast inference)
- Llama (Open source models)
"""

import os
import json
import streamlit as st
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self) -> None:
        """Initialize the AI client."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available."""
        pass
    
    @abstractmethod
    def generate_completion(self, messages: List[Dict[str, str]], 
                          max_tokens: int = 300, 
                          temperature: float = 0.3,
                          model: Optional[str] = None) -> Optional[str]:
        """Generate completion from messages."""
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Get the default model for this provider."""
        pass
    
    @abstractmethod
    def get_chatcompletion(self, prompt: str, 
                          max_tokens: int = 300, 
                          temperature: float = 0.3,
                          model: Optional[str] = None) -> Optional[str]:
        """Get chat completion with a simple prompt."""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        super().__init__(self.api_key)
    
    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                st.warning("OpenAI library not installed. Run: pip install openai")
                self.client = None
            except Exception as e:
                st.warning(f"OpenAI initialization failed: {str(e)}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.api_key is not None and self.client is not None
    
    def generate_completion(self, messages: List[Dict[str, str]], 
                          max_tokens: int = 300, 
                          temperature: float = 0.3,
                          model: Optional[str] = None) -> Optional[str]:
        """Generate completion using OpenAI."""
        if not self.is_available():
            return None
        
        try:
            model = model or self.get_default_model()
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.warning(f"OpenAI API call failed: {str(e)}")
            return None
    
    def get_default_model(self) -> str:
        """Get default OpenAI model."""
        return "gpt-3.5-turbo"
    
    def get_chatcompletion(self, prompt: str, 
                          max_tokens: int = 300, 
                          temperature: float = 0.3,
                          model: Optional[str] = None) -> Optional[str]:
        """
        Get chat completion from OpenAI with a simple prompt.
        
        Args:
            prompt: User prompt/question
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0 to 1.0)
            model: Model to use (optional, uses default if not specified)
            
        Returns:
            AI response as string or None if failed
        """
        if not self.is_available():
            return None
        
        messages = [{"role": "user", "content": prompt}]
        return self.generate_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model
        )
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        return [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-4o",
            "gpt-4o-mini"
        ]


class GroqProvider(BaseAIProvider):
    """Groq API provider for fast inference with Llama and other models."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        super().__init__(self.api_key)
    
    def _initialize_client(self) -> None:
        """Initialize Groq client."""
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except ImportError:
                st.warning("Groq library not installed. Run: pip install groq")
                self.client = None
            except Exception as e:
                st.warning(f"Groq initialization failed: {str(e)}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if Groq is available."""
        return self.api_key is not None and self.client is not None
    
    def generate_completion(self, messages: List[Dict[str, str]], 
                          max_tokens: int = 300, 
                          temperature: float = 0.3,
                          model: Optional[str] = None) -> Optional[str]:
        """Generate completion using Groq."""
        if not self.is_available():
            return None
        
        try:
            model = model or self.get_default_model()
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.warning(f"Groq API call failed: {str(e)}")
            return None
    
    def get_default_model(self) -> str:
        """Get default Groq model."""
        return "llama3-8b-8192"
    
    def get_chatcompletion(self, prompt: str, 
                          max_tokens: int = 300, 
                          temperature: float = 0.3,
                          model: Optional[str] = None) -> Optional[str]:
        """
        Get chat completion from Groq with a simple prompt.
        
        Args:
            prompt: User prompt/question
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0 to 1.0)
            model: Model to use (optional, uses default if not specified)
            
        Returns:
            AI response as string or None if failed
        """
        if not self.is_available():
            return None
        
        messages = [{"role": "user", "content": prompt}]
        return self.generate_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model
        )
    
    def get_available_models(self) -> List[str]:
        """Get available Groq models (includes Llama, Mixtral, Gemma)."""
        return [
            # Llama models (fast and efficient)
            "llama3-8b-8192",
            "llama3-70b-8192",
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "llama-3.1-405b-reasoning",
            
            # Mixtral models (good for complex tasks)
            "mixtral-8x7b-32768",
            
            # Gemma models (Google's open models)
            "gemma-7b-it",
            "gemma2-9b-it"
        ]


class UnifiedAIService:
    """
    Unified AI service that manages OpenAI and Groq providers.
    Automatically falls back to available providers.
    """
    
    def __init__(self):
        """Initialize the unified AI service."""
        self.providers = {}
        self.current_provider = None
        self.current_model = None
        self._initialize_providers()
        self._select_best_provider()
    
    def _initialize_providers(self) -> None:
        """Initialize available AI providers."""
        # Initialize OpenAI
        openai_provider = OpenAIProvider()
        if openai_provider.is_available():
            self.providers['openai'] = openai_provider
        
        # Initialize Groq (includes Llama models)
        groq_provider = GroqProvider()
        if groq_provider.is_available():
            self.providers['groq'] = groq_provider
    
    def _select_best_provider(self) -> None:
        """Select the best available provider."""
        # Priority order: OpenAI > Groq
        if 'openai' in self.providers:
            self.current_provider = 'openai'
        elif 'groq' in self.providers:
            self.current_provider = 'groq'
        else:
            self.current_provider = None
        
        if self.current_provider:
            self.current_model = self.providers[self.current_provider].get_default_model()
    
    def is_available(self) -> bool:
        """Check if any AI provider is available."""
        return len(self.providers) > 0 and self.current_provider is not None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.providers.keys())
    
    def get_current_provider(self) -> Optional[str]:
        """Get current active provider."""
        return self.current_provider
    
    def set_provider(self, provider_name: str, model: Optional[str] = None) -> bool:
        """Set the active provider and model."""
        if provider_name in self.providers:
            self.current_provider = provider_name
            self.current_model = model or self.providers[provider_name].get_default_model()
            return True
        return False
    
    def get_available_models(self, provider_name: Optional[str] = None) -> List[str]:
        """Get available models for a provider."""
        provider = provider_name or self.current_provider
        if provider in self.providers:
            return self.providers[provider].get_available_models()
        return []
    
    def generate_completion(self, messages: List[Dict[str, str]], 
                          max_tokens: int = 300, 
                          temperature: float = 0.3,
                          model: Optional[str] = None) -> Optional[str]:
        """Generate completion using the current provider."""
        if not self.is_available():
            return None
        
        provider = self.providers[self.current_provider]
        model = model or self.current_model
        
        return provider.generate_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model
        )
    
    def get_chatcompletion(self, prompt: str, 
                          max_tokens: int = 300, 
                          temperature: float = 0.3,
                          model: Optional[str] = None) -> Optional[str]:
        """
        Get chat completion using the current provider with a simple prompt.
        
        Args:
            prompt: User prompt/question
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0 to 1.0)
            model: Model to use (optional, uses current model if not specified)
            
        Returns:
            AI response as string or None if failed
        """
        if not self.is_available():
            return None
        
        provider = self.providers[self.current_provider]
        return provider.get_chatcompletion(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model or self.current_model
        )
    
    def generate_json_completion(self, prompt: str, 
                               max_tokens: int = 300, 
                               temperature: float = 0.3) -> Optional[Dict[str, Any]]:
        """Generate JSON completion with automatic parsing."""
        messages = [{"role": "user", "content": prompt}]
        response = self.generate_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if not response:
            return None
        
        # Try to parse JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_content = response[json_start:json_end].strip()
                return json.loads(json_content)
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_content = response[json_start:json_end].strip()
                return json.loads(json_content)
            else:
                st.warning(f"Could not parse JSON response: {response[:100]}...")
                return None
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current provider and available options."""
        return {
            'current_provider': self.current_provider,
            'current_model': self.current_model,
            'available_providers': self.get_available_providers(),
            'available_models': self.get_available_models(),
            'total_providers': len(self.providers)
        }


# Global unified AI service instance
ai_service = UnifiedAIService()
