# LLM Memory System

A simple Python repository for managing LLM memory in a text-based format. This system helps chatbot developers easily implement personalized memory by maintaining a user profile that can be injected into system prompts.

## Features

- **Text-based Memory Storage**: Simple, human-readable memory.txt format
- **Chat Log Processing**: Automated analysis of conversation logs
- **Claude 3.5 Haiku Integration**: Uses Anthropic's efficient model for memory updates
- **Diff-based Updates**: Precise memory amendments using search/replace format
- **Easy Integration**: Minimal setup for existing chatbot systems

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API Key**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   # Or create a .env file with ANTHROPIC_API_KEY=your-api-key-here
   ```

3. **Initialize Memory**
   ```bash
   python scripts/init_memory.py
   ```

4. **Process Chat Logs**
   ```bash
   python scripts/process_logs.py --log-file logs/sample_chat.log
   ```

5. **Test Memory System**
   ```bash
   python scripts/test_memory.py
   ```

## Project Structure

```
memory/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── prompts.yaml             # LLM prompts for memory processing
├── config.py                # Configuration settings
├── memory.txt               # User memory file (created after init)
├── scripts/                 # Main scripts
│   ├── init_memory.py       # Initialize memory system
│   ├── process_logs.py      # Process chat logs to update memory
│   └── test_memory.py       # Test and demonstrate the system
├── logs/                    # Sample chat logs
│   ├── sample_chat.log      # Example conversation
│   └── sample_chat_2.log    # Another example
└── src/                     # Core library code
    ├── __init__.py
    ├── memory_manager.py    # Memory file operations
    ├── log_processor.py     # Chat log parsing
    └── claude_client.py     # Anthropic API integration
```

## Memory File Format

The `memory.txt` file uses a structured text format:

```
USER PROFILE
===========

COMMUNICATION STYLE:
- Prefers concise, direct responses
- Appreciates technical details when relevant
- Responds well to examples and code snippets

INTERESTS:
- Machine learning and AI development
- Python programming
- Software architecture

PREFERENCES:
- Likes step-by-step explanations
- Values practical, actionable advice
- Prefers markdown formatting for code

CONTEXT:
- Works as a software developer
- Has experience with cloud platforms
- Currently building chatbot applications
```

## Chat Log Format

Chat logs should follow this format:

```
[2024-01-15 10:30:00] USER: How do I implement rate limiting in my API?
[2024-01-15 10:30:15] ASSISTANT: Here are several approaches to implement rate limiting...
[2024-01-15 10:32:00] USER: Thanks! Can you show me a Python example?
[2024-01-15 10:32:30] ASSISTANT: Certainly! Here's a simple rate limiter using Redis...
```

## Configuration

Edit `config.py` to customize:

- API settings (model, temperature, max tokens)
- File paths (memory file, log directory)
- Processing options (date ranges, log filters)

## Usage Examples

### Processing Recent Logs
```python
from src.log_processor import LogProcessor
from src.memory_manager import MemoryManager

# Process logs from the last week
processor = LogProcessor()
memory_manager = MemoryManager()

logs = processor.get_recent_logs(days=7)
amendments = processor.analyze_logs(logs)
memory_manager.apply_amendments(amendments)
```

### Custom Memory Queries
```python
from src.memory_manager import MemoryManager

memory = MemoryManager()
user_context = memory.get_context_for_prompt()
print(f"Current user context:\n{user_context}")
```

## API Reference

### MemoryManager
- `load_memory()`: Load current memory from file
- `save_memory(content)`: Save memory to file
- `apply_amendments(amendments)`: Apply diff-based changes
- `get_context_for_prompt()`: Get formatted context for LLM prompts

### LogProcessor
- `parse_log_file(filepath)`: Parse a single log file
- `get_recent_logs(days)`: Get logs from recent days
- `analyze_logs(logs)`: Send logs to Claude for analysis
- `extract_amendments(response)`: Extract diff blocks from LLM response

### ClaudeClient
- `analyze_conversation(logs, current_memory)`: Send analysis request
- `configure(api_key, model)`: Set up API client

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For questions or issues:
- Check the examples in the `scripts/` directory
- Review the test cases in `scripts/test_memory.py`
- Open an issue on GitHub
