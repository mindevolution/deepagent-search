# DeepAgent Chat UI

Interactive chat interfaces for DeepAgent with persistent memory support.

## Available Interfaces

### 1. Streamlit Web UI (Recommended)

A beautiful web-based chat interface with memory management.

**Installation:**
```bash
pip install streamlit
```

**Run:**
```bash
streamlit run chat_ui.py
```

**Features:**
- 🎨 Modern web interface
- 💬 Real-time chat
- 🧵 Thread management (new conversations)
- 🔍 Memory inspection
- 📱 Responsive design
- 💾 Persistent memory across sessions

**Usage:**
1. Start the server: `streamlit run chat_ui.py`
2. Open your browser to the URL shown (usually `http://localhost:8501`)
3. Type your questions in the chat input
4. Use sidebar to manage threads and inspect memories

### 2. Command-Line Interface (CLI)

A simple terminal-based chat interface.

**Run:**
```bash
python chat_cli.py
```

**Features:**
- 💻 Terminal-based interface
- 🧵 Thread management
- 🔍 Memory inspection
- 📝 Command-based controls

**Commands:**
- `help` - Show help message
- `new` - Start a new conversation thread
- `memories` - List all memories
- `memory <key>` - View a specific memory
- `clear` - Clear chat history
- `quit` / `exit` - Exit the chat

**Example:**
```
You: What is React?
🤖 Agent: React is a JavaScript library for building user interfaces...

You: memories
📚 Found 2 memory item(s):
  1. /memories/project_notes.txt
  2. /memories/preferences.txt

You: memory project_notes.txt
📄 Memory: project_notes.txt
------------------------------------------------------------
We're building a web app with React...
------------------------------------------------------------

You: quit
👋 Goodbye!
```

## Configuration

Both interfaces use the agent configuration from `long-term-memory.py`:
- **Model**: DeepSeek via DashScope
- **Tools**: Internet search (Tavily)
- **Memory**: Persistent storage at `/memories/`
- **System Prompt**: Custom instructions with memory awareness

## Environment Variables

Make sure your `.env` file contains:
```env
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_MODEL=deepseek-v3  # Optional, defaults to deepseek-v3
TAVILY_API_KEY=your_tavily_key_here
```

## Features

### Persistent Memory

The agent can remember information across conversations:
- Save preferences: "Save my preferences to /memories/preferences.txt"
- Read memories: "What are my preferences?"
- Update memories: "Update my preferences to include dark mode"

### Web Search

The agent has access to real-time web search:
- "Search for the latest news about AI"
- "What is the weather in Tokyo?"
- "Find information about Python async programming"

### Thread Management

Each conversation thread maintains its own context:
- **New Thread**: Start a fresh conversation
- **Same Thread**: Continue previous conversation with context
- **Thread ID**: Unique identifier for each conversation

## Troubleshooting

### Streamlit not found
```bash
pip install streamlit
```

### Agent errors
- Check your API keys in `.env`
- Verify network connection
- Check API quotas/limits

### Memory not persisting
- Memories are stored in-memory (lost on restart)
- For persistent storage, consider using a file-based store

### Port already in use (Streamlit)
```bash
streamlit run chat_ui.py --server.port 8502
```

## Advanced Usage

### Custom System Prompt

Edit `long-term-memory.py` to change the agent's behavior:
```python
agent = create_deep_agent(
    ...
    system_prompt="Your custom instructions here"
)
```

### Add More Tools

Add tools to the agent in `long-term-memory.py`:
```python
agent = create_deep_agent(
    ...
    tools=[internet_search, your_custom_tool]
)
```

### Memory Access

Access memories programmatically:
```python
from long_term_memory import store
import asyncio

async def check_memories():
    async for key in store.alist("/memories/"):
        value = await store.aget(key)
        print(f"{key}: {value}")

asyncio.run(check_memories())
```

## Tips

1. **Use specific questions**: "What is React?" instead of "Tell me about React"
2. **Save important info**: "Save this to /memories/notes.txt"
3. **Start new threads**: Use "New Thread" for unrelated topics
4. **Inspect memories**: Check what the agent remembers
5. **Clear chat**: Start fresh without losing memories

## Next Steps

- Add streaming responses for real-time output
- Implement conversation history export
- Add memory search functionality
- Create custom tool integrations
- Add multi-user support

