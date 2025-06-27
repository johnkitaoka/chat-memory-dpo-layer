# LLM Memory System

**Automatically learn user preferences from chat logs and inject personalized context into any chatbot.** This system analyzes conversations to build user profiles that make your AWS Bedrock, Knowledge Base, or any LLM-powered chatbot more personalized and effective.

## What It Does

- **Learns Automatically**: Processes chat logs to understand user communication style, preferences, and context
- **Works Everywhere**: Inject memory context into Amazon Bedrock, Knowledge Bases, or any chatbot system
- **Simple Integration**: Add one line to your prompts to get personalized responses
- **Production Ready**: Handles real conversations, maintains backups, and scales with your application

## Quick Start (5 Minutes)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Set API key (get free key at console.anthropic.com)
export ANTHROPIC_API_KEY="your-api-key-here"

# 3. Initialize system
python scripts/init_memory.py

# 4. Process sample conversations
python scripts/process_logs.py --log-file sample_chat.log

# 5. See it work
python scripts/demo.py
```

## AWS Bedrock Integration

### Option 1: Direct Prompt Injection (Recommended)

```python
import boto3
from src.memory_manager import MemoryManager

# Initialize Bedrock and memory
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
memory = MemoryManager()

# Get personalized context
user_context = memory.get_context_for_prompt()

# Inject into your Bedrock prompt
prompt = f"""{user_context}

User Question: {user_question}

Please provide a helpful response based on the user context above."""

# Call Bedrock
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-5-haiku-20241022-v1:0',
    body=json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 1000,
        'messages': [{'role': 'user', 'content': prompt}]
    })
)
```

### Option 2: Knowledge Base Integration

```python
# For Bedrock Knowledge Bases, add memory to system instructions
knowledge_base = boto3.client('bedrock-agent-runtime')

# Get memory context
user_context = memory.get_context_for_prompt()

# Query with personalized context
response = knowledge_base.retrieve_and_generate(
    input={'text': user_question},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'your-kb-id',
            'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0',
            'generationConfiguration': {
                'additionalModelRequestFields': {
                    'system': user_context  # Inject memory here
                }
            }
        }
    }
)
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
