#!/usr/bin/env python3
"""
Memory System Demo

Interactive demo showing how to integrate the memory system into a chatbot.
"""

import sys
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.claude_client import ClaudeClient
from src.memory_manager import MemoryManager


def setup_logging() -> None:
    """Setup logging configuration"""
    logging.basicConfig(level=logging.WARNING)  # Quiet for demo


class PersonalizedChatbot:
    """Example chatbot with memory integration"""
    
    def __init__(self):
        self.claude_client = ClaudeClient()
        self.memory_manager = MemoryManager()
        self.conversation_history = []
    
    def get_response(self, user_input: str, use_memory: bool = True) -> str:
        """
        Generate response with optional memory context
        
        Args:
            user_input: User's message
            use_memory: Whether to include memory context
            
        Returns:
            Chatbot response
        """
        try:
            # Build prompt
            if use_memory:
                memory_context = self.memory_manager.get_context_for_prompt()
                prompt = f"{memory_context}\n\nUser: {user_input}\n\nAssistant:"
            else:
                prompt = f"User: {user_input}\n\nAssistant:"
            
            # Get response from Claude
            response = self.claude_client.client.messages.create(
                model=self.claude_client.model,
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
            return f"Sorry, I encountered an error: {str(e)}"
    
    def chat_session(self):
        """Run interactive chat session"""
        print("🤖 Personalized Chatbot Demo")
        print("=" * 40)
        print("This demo shows how memory enhances chatbot responses.")
        print("Type 'quit' to exit, 'memory' to view current memory.")
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'memory':
                    self.show_memory()
                    continue
                
                if not user_input:
                    continue
                
                # Show both responses for comparison
                print("\n🤖 Response WITHOUT memory:")
                response_without = self.get_response(user_input, use_memory=False)
                print(response_without)
                
                print("\n🧠 Response WITH memory:")
                response_with = self.get_response(user_input, use_memory=True)
                print(response_with)
                
                print("\n" + "-" * 40)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_memory(self):
        """Display current memory content"""
        try:
            memory_content = self.memory_manager.load_memory()
            print("\n📋 Current Memory:")
            print("=" * 40)
            print(memory_content)
            print("=" * 40)
        except Exception as e:
            print(f"Error loading memory: {e}")


def run_quick_demo():
    """Run a quick automated demo"""
    print("🚀 Quick Demo: Memory System in Action")
    print("=" * 50)
    
    try:
        chatbot = PersonalizedChatbot()
        
        # Test queries that should show memory benefits
        test_queries = [
            "I need help with a Python project",
            "What's the best way to handle errors?",
            "Can you recommend a deployment strategy?",
            "How should I structure my code?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Example {i} ---")
            print(f"User: {query}")
            
            # Response without memory
            print(f"\n🤖 Standard Response:")
            response_without = chatbot.get_response(query, use_memory=False)
            print(response_without[:300] + ("..." if len(response_without) > 300 else ""))
            
            # Response with memory
            print(f"\n🧠 Personalized Response:")
            response_with = chatbot.get_response(query, use_memory=True)
            print(response_with[:300] + ("..." if len(response_with) > 300 else ""))
            
            print("\n" + "=" * 50)
        
        print("\n✨ Notice how the personalized responses:")
        print("   • Use your preferred communication style")
        print("   • Reference your technical background")
        print("   • Provide more relevant examples")
        print("   • Match your response format preferences")
        
    except Exception as e:
        print(f"Demo failed: {e}")


def main():
    """Main demo function"""
    setup_logging()
    
    print("Welcome to the LLM Memory System Demo!")
    print("\nChoose an option:")
    print("1. Quick automated demo")
    print("2. Interactive chat session")
    print("3. View current memory")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            run_quick_demo()
        elif choice == "2":
            chatbot = PersonalizedChatbot()
            chatbot.chat_session()
        elif choice == "3":
            memory_manager = MemoryManager()
            memory_content = memory_manager.load_memory()
            print("\n📋 Current Memory:")
            print("=" * 40)
            print(memory_content)
        else:
            print("Invalid choice. Please run again and select 1, 2, or 3.")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        return 1
    except Exception as e:
        print(f"Demo error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
