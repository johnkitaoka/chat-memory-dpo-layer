# LLM Memory System Examples

This document provides practical examples of how to use the LLM Memory System in various scenarios.

## Basic Usage Examples

### Example 1: Processing a Single Log File

```bash
# Process a specific conversation log
python scripts/process_logs.py --log-file sample_chat.log

# Output:
# === Proposed Memory Amendments ===
# Amendment 1:
# SEARCH: [To be determined from conversations]
# REPLACE: Prefers step-by-step technical explanations with code examples
```

### Example 2: Processing Recent Logs

```bash
# Process logs from the last 3 days
python scripts/process_logs.py --days 3

# Dry run to see what would change
python scripts/process_logs.py --days 7 --dry-run
```

### Example 3: Automated Processing

```bash
# Force processing without confirmation
python scripts/process_logs.py --days 1 --force

# Verbose output for debugging
python scripts/process_logs.py --log-file debug.log --verbose
```

## Integration Examples

### Example 1: Simple Chatbot Integration

```python
#!/usr/bin/env python3
"""
Simple chatbot with memory integration
"""
import sys
from pathlib import Path

# Add memory system to path
sys.path.insert(0, str(Path(__file__).parent / "memory"))

from src.memory_manager import MemoryManager
from src.claude_client import ClaudeClient

class MemoryEnabledChatbot:
    def __init__(self):
        self.memory = MemoryManager()
        self.claude = ClaudeClient()
    
    def get_response(self, user_message: str) -> str:
        # Get personalized context
        context = self.memory.get_context_for_prompt()
        
        # Build prompt with memory context
        prompt = f"{context}\n\nUser: {user_message}\n\nAssistant:"
        
        # Get response from Claude
        response = self.claude.client.messages.create(
            model=self.claude.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text

# Usage
chatbot = MemoryEnabledChatbot()
response = chatbot.get_response("Help me with Python error handling")
print(response)
```

### Example 2: Flask Web Application

```python
from flask import Flask, request, jsonify
from src.memory_manager import MemoryManager
from src.claude_client import ClaudeClient

app = Flask(__name__)
memory_manager = MemoryManager()
claude_client = ClaudeClient()

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # Get personalized context
    context = memory_manager.get_context_for_prompt()
    
    # Generate response with memory
    prompt = f"{context}\n\nUser: {user_message}\n\nAssistant:"
    
    response = claude_client.client.messages.create(
        model=claude_client.model,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return jsonify({
        'response': response.content[0].text,
        'personalized': True
    })

@app.route('/memory', methods=['GET'])
def get_memory():
    memory_content = memory_manager.load_memory()
    stats = memory_manager.get_memory_stats()
    
    return jsonify({
        'memory': memory_content,
        'stats': stats
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### Example 3: Discord Bot Integration

```python
import discord
from discord.ext import commands
from src.memory_manager import MemoryManager
from src.claude_client import ClaudeClient

class MemoryBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.memory = MemoryManager()
        self.claude = ClaudeClient()
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
    
    @commands.command(name='ask')
    async def ask_with_memory(self, ctx, *, question):
        """Ask a question with personalized memory context"""
        
        # Get memory context
        context = self.memory.get_context_for_prompt()
        
        # Generate response
        prompt = f"{context}\n\nUser: {question}\n\nAssistant:"
        
        response = self.claude.client.messages.create(
            model=self.claude.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        await ctx.send(response.content[0].text)
    
    @commands.command(name='memory')
    async def show_memory(self, ctx):
        """Show current memory summary"""
        stats = self.memory.get_memory_stats()
        
        embed = discord.Embed(
            title="Memory Status",
            description=f"Characters: {stats['character_count']}\nLast updated: {stats['last_modified'][:10]}",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)

# Usage
bot = MemoryBot()
bot.run('YOUR_DISCORD_TOKEN')
```

## Log Format Examples

### Example 1: Customer Support Logs

```
[2024-06-27 09:15:00] USER: I'm having trouble with my API integration. The authentication keeps failing.
[2024-06-27 09:15:30] ASSISTANT: I can help you troubleshoot the API authentication. Let's start by checking your API key format. Are you using the correct header format?
[2024-06-27 09:16:00] USER: I'm using Bearer token in the Authorization header. Is that correct?
[2024-06-27 09:16:15] ASSISTANT: Yes, that's correct. The format should be "Authorization: Bearer YOUR_API_KEY". Can you verify that your API key is active and hasn't expired?
```

### Example 2: Technical Consultation Logs

```
[2024-06-27 14:20:00] USER: I need to design a microservices architecture for an e-commerce platform. What's the best approach?
[2024-06-27 14:20:45] ASSISTANT: For e-commerce microservices, I'd recommend starting with these core services: User Management, Product Catalog, Order Processing, Payment, and Inventory. Let me break down each service...
[2024-06-27 14:22:00] USER: How should I handle data consistency across these services?
[2024-06-27 14:22:30] ASSISTANT: For data consistency in microservices, you have several patterns to consider: Saga pattern for distributed transactions, Event Sourcing for audit trails, and CQRS for read/write separation...
```

### Example 3: Educational Tutoring Logs

```
[2024-06-27 16:30:00] USER: Can you explain how machine learning algorithms work?
[2024-06-27 16:30:30] ASSISTANT: Machine learning algorithms learn patterns from data to make predictions. There are three main types: supervised learning (with labeled data), unsupervised learning (finding hidden patterns), and reinforcement learning (learning through trial and error).
[2024-06-27 16:32:00] USER: Can you give me a simple example of supervised learning?
[2024-06-27 16:32:15] ASSISTANT: Sure! A classic example is email spam detection. You train the algorithm with thousands of emails labeled as "spam" or "not spam". The algorithm learns patterns in the text, and then can classify new emails automatically.
```

## Memory Evolution Examples

### Initial Memory State

```
USER PROFILE
===========

COMMUNICATION STYLE:
- [To be determined from conversations]

INTERESTS:
- [To be determined from conversations]

PREFERENCES:
- [To be determined from conversations]

CONTEXT:
- [To be determined from conversations]
```

### After Processing Technical Support Logs

```
USER PROFILE
===========

COMMUNICATION STYLE:
- Prefers direct, solution-focused responses
- Appreciates step-by-step troubleshooting guides
- Values clear explanations of technical concepts
- Responds well to code examples and practical demonstrations

INTERESTS:
- API development and integration
- Web application architecture
- Database design and optimization
- Cloud deployment and DevOps practices

PREFERENCES:
- Likes detailed error analysis and debugging steps
- Prefers multiple solution options when available
- Values links to documentation and resources
- Appreciates follow-up questions to clarify requirements

CONTEXT:
- Works as a backend developer
- Frequently integrates third-party APIs
- Uses Python and JavaScript primarily
- Deploys applications on AWS
```

### After Processing Educational Logs

```
USER PROFILE
===========

COMMUNICATION STYLE:
- Prefers structured, educational explanations
- Appreciates analogies and real-world examples
- Values progressive complexity (simple to advanced)
- Responds well to interactive learning approaches

INTERESTS:
- Machine learning and data science
- Software engineering principles
- Algorithm design and analysis
- Technology trends and innovations

PREFERENCES:
- Likes visual aids and diagrams when possible
- Prefers hands-on exercises and practice problems
- Values historical context and background information
- Appreciates recommended reading and further resources

CONTEXT:
- Student or early-career professional
- Learning programming and computer science concepts
- Interested in AI and machine learning applications
- Seeks comprehensive understanding rather than quick fixes
```

## Advanced Usage Examples

### Example 1: Batch Processing Multiple Log Files

```python
#!/usr/bin/env python3
"""
Batch process multiple log files
"""
from pathlib import Path
from src.log_processor import LogProcessor
from src.memory_manager import MemoryManager
from src.claude_client import ClaudeClient

def batch_process_logs():
    log_processor = LogProcessor()
    memory_manager = MemoryManager()
    claude_client = ClaudeClient()
    
    logs_dir = Path("logs")
    log_files = list(logs_dir.glob("*.log"))
    
    print(f"Processing {len(log_files)} log files...")
    
    for log_file in log_files:
        print(f"Processing {log_file.name}...")
        
        # Get entries from this file
        entries = log_processor.get_logs_by_file(log_file.name)
        
        if len(entries) < 3:  # Skip short conversations
            continue
        
        # Analyze and update memory
        current_memory = memory_manager.load_memory()
        analysis = log_processor.analyze_logs(entries, current_memory, claude_client)
        amendments = memory_manager.extract_amendments(analysis)
        
        if amendments:
            print(f"  Found {len(amendments)} amendments")
            memory_manager.apply_amendments(amendments)
        else:
            print("  No amendments needed")

if __name__ == "__main__":
    batch_process_logs()
```

### Example 2: Memory Backup and Versioning

```python
#!/usr/bin/env python3
"""
Memory backup and versioning system
"""
import shutil
from datetime import datetime
from pathlib import Path
from src.memory_manager import MemoryManager

def backup_memory():
    memory_manager = MemoryManager()
    
    # Create backup directory
    backup_dir = Path("memory_backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"memory_{timestamp}.txt"
    
    # Copy current memory
    shutil.copy2(memory_manager.memory_file, backup_file)
    
    print(f"Memory backed up to: {backup_file}")
    
    # Keep only last 10 backups
    backups = sorted(backup_dir.glob("memory_*.txt"))
    if len(backups) > 10:
        for old_backup in backups[:-10]:
            old_backup.unlink()
            print(f"Removed old backup: {old_backup}")

def restore_memory(backup_file: str):
    memory_manager = MemoryManager()
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"Backup file not found: {backup_file}")
        return
    
    # Create backup of current memory
    current_backup = memory_manager.memory_file.with_suffix('.txt.pre_restore')
    shutil.copy2(memory_manager.memory_file, current_backup)
    
    # Restore from backup
    shutil.copy2(backup_path, memory_manager.memory_file)
    
    print(f"Memory restored from: {backup_file}")
    print(f"Previous memory saved as: {current_backup}")

if __name__ == "__main__":
    backup_memory()
```

### Example 3: Memory Analytics

```python
#!/usr/bin/env python3
"""
Analyze memory evolution and statistics
"""
import re
from collections import Counter
from src.memory_manager import MemoryManager

def analyze_memory():
    memory_manager = MemoryManager()
    memory_content = memory_manager.load_memory()
    
    # Extract sections
    sections = {}
    current_section = None
    
    for line in memory_content.split('\n'):
        if line.endswith(':') and line.isupper():
            current_section = line.rstrip(':')
            sections[current_section] = []
        elif line.startswith('- ') and current_section:
            sections[current_section].append(line[2:])
    
    # Analyze content
    print("Memory Analysis Report")
    print("=" * 40)
    
    for section, items in sections.items():
        print(f"\n{section}:")
        print(f"  Items: {len(items)}")
        
        if items:
            # Word frequency analysis
            all_text = ' '.join(items)
            words = re.findall(r'\b\w+\b', all_text.lower())
            common_words = Counter(words).most_common(5)
            
            print(f"  Common terms: {', '.join([word for word, count in common_words])}")
    
    # Overall statistics
    stats = memory_manager.get_memory_stats()
    print(f"\nOverall Statistics:")
    print(f"  Total characters: {stats['character_count']}")
    print(f"  Total lines: {stats['line_count']}")
    print(f"  Last modified: {stats['last_modified']}")
    print(f"  Valid format: {stats['valid_format']}")

if __name__ == "__main__":
    analyze_memory()
```

These examples demonstrate the flexibility and power of the LLM Memory System for various use cases and integration scenarios.
