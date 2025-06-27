"""
LLM Memory System - Core Library

A simple system for managing LLM memory through text-based storage
and automated conversation analysis.
"""

__version__ = "1.0.0"
__author__ = "LLM Memory System"

# Import handling for the memory system
try:
    from .memory_manager import MemoryManager
    from .log_processor import LogProcessor
    from .claude_client import ClaudeClient
    __all__ = ["MemoryManager", "LogProcessor", "ClaudeClient"]
except ImportError:
    # Handle case where dependencies aren't installed
    __all__ = []
