"""
Log Processor for LLM Memory System

Handles parsing and processing of chat log files for memory analysis.
"""

import re
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import yaml

import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    LOGS_DIR,
    PROMPTS_FILE,
    LOG_DATE_FORMAT,
    LOG_LINE_PATTERN,
    DEFAULT_LOG_DAYS,
    MIN_CONVERSATION_LENGTH,
    MAX_LOG_CHARS
)

logger = logging.getLogger(__name__)


class LogProcessor:
    """Processes chat logs for memory analysis"""
    
    def __init__(self, logs_dir: Optional[Path] = None, prompts_file: Optional[Path] = None):
        """
        Initialize log processor
        
        Args:
            logs_dir: Directory containing log files (defaults to config)
            prompts_file: Path to prompts YAML file (defaults to config)
        """
        self.logs_dir = logs_dir or LOGS_DIR
        self.prompts_file = prompts_file or PROMPTS_FILE
        
        # Load prompts
        self.prompts = self._load_prompts()
        
        logger.info(f"Initialized LogProcessor with logs_dir: {self.logs_dir}")
    
    def _load_prompts(self) -> Dict[str, str]:
        """
        Load prompts from YAML file
        
        Returns:
            Dictionary of prompt templates
        """
        try:
            if not self.prompts_file.exists():
                logger.error(f"Prompts file not found: {self.prompts_file}")
                return {}
            
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                prompts = yaml.safe_load(f)
            
            logger.info(f"Loaded {len(prompts)} prompts from {self.prompts_file}")
            return prompts
            
        except Exception as e:
            logger.error(f"Failed to load prompts: {str(e)}")
            return {}
    
    def parse_log_file(self, log_file: Path) -> List[Dict[str, str]]:
        """
        Parse a single log file into structured conversation data
        
        Args:
            log_file: Path to log file
            
        Returns:
            List of conversation entries with timestamp, role, and content
        """
        try:
            if not log_file.exists():
                logger.error(f"Log file not found: {log_file}")
                return []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse log entries using regex
            pattern = LOG_LINE_PATTERN
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            
            entries = []
            for timestamp_str, role, message in matches:
                try:
                    timestamp = datetime.strptime(timestamp_str, LOG_DATE_FORMAT)
                    entries.append({
                        'timestamp': timestamp,
                        'role': role.upper(),
                        'content': message.strip()
                    })
                except ValueError as e:
                    logger.warning(f"Failed to parse timestamp '{timestamp_str}': {e}")
                    continue
            
            logger.info(f"Parsed {len(entries)} entries from {log_file}")
            return entries
            
        except Exception as e:
            logger.error(f"Failed to parse log file {log_file}: {str(e)}")
            return []
    
    def get_recent_logs(self, days: int = DEFAULT_LOG_DAYS) -> List[Dict[str, str]]:
        """
        Get log entries from the last N days
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent conversation entries
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        all_entries = []
        
        # Process all log files in the directory
        if not self.logs_dir.exists():
            logger.warning(f"Logs directory not found: {self.logs_dir}")
            return []
        
        log_files = list(self.logs_dir.glob("*.log"))
        logger.info(f"Found {len(log_files)} log files")
        
        for log_file in log_files:
            entries = self.parse_log_file(log_file)
            
            # Filter by date
            recent_entries = [
                entry for entry in entries 
                if entry['timestamp'] >= cutoff_date
            ]
            
            all_entries.extend(recent_entries)
        
        # Sort by timestamp
        all_entries.sort(key=lambda x: x['timestamp'])
        
        logger.info(f"Found {len(all_entries)} recent entries from last {days} days")
        return all_entries
    
    def get_logs_by_file(self, filename: str) -> List[Dict[str, str]]:
        """
        Get logs from a specific file
        
        Args:
            filename: Name of the log file
            
        Returns:
            List of conversation entries from the file
        """
        log_file = self.logs_dir / filename
        return self.parse_log_file(log_file)
    
    def format_logs_for_analysis(self, entries: List[Dict[str, str]]) -> str:
        """
        Format log entries for Claude analysis
        
        Args:
            entries: List of conversation entries
            
        Returns:
            Formatted string suitable for Claude analysis
        """
        if not entries:
            return "No conversation logs provided."
        
        # Group entries into conversations (sessions)
        conversations = self._group_into_conversations(entries)
        
        formatted_logs = []
        for i, conversation in enumerate(conversations, 1):
            if len(conversation) < MIN_CONVERSATION_LENGTH:
                continue  # Skip very short conversations
            
            formatted_logs.append(f"=== Conversation {i} ===")
            formatted_logs.append(f"Date: {conversation[0]['timestamp'].strftime('%Y-%m-%d')}")
            formatted_logs.append(f"Duration: {len(conversation)} exchanges")
            formatted_logs.append("")
            
            for entry in conversation:
                timestamp = entry['timestamp'].strftime('%H:%M:%S')
                role = entry['role']
                content = entry['content']
                
                # Truncate very long messages
                if len(content) > 1000:
                    content = content[:1000] + "... [truncated]"
                
                formatted_logs.append(f"[{timestamp}] {role}: {content}")
            
            formatted_logs.append("")
        
        result = "\n".join(formatted_logs)
        
        # Ensure we don't exceed Claude's context limits
        if len(result) > MAX_LOG_CHARS:
            logger.warning(f"Formatted logs ({len(result)} chars) exceed limit, truncating")
            result = result[:MAX_LOG_CHARS] + "\n\n[Logs truncated due to length]"
        
        logger.info(f"Formatted {len(conversations)} conversations for analysis")
        return result
    
    def _group_into_conversations(self, entries: List[Dict[str, str]]) -> List[List[Dict[str, str]]]:
        """
        Group log entries into conversation sessions
        
        Args:
            entries: List of conversation entries
            
        Returns:
            List of conversation sessions (each session is a list of entries)
        """
        if not entries:
            return []
        
        conversations = []
        current_conversation = []
        
        for entry in entries:
            # Start new conversation if there's a large time gap (>1 hour)
            if (current_conversation and 
                entry['timestamp'] - current_conversation[-1]['timestamp'] > timedelta(hours=1)):
                
                if current_conversation:
                    conversations.append(current_conversation)
                current_conversation = [entry]
            else:
                current_conversation.append(entry)
        
        # Add the last conversation
        if current_conversation:
            conversations.append(current_conversation)
        
        return conversations
    
    def analyze_logs(self, entries: List[Dict[str, str]], current_memory: str, claude_client) -> str:
        """
        Analyze logs using Claude and get memory amendments
        
        Args:
            entries: List of conversation entries
            current_memory: Current memory content
            claude_client: Initialized Claude client
            
        Returns:
            Claude's analysis response
        """
        try:
            # Get the augment-memory prompt
            if 'augment-memory' not in self.prompts:
                raise ValueError("augment-memory prompt not found in prompts file")
            
            prompt_template = self.prompts['augment-memory']
            
            # Format logs for analysis
            formatted_logs = self.format_logs_for_analysis(entries)
            
            # Validate request size
            if not claude_client.validate_request_size(formatted_logs, current_memory, prompt_template):
                logger.warning("Request size too large, truncating logs")
                # Truncate logs if too large
                formatted_logs = formatted_logs[:MAX_LOG_CHARS//2]
            
            # Send to Claude for analysis
            response = claude_client.analyze_conversation(
                logs=formatted_logs,
                current_memory=current_memory,
                prompt_template=prompt_template
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to analyze logs: {str(e)}")
            raise
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        Get statistics about available log files
        
        Returns:
            Dictionary with log file statistics
        """
        try:
            if not self.logs_dir.exists():
                return {"logs_dir_exists": False}
            
            log_files = list(self.logs_dir.glob("*.log"))
            total_entries = 0
            date_range = {"earliest": None, "latest": None}
            
            for log_file in log_files:
                entries = self.parse_log_file(log_file)
                total_entries += len(entries)
                
                if entries:
                    file_earliest = min(entry['timestamp'] for entry in entries)
                    file_latest = max(entry['timestamp'] for entry in entries)
                    
                    if date_range["earliest"] is None or file_earliest < date_range["earliest"]:
                        date_range["earliest"] = file_earliest
                    
                    if date_range["latest"] is None or file_latest > date_range["latest"]:
                        date_range["latest"] = file_latest
            
            return {
                "logs_dir_exists": True,
                "log_file_count": len(log_files),
                "total_entries": total_entries,
                "date_range": {
                    "earliest": date_range["earliest"].isoformat() if date_range["earliest"] else None,
                    "latest": date_range["latest"].isoformat() if date_range["latest"] else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get log stats: {str(e)}")
            return {"error": str(e)}
