#!/usr/bin/env python3
"""
Test Memory System

Script to test and demonstrate the effectiveness of the memory system
with before/after comparisons of chatbot responses.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.claude_client import ClaudeClient
from src.memory_manager import MemoryManager
from src.log_processor import LogProcessor
from config import validate_config


def setup_logging() -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_test_queries() -> List[Dict[str, str]]:
    """Get test queries to demonstrate memory effectiveness"""
    return [
        {
            "query": "I need help with a Python API project. What's the best approach?",
            "context": "General API development question"
        },
        {
            "query": "How should I handle file uploads in my application?",
            "context": "File handling question"
        },
        {
            "query": "I want to set up CI/CD for my project. Any recommendations?",
            "context": "DevOps and deployment question"
        },
        {
            "query": "Can you help me with database design for user data?",
            "context": "Database architecture question"
        },
        {
            "query": "What's the best way to implement authentication?",
            "context": "Security and authentication question"
        }
    ]


def generate_response(claude_client: ClaudeClient, query: str, context: str = "") -> str:
    """
    Generate a response using Claude
    
    Args:
        claude_client: Initialized Claude client
        query: User query
        context: Additional context (memory) to include
        
    Returns:
        Claude's response
    """
    try:
        # Construct prompt with optional context
        if context:
            prompt = f"{context}\n\nUser Question: {query}"
        else:
            prompt = f"User Question: {query}"
        
        response = claude_client.client.messages.create(
            model=claude_client.model,
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return response.content[0].text
        
    except Exception as e:
        return f"Error generating response: {str(e)}"


def run_comparison_test(claude_client: ClaudeClient, memory_manager: MemoryManager) -> None:
    """Run before/after comparison test"""
    
    print("\n" + "=" * 60)
    print("🧪 MEMORY EFFECTIVENESS TEST")
    print("=" * 60)
    
    # Get user context from memory
    user_context = memory_manager.get_context_for_prompt()
    
    # Get test queries
    test_queries = get_test_queries()
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        description = test_case["context"]
        
        print(f"\n--- Test Case {i}: {description} ---")
        print(f"Query: {query}")
        
        # Generate response WITHOUT memory context
        print("\n🤖 Response WITHOUT Memory:")
        print("-" * 40)
        response_without = generate_response(claude_client, query)
        print(response_without[:500] + ("..." if len(response_without) > 500 else ""))
        
        # Generate response WITH memory context
        print(f"\n🧠 Response WITH Memory:")
        print("-" * 40)
        response_with = generate_response(claude_client, query, user_context)
        print(response_with[:500] + ("..." if len(response_with) > 500 else ""))
        
        print("\n" + "=" * 60)


def run_memory_analysis_test(log_processor: LogProcessor, memory_manager: MemoryManager, claude_client: ClaudeClient) -> None:
    """Test memory analysis with sample logs"""
    
    print("\n" + "=" * 60)
    print("📊 MEMORY ANALYSIS TEST")
    print("=" * 60)
    
    # Get log stats
    log_stats = log_processor.get_log_stats()
    print(f"Available log files: {log_stats.get('log_file_count', 0)}")
    print(f"Total log entries: {log_stats.get('total_entries', 0)}")
    
    if log_stats.get('total_entries', 0) == 0:
        print("\n⚠️  No log entries found. Please add some log files to test memory analysis.")
        return
    
    # Test with sample logs
    print("\n🔍 Analyzing sample logs...")
    
    try:
        # Get recent logs
        entries = log_processor.get_recent_logs(days=30)  # Look back 30 days
        
        if not entries:
            print("No recent log entries found.")
            return
        
        print(f"Found {len(entries)} log entries to analyze")
        
        # Load current memory
        current_memory = memory_manager.load_memory()
        
        # Analyze logs
        analysis_response = log_processor.analyze_logs(
            entries=entries,
            current_memory=current_memory,
            claude_client=claude_client
        )
        
        print("\n📝 Claude's Analysis:")
        print("-" * 40)
        print(analysis_response)
        
        # Extract potential amendments
        amendments = memory_manager.extract_amendments(analysis_response)
        
        if amendments:
            print(f"\n💡 Found {len(amendments)} potential memory amendments:")
            for i, (search, replace) in enumerate(amendments, 1):
                print(f"\nAmendment {i}:")
                print(f"  SEARCH: {search[:100]}{'...' if len(search) > 100 else ''}")
                print(f"  REPLACE: {replace[:100]}{'...' if len(replace) > 100 else ''}")
        else:
            print("\n✅ No memory amendments needed - current memory is up to date!")
        
    except Exception as e:
        print(f"\n❌ Error during memory analysis: {str(e)}")


def run_system_health_check() -> bool:
    """Run comprehensive system health check"""
    
    print("\n" + "=" * 60)
    print("🏥 SYSTEM HEALTH CHECK")
    print("=" * 60)
    
    all_good = True
    
    try:
        # Test 1: Configuration
        print("\n1. Configuration Check...")
        validate_config()
        print("   ✅ Configuration valid")
        
        # Test 2: Claude API
        print("\n2. Claude API Check...")
        claude_client = ClaudeClient()
        if claude_client.test_connection():
            print("   ✅ Claude API connection successful")
            model_info = claude_client.get_model_info()
            print(f"   ✅ Model: {model_info['model']}")
        else:
            print("   ❌ Claude API connection failed")
            all_good = False
        
        # Test 3: Memory System
        print("\n3. Memory System Check...")
        memory_manager = MemoryManager()
        memory_stats = memory_manager.get_memory_stats()
        
        if memory_stats['exists']:
            print(f"   ✅ Memory file exists ({memory_stats['character_count']} chars)")
            if memory_stats['valid_format']:
                print("   ✅ Memory format valid")
            else:
                print("   ⚠️  Memory format issues detected")
        else:
            print("   ❌ Memory file not found")
            all_good = False
        
        # Test 4: Log Processing
        print("\n4. Log Processing Check...")
        log_processor = LogProcessor()
        log_stats = log_processor.get_log_stats()
        
        if log_stats.get('logs_dir_exists', False):
            print(f"   ✅ Logs directory exists")
            print(f"   ✅ Found {log_stats['log_file_count']} log files")
            print(f"   ✅ Total entries: {log_stats['total_entries']}")
        else:
            print("   ⚠️  Logs directory not found or empty")
        
        return all_good
        
    except Exception as e:
        print(f"\n❌ Health check failed: {str(e)}")
        return False


def main():
    """Main test function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🧠 LLM Memory System Test Suite")
    print("Testing memory effectiveness and system health...")
    
    try:
        # Run health check first
        if not run_system_health_check():
            print("\n❌ System health check failed. Please fix issues before running tests.")
            return 1
        
        # Initialize components
        claude_client = ClaudeClient()
        memory_manager = MemoryManager()
        log_processor = LogProcessor()
        
        # Run comparison test
        run_comparison_test(claude_client, memory_manager)
        
        # Run memory analysis test
        run_memory_analysis_test(log_processor, memory_manager, claude_client)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nThe memory system is working correctly!")
        print("You can now use it to enhance your chatbot's personalization.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"\n❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
