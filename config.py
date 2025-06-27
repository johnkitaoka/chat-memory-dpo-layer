"""
Configuration settings for the LLM Memory System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-3-5-haiku-20241022"  # Claude 3.5 Haiku
CLAUDE_MAX_TOKENS = 4000
CLAUDE_TEMPERATURE = 0.1

# File Paths
MEMORY_FILE = BASE_DIR / "memory.txt"
PROMPTS_FILE = BASE_DIR / "prompts.yaml"
LOGS_DIR = BASE_DIR / "logs"
SCRIPTS_DIR = BASE_DIR / "scripts"
SRC_DIR = BASE_DIR / "src"

# Log Processing Settings
DEFAULT_LOG_DAYS = 7  # Process logs from last N days by default
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LINE_PATTERN = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (USER|ASSISTANT): (.*)'

# Memory Processing Settings
MIN_CONVERSATION_LENGTH = 3  # Minimum exchanges to consider for memory updates
MAX_LOG_CHARS = 50000  # Maximum characters to send to Claude at once

# Default Memory Template
DEFAULT_MEMORY_TEMPLATE = """USER PROFILE
===========

COMMUNICATION STYLE:
- [To be determined from conversations]

INTERESTS:
- [To be determined from conversations]

PREFERENCES:
- [To be determined from conversations]

CONTEXT:
- [To be determined from conversations]

TECHNICAL BACKGROUND:
- [To be determined from conversations]

RESPONSE FORMAT PREFERENCES:
- [To be determined from conversations]
"""

# Validation Settings
REQUIRED_ENV_VARS = ["ANTHROPIC_API_KEY"]

def validate_config():
    """Validate that all required configuration is present"""
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [LOGS_DIR, SCRIPTS_DIR, SRC_DIR]
    for directory in directories:
        directory.mkdir(exist_ok=True)
    
    return True
