#!/usr/bin/env python3
"""
Initialize Memory System

Script to set up the memory system with initial configuration and validation.
"""

import sys
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.claude_client import ClaudeClient
from src.memory_manager import MemoryManager
from src.log_processor import LogProcessor
from config import validate_config, ensure_directories


def setup_logging() -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    """Initialize the memory system"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🧠 LLM Memory System Initialization")
    print("=" * 40)
    
    try:
        # Step 1: Validate configuration
        print("\n1. Validating configuration...")
        try:
            validate_config()
            print("   ✓ Configuration valid")
        except ValueError as e:
            print(f"   ✗ Configuration error: {e}")
            print("\n   Please set the required environment variables:")
            print("   export ANTHROPIC_API_KEY='your-api-key-here'")
            return 1
        
        # Step 2: Create directories
        print("\n2. Creating directories...")
        ensure_directories()
        print("   ✓ Directories created")
        
        # Step 3: Test Claude API connection
        print("\n3. Testing Claude API connection...")
        try:
            claude_client = ClaudeClient()
            if claude_client.test_connection():
                print("   ✓ Claude API connection successful")
                
                # Show model info
                model_info = claude_client.get_model_info()
                print(f"   ✓ Using model: {model_info['model']}")
            else:
                print("   ✗ Claude API connection failed")
                return 1
        except Exception as e:
            print(f"   ✗ Claude API error: {e}")
            return 1
        
        # Step 4: Initialize memory file
        print("\n4. Initializing memory file...")
        memory_manager = MemoryManager()
        
        try:
            memory_manager.create_initial_memory()
            print("   ✓ Memory file initialized")
            
            # Show memory stats
            stats = memory_manager.get_memory_stats()
            if stats['exists']:
                print(f"   ✓ Memory file: {stats['character_count']} characters")
            
        except Exception as e:
            print(f"   ✗ Failed to initialize memory: {e}")
            return 1
        
        # Step 5: Validate log processor
        print("\n5. Validating log processor...")
        try:
            log_processor = LogProcessor()
            log_stats = log_processor.get_log_stats()
            
            if log_stats.get('logs_dir_exists', False):
                print(f"   ✓ Found {log_stats['log_file_count']} log files")
                if log_stats['total_entries'] > 0:
                    print(f"   ✓ Total log entries: {log_stats['total_entries']}")
                else:
                    print("   ⚠ No log entries found (this is normal for new setups)")
            else:
                print("   ⚠ Logs directory created but empty")
            
        except Exception as e:
            print(f"   ✗ Log processor error: {e}")
            return 1
        
        # Step 6: Show next steps
        print("\n" + "=" * 40)
        print("🎉 Initialization Complete!")
        print("\nNext steps:")
        print("1. Add chat log files to the 'logs/' directory")
        print("2. Run: python scripts/process_logs.py --log-file sample_chat.log")
        print("3. Run: python scripts/test_memory.py")
        
        print("\nExample commands:")
        print("  # Process a specific log file")
        print("  python scripts/process_logs.py --log-file sample_chat.log")
        print("")
        print("  # Process logs from last 3 days")
        print("  python scripts/process_logs.py --days 3")
        print("")
        print("  # Dry run to see what would change")
        print("  python scripts/process_logs.py --dry-run")
        print("")
        print("  # Test the memory system")
        print("  python scripts/test_memory.py")
        
        print(f"\nMemory file location: {memory_manager.memory_file}")
        print(f"Logs directory: {log_processor.logs_dir}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        print(f"\n✗ Initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
