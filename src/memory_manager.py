"""
Memory Manager for LLM Memory System

Handles loading, saving, and updating the memory file with diff-based amendments.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MEMORY_FILE, DEFAULT_MEMORY_TEMPLATE

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages the memory file and applies amendments"""
    
    def __init__(self, memory_file: Optional[Path] = None):
        """
        Initialize memory manager
        
        Args:
            memory_file: Path to memory file (defaults to config)
        """
        self.memory_file = memory_file or MEMORY_FILE
        logger.info(f"Initialized MemoryManager with file: {self.memory_file}")
    
    def load_memory(self) -> str:
        """
        Load current memory from file
        
        Returns:
            Memory file content as string
            
        Raises:
            FileNotFoundError: If memory file doesn't exist
        """
        try:
            if not self.memory_file.exists():
                logger.warning(f"Memory file not found: {self.memory_file}")
                return DEFAULT_MEMORY_TEMPLATE
            
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Loaded memory file ({len(content)} characters)")
            return content
            
        except Exception as e:
            logger.error(f"Failed to load memory file: {str(e)}")
            raise
    
    def save_memory(self, content: str) -> None:
        """
        Save memory content to file
        
        Args:
            content: Memory content to save
            
        Raises:
            Exception: If save operation fails
        """
        try:
            # Ensure directory exists
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup of existing file
            if self.memory_file.exists():
                backup_path = self.memory_file.with_suffix('.txt.backup')
                self.memory_file.rename(backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Save new content
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved memory file ({len(content)} characters)")
            
        except Exception as e:
            logger.error(f"Failed to save memory file: {str(e)}")
            raise
    
    def extract_amendments(self, claude_response: str) -> List[Tuple[str, str]]:
        """
        Extract diff-fenced amendments from Claude's response
        
        Args:
            claude_response: Claude's response containing analysis and amendments
            
        Returns:
            List of (search_text, replace_text) tuples
        """
        amendments = []
        
        # Pattern to match diff-fenced blocks
        pattern = r'<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE'
        matches = re.findall(pattern, claude_response, re.DOTALL)
        
        for search_text, replace_text in matches:
            # Clean up whitespace
            search_text = search_text.strip()
            replace_text = replace_text.strip()
            
            amendments.append((search_text, replace_text))
            logger.debug(f"Extracted amendment: {len(search_text)} -> {len(replace_text)} chars")
        
        logger.info(f"Extracted {len(amendments)} amendments from Claude response")
        return amendments
    
    def apply_amendments(self, amendments: List[Tuple[str, str]]) -> bool:
        """
        Apply amendments to the memory file
        
        Args:
            amendments: List of (search_text, replace_text) tuples
            
        Returns:
            True if all amendments applied successfully, False otherwise
        """
        if not amendments:
            logger.info("No amendments to apply")
            return True
        
        try:
            # Load current memory
            current_memory = self.load_memory()
            updated_memory = current_memory
            
            # Apply each amendment
            applied_count = 0
            for i, (search_text, replace_text) in enumerate(amendments):
                if search_text in updated_memory:
                    updated_memory = updated_memory.replace(search_text, replace_text, 1)
                    applied_count += 1
                    logger.debug(f"Applied amendment {i+1}/{len(amendments)}")
                else:
                    logger.warning(f"Amendment {i+1} search text not found in memory")
            
            # Save updated memory if changes were made
            if applied_count > 0:
                self.save_memory(updated_memory)
                logger.info(f"Successfully applied {applied_count}/{len(amendments)} amendments")
                return True
            else:
                logger.warning("No amendments could be applied")
                return False
                
        except Exception as e:
            logger.error(f"Failed to apply amendments: {str(e)}")
            return False
    
    def get_context_for_prompt(self) -> str:
        """
        Get formatted memory content for use in LLM prompts
        
        Returns:
            Formatted memory content suitable for prompt injection
        """
        try:
            memory_content = self.load_memory()
            
            # Format for prompt injection
            formatted_context = f"""
# User Context

Based on previous interactions, here's what I know about you:

{memory_content}

---

I'll use this context to provide more personalized and relevant responses.
"""
            
            return formatted_context.strip()
            
        except Exception as e:
            logger.error(f"Failed to get context for prompt: {str(e)}")
            return "# User Context\n\nNo previous context available."
    
    def validate_memory_format(self, content: str) -> bool:
        """
        Validate that memory content follows expected format
        
        Args:
            content: Memory content to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        required_sections = [
            "USER PROFILE",
            "COMMUNICATION STYLE:",
            "INTERESTS:",
            "PREFERENCES:",
            "CONTEXT:"
        ]
        
        for section in required_sections:
            if section not in content:
                logger.warning(f"Memory validation failed: missing section '{section}'")
                return False
        
        logger.debug("Memory format validation passed")
        return True
    
    def get_memory_stats(self) -> dict:
        """
        Get statistics about the current memory file
        
        Returns:
            Dictionary with memory file statistics
        """
        try:
            if not self.memory_file.exists():
                return {"exists": False}
            
            content = self.load_memory()
            
            stats = {
                "exists": True,
                "file_size": self.memory_file.stat().st_size,
                "character_count": len(content),
                "line_count": len(content.splitlines()),
                "last_modified": datetime.fromtimestamp(
                    self.memory_file.stat().st_mtime
                ).isoformat(),
                "valid_format": self.validate_memory_format(content)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {str(e)}")
            return {"exists": False, "error": str(e)}
    
    def create_initial_memory(self) -> None:
        """
        Create initial memory file with default template
        """
        try:
            if self.memory_file.exists():
                logger.info("Memory file already exists, skipping initialization")
                return
            
            self.save_memory(DEFAULT_MEMORY_TEMPLATE)
            logger.info("Created initial memory file with default template")
            
        except Exception as e:
            logger.error(f"Failed to create initial memory: {str(e)}")
            raise
