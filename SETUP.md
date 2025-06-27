# LLM Memory System Setup Guide

This guide will walk you through setting up the LLM Memory System step by step.

## Prerequisites

- Python 3.9 or higher
- Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))
- Basic familiarity with command line

## Step 1: Installation

### 1.1 Clone or Download the Repository

If you have the files, navigate to the memory directory:
```bash
cd memory
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `anthropic` - Anthropic's Python SDK
- `pyyaml` - YAML file processing
- `python-dotenv` - Environment variable management

## Step 2: Configuration

### 2.1 Set Up API Key

You have several options for setting your Anthropic API key:

**Option A: Environment Variable (Recommended)**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Option B: .env File**
Create a `.env` file in the memory directory:
```bash
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

**Option C: System Environment (Permanent)**
Add to your shell profile (`.bashrc`, `.zshrc`, etc.):
```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 2.2 Verify Configuration

Test your setup:
```bash
python scripts/init_memory.py
```

You should see output like:
```
🧠 LLM Memory System Initialization
========================================

1. Validating configuration...
   ✓ Configuration valid

2. Creating directories...
   ✓ Directories created

3. Testing Claude API connection...
   ✓ Claude API connection successful
   ✓ Using model: claude-3-5-haiku-20241022

4. Initializing memory file...
   ✓ Memory file initialized
   ✓ Memory file: 847 characters

5. Validating log processor...
   ✓ Found 2 log files
   ✓ Total log entries: 24

========================================
🎉 Initialization Complete!
```

## Step 3: Basic Usage

### 3.1 Process Sample Logs

The system comes with sample chat logs. Process them:

```bash
python scripts/process_logs.py --log-file sample_chat.log
```

### 3.2 Run Tests

Verify everything works:

```bash
python scripts/test_memory.py
```

### 3.3 Try the Demo

See the memory system in action:

```bash
python scripts/demo.py
```

## Step 4: Adding Your Own Data

### 4.1 Chat Log Format

Create log files in the `logs/` directory with this format:

```
[2024-06-27 10:30:00] USER: Your question here
[2024-06-27 10:30:15] ASSISTANT: Assistant response here
[2024-06-27 10:32:00] USER: Follow-up question
[2024-06-27 10:32:30] ASSISTANT: Another response
```

**Important formatting rules:**
- Use exact timestamp format: `[YYYY-MM-DD HH:MM:SS]`
- Use `USER:` and `ASSISTANT:` labels (case-sensitive)
- Save files with `.log` extension in the `logs/` directory

### 4.2 Processing Your Logs

Process specific log files:
```bash
python scripts/process_logs.py --log-file your_chat.log
```

Process recent logs (last 7 days):
```bash
python scripts/process_logs.py --days 7
```

Dry run to see what would change:
```bash
python scripts/process_logs.py --dry-run
```

## Step 5: Integration with Your Chatbot

### 5.1 Basic Integration

```python
from src.memory_manager import MemoryManager
from src.claude_client import ClaudeClient

# Initialize components
memory_manager = MemoryManager()
claude_client = ClaudeClient()

# Get user context for your prompts
user_context = memory_manager.get_context_for_prompt()

# Use in your chatbot prompt
prompt = f"{user_context}\n\nUser: {user_message}\n\nAssistant:"

# Send to your LLM
response = claude_client.client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=1000,
    messages=[{"role": "user", "content": prompt}]
)
```

### 5.2 Automated Memory Updates

Set up a cron job or scheduled task to process logs regularly:

```bash
# Add to crontab (run daily at 2 AM)
0 2 * * * cd /path/to/memory && python scripts/process_logs.py --days 1
```

## Troubleshooting

### Common Issues

**1. "Missing required environment variables: ANTHROPIC_API_KEY"**
- Solution: Set your API key as described in Step 2.1

**2. "Claude API connection failed"**
- Check your API key is correct
- Verify internet connection
- Check Anthropic service status

**3. "No log entries found to process"**
- Add log files to the `logs/` directory
- Check log file format matches the required pattern
- Ensure files have `.log` extension

**4. Import errors**
- Make sure you're running scripts from the memory directory
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Getting Help

1. Check the logs: `tail -f memory_processing.log`
2. Run with verbose output: `python scripts/process_logs.py --verbose`
3. Test system health: `python scripts/test_memory.py`

## Advanced Configuration

### Custom Model Settings

Edit `config.py` to customize:

```python
# Use a different Claude model
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"

# Adjust response length
CLAUDE_MAX_TOKENS = 2000

# Change creativity level
CLAUDE_TEMPERATURE = 0.3
```

### Custom Memory Template

Modify the default memory template in `config.py`:

```python
DEFAULT_MEMORY_TEMPLATE = """
YOUR CUSTOM MEMORY STRUCTURE
============================

SECTION 1:
- Custom field 1
- Custom field 2

SECTION 2:
- Another custom field
"""
```

### Log Processing Settings

Adjust processing behavior in `config.py`:

```python
# Minimum conversation length to analyze
MIN_CONVERSATION_LENGTH = 5

# Maximum characters to send to Claude
MAX_LOG_CHARS = 75000

# Default days to look back
DEFAULT_LOG_DAYS = 14
```

## Security Considerations

1. **API Key Security**: Never commit API keys to version control
2. **Log Privacy**: Ensure chat logs don't contain sensitive information
3. **File Permissions**: Restrict access to memory and log files
4. **Network Security**: Use HTTPS for API calls (handled automatically)

## Next Steps

1. **Production Deployment**: Set up automated log processing
2. **Monitoring**: Add logging and alerting for memory updates
3. **Backup**: Implement regular backups of memory files
4. **Scaling**: Consider database storage for large-scale deployments

For more examples and advanced usage, see the `scripts/` directory and the main README.md file.
