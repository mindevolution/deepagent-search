# Skill Agent UI Guide

A Streamlit-based web interface for interacting with the Skill Agent powered by Qianwen (通义千问) models.

## Features

### 🎨 Interactive Web Interface
- Clean, modern UI built with Streamlit
- Real-time chat with the skill agent
- Sidebar configuration panel

### ⚙️ Model Configuration
- Select Qianwen model (turbo, plus, max, max-longcontext)
- Adjust temperature and top_p parameters
- Configure skill system settings

### 🔧 Skill Management
- View all available skills
- See skill descriptions, tags, and visibility
- Auto-discover skills from directory

### 💬 Chat Interface
- Real-time conversation with the agent
- Chat history preservation
- Quick action buttons for common tasks

## Installation

### 1. Install Streamlit

```bash
pip install streamlit
```

### 2. Set Up Environment

Create a `.env` file in the project root:

```env
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_MODEL=qwen-turbo
```

### 3. Ensure Skills Directory Exists

Make sure you have skills in the `skills/` directory:

```bash
ls skills/
# Should show files like:
# skill_calculator.py
# skill_text_processor.py
# skill_time.py
# skill_example.py
```

## Usage

### Start the UI

```bash
streamlit run skill_agent_ui.py
```

The UI will open in your browser at `http://localhost:8501`

### Step-by-Step Guide

1. **Configure Model** (Sidebar):
   - Select Qianwen model (default: qwen-turbo)
   - Adjust temperature (0.0-1.0, default: 0.7)
   - Adjust top_p (0.0-1.0, default: 0.8)

2. **Configure Skill System** (Sidebar):
   - Set skills directory (default: ./skills)
   - Choose state mode (replace, accumulate, fifo)
   - Enable/disable auto-discovery
   - Enable/disable middleware
   - Toggle verbose logging

3. **Initialize Agent**:
   - Click "🚀 Initialize Agent" button
   - Wait for initialization to complete
   - You'll see the number of skills loaded

4. **Start Chatting**:
   - Type your question in the chat input
   - The agent will use available skills to help
   - View chat history in the main area

## Example Interactions

### Calculator
```
User: Calculate 25 * 4 + 10
Agent: [Uses calculator skill] Result: 110
```

### Text Processing
```
User: Convert "Hello World" to uppercase
Agent: [Uses text processor skill] HELLO WORLD
```

### Time Information
```
User: What time is it?
Agent: [Uses time skill] Current time: 2024-01-15 14:30:25
```

### Multiple Skills
```
User: What time is it and calculate 10 * 5?
Agent: [Uses time and calculator skills] Current time: ... Result: 50
```

## Quick Actions

The UI includes quick action buttons:

- **📋 List Skills**: Show all available skills
- **🧮 Calculator**: Quick access to calculator
- **⏰ Current Time**: Get current time
- **ℹ️ Agent Info**: Display agent configuration

## Configuration Options

### Model Settings

- **Model**: Choose from qwen-turbo, qwen-plus, qwen-max, qwen-max-longcontext
- **Temperature**: Controls randomness (0.0 = deterministic, 1.0 = creative)
- **Top P**: Nucleus sampling parameter

### Skill System Settings

- **Skills Directory**: Path to skills directory (default: ./skills)
- **State Mode**: 
  - `replace`: Replace state on each step
  - `accumulate`: Accumulate all messages
  - `fifo`: Fixed-size queue (recommended)
- **Auto Discover**: Automatically find and load skills
- **Middleware**: Enable dynamic tool filtering
- **Verbose**: Show detailed logging

## Troubleshooting

### Agent Not Initializing

**Error**: "DASHSCOPE_API_KEY not found"

**Solution**:
1. Create `.env` file in project root
2. Add `DASHSCOPE_API_KEY=your_key_here`
3. Restart the UI

### No Skills Loaded

**Issue**: Agent shows 0 skills

**Solution**:
1. Check that `skills/` directory exists
2. Ensure skill files follow pattern `skill_*.py`
3. Verify skills export a `tool` variable
4. Check that `auto_discover` is enabled

### Port Already in Use

**Error**: Port 8501 is already in use

**Solution**:
```bash
streamlit run skill_agent_ui.py --server.port 8502
```

### Import Errors

**Error**: Module not found

**Solution**:
1. Ensure you're running from project root
2. Check that all dependencies are installed
3. Verify Python path includes project directory

## Advanced Usage

### Custom System Prompt

Edit the `custom_system_prompt` in `skill_agent_ui.py`:

```python
agent = create_skill_agent(
    model=qianwen_model,
    config=config,
    custom_system_prompt="Your custom instructions here"
)
```

### Adding New Skills

1. Create a new file in `skills/` directory: `skill_mynewskill.py`
2. Follow the skill template:
```python
from langchain_core.tools import tool
from core import SkillMetadata

metadata = SkillMetadata(
    name="mynewskill",
    description="Description of your skill",
    tags=["tag1", "tag2"],
    visibility="public"
)

@tool
def my_tool(input: str) -> str:
    """Tool description"""
    return "Result"

tool = my_tool
```

3. Restart the UI and reinitialize the agent

### Multiple UI Instances

Run multiple instances on different ports:

```bash
# Terminal 1
streamlit run skill_agent_ui.py --server.port 8501

# Terminal 2
streamlit run skill_agent_ui.py --server.port 8502
```

## Tips

1. **Start Simple**: Begin with basic questions to test the agent
2. **Check Skills**: Use "List Skills" to see what's available
3. **Clear Chat**: Use "Clear Chat" button to start fresh
4. **Adjust Temperature**: Lower temperature for more consistent responses
5. **Use Specific Requests**: Be clear about which skill to use

## Keyboard Shortcuts

- `Ctrl/Cmd + Enter`: Send message
- `Ctrl/Cmd + K`: Clear chat (in some browsers)
- `R`: Rerun app (in Streamlit)

## Comparison with CLI

| Feature | Web UI | CLI |
|---------|--------|-----|
| Visual Interface | ✅ | ❌ |
| Configuration Panel | ✅ | ❌ |
| Skill Browser | ✅ | Limited |
| Chat History | ✅ | ✅ |
| Quick Actions | ✅ | ❌ |
| Easy Setup | ✅ | ✅ |

## Next Steps

1. Create custom skills for your use case
2. Experiment with different models
3. Adjust parameters for optimal performance
4. Integrate with other tools and services

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Qianwen Model Information](https://help.aliyun.com/zh/model-studio/)
- [Skill Agent Guide](./QIANWEN_SKILL_AGENT_GUIDE.md)
