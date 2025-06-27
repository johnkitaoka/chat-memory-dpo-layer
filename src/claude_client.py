"""
Claude Client for LLM Memory System

Handles communication with Anthropic's Claude API for memory analysis and updates.
"""

import os
import logging
from typing import Optional, Dict, Any
from anthropic import Anthropic
from anthropic.types import Message

import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    CLAUDE_MAX_TOKENS,
    CLAUDE_TEMPERATURE
)

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with Anthropic's Claude API"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Claude client
        
        Args:
            api_key: Anthropic API key (defaults to config)
            model: Claude model to use (defaults to config)
        """
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.model = model or CLAUDE_MODEL
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
        
        self.client = Anthropic(api_key=self.api_key)
        logger.info(f"Initialized Claude client with model: {self.model}")
    
    def analyze_conversation(self, logs: str, current_memory: str, prompt_template: str) -> str:
        """
        Analyze conversation logs and propose memory amendments
        
        Args:
            logs: Formatted conversation logs
            current_memory: Current memory file content
            prompt_template: Prompt template with placeholders
            
        Returns:
            Claude's response with analysis and proposed amendments
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Format the prompt with logs and memory
            formatted_prompt = prompt_template.replace("{{LOGS}}", logs)
            formatted_prompt = formatted_prompt.replace("{{MEMORY}}", current_memory)
            
            logger.info(f"Sending analysis request to Claude ({self.model})")
            logger.debug(f"Prompt length: {len(formatted_prompt)} characters")
            
            # Make API call to Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=CLAUDE_MAX_TOKENS,
                temperature=CLAUDE_TEMPERATURE,
                messages=[
                    {
                        "role": "user",
                        "content": formatted_prompt
                    }
                ]
            )
            
            # Extract response text
            response_text = response.content[0].text
            
            logger.info("Successfully received response from Claude")
            logger.debug(f"Response length: {len(response_text)} characters")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Failed to analyze conversation with Claude: {str(e)}")
            raise Exception(f"Claude API error: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test connection to Claude API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ]
            )
            
            logger.info("Claude API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Claude API connection test failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration
        
        Returns:
            Dictionary with model configuration details
        """
        return {
            "model": self.model,
            "max_tokens": CLAUDE_MAX_TOKENS,
            "temperature": CLAUDE_TEMPERATURE,
            "api_key_configured": bool(self.api_key)
        }
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of token count for text
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count (rough approximation)
        """
        # Rough approximation: ~4 characters per token for English text
        return len(text) // 4
    
    def validate_request_size(self, logs: str, memory: str, prompt_template: str) -> bool:
        """
        Validate that the request size is within Claude's limits
        
        Args:
            logs: Conversation logs
            memory: Current memory content
            prompt_template: Prompt template
            
        Returns:
            True if request size is acceptable, False otherwise
        """
        total_text = logs + memory + prompt_template
        estimated_tokens = self.estimate_tokens(total_text)
        
        # Claude 3.5 Haiku has a 200k token context window
        # Leave room for response tokens
        max_input_tokens = 190000
        
        if estimated_tokens > max_input_tokens:
            logger.warning(f"Request size ({estimated_tokens} tokens) exceeds recommended limit")
            return False
        
        logger.debug(f"Request size validation passed: {estimated_tokens} tokens")
        return True
