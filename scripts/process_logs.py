#!/usr/bin/env python3
"""
Process Chat Logs Script

Main script for processing chat logs and updating memory using Claude analysis.
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.claude_client import ClaudeClient
from src.memory_manager import MemoryManager
from src.log_processor import LogProcessor
from config import validate_config, ensure_directories


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('memory_processing.log')
        ]
    )


def main():
    """Main function for processing logs and updating memory"""
    parser = argparse.ArgumentParser(
        description="Process chat logs and update memory using Claude analysis"
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Specific log file to process (e.g., sample_chat.log)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back for logs (default: 7)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without actually updating memory'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force processing even if no significant changes detected'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        logger.info("Starting memory processing...")
        validate_config()
        ensure_directories()
        
        # Initialize components
        claude_client = ClaudeClient()
        memory_manager = MemoryManager()
        log_processor = LogProcessor()
        
        # Test Claude connection
        logger.info("Testing Claude API connection...")
        if not claude_client.test_connection():
            logger.error("Failed to connect to Claude API")
            return 1
        
        # Load current memory
        logger.info("Loading current memory...")
        current_memory = memory_manager.load_memory()
        logger.info(f"Current memory: {len(current_memory)} characters")
        
        # Get logs to process
        if args.log_file:
            logger.info(f"Processing specific log file: {args.log_file}")
            entries = log_processor.get_logs_by_file(args.log_file)
        else:
            logger.info(f"Processing logs from last {args.days} days")
            entries = log_processor.get_recent_logs(args.days)
        
        if not entries:
            logger.warning("No log entries found to process")
            return 0
        
        logger.info(f"Found {len(entries)} log entries to analyze")
        
        # Analyze logs with Claude
        logger.info("Sending logs to Claude for analysis...")
        analysis_response = log_processor.analyze_logs(
            entries=entries,
            current_memory=current_memory,
            claude_client=claude_client
        )
        
        logger.info("Received analysis from Claude")
        
        # Extract amendments from Claude's response
        amendments = memory_manager.extract_amendments(analysis_response)
        
        if not amendments:
            logger.info("No memory amendments suggested by Claude")
            print("\n=== Claude Analysis ===")
            print(analysis_response)
            return 0
        
        logger.info(f"Claude suggested {len(amendments)} amendments")
        
        # Show what would be changed
        print("\n=== Proposed Memory Amendments ===")
        for i, (search_text, replace_text) in enumerate(amendments, 1):
            print(f"\nAmendment {i}:")
            print(f"SEARCH: {search_text[:100]}{'...' if len(search_text) > 100 else ''}")
            print(f"REPLACE: {replace_text[:100]}{'...' if len(replace_text) > 100 else ''}")
        
        print(f"\n=== Full Claude Analysis ===")
        print(analysis_response)
        
        # Apply amendments if not dry run
        if args.dry_run:
            logger.info("Dry run mode - no changes applied")
            print("\n[DRY RUN] No changes were applied to memory file")
        else:
            # Confirm before applying changes
            if not args.force:
                response = input(f"\nApply {len(amendments)} amendments to memory? (y/N): ")
                if response.lower() != 'y':
                    logger.info("User cancelled memory update")
                    return 0
            
            # Apply amendments
            logger.info("Applying amendments to memory...")
            success = memory_manager.apply_amendments(amendments)
            
            if success:
                logger.info("Successfully updated memory file")
                print(f"\n✓ Applied {len(amendments)} amendments to memory file")
                
                # Show updated memory stats
                stats = memory_manager.get_memory_stats()
                print(f"✓ Memory file updated: {stats['character_count']} characters")
            else:
                logger.error("Failed to apply some amendments")
                print("\n✗ Some amendments could not be applied")
                return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
