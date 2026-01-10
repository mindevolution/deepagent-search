# Qianwen Skill Agent Guide

Complete guide for using DashScope Qianwen (通义千问) model with the Skill Agent system.

## Overview

This guide demonstrates how to create a skill agent using Qianwen chat models from DashScope (阿里云通义千问). The skill agent can automatically discover and use various skills (tools) to accomplish tasks.

## Prerequisites

1. **DashScope API Key**: Get your API key from [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. **Python Dependencies**: Install required packages
3. **Skills Directory**: Create skills in the `skills/` directory

## Setup

### 1. Install Dependencies

```bash
pip install langchain langchain-core langchain-community python-dotenv
```

### 2. Configure API Key

Create a `.env` file in the project root:

```env
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_MODEL=qwen-turbo  # Optional, defaults to qwen-turbo
```

### 3. Available Qianwen Models

DashScope provides several Qianwen models:

- **qwen-turbo**: Fast and cost-effective (recommended for most use cases)
- **qwen-plus**: More capable, better for complex tasks
- **qwen-max**: Most capable, best quality
- **qwen-max-longcontext**: For long context tasks

## Quick Start

### Basic Example

```python
from pathlib import Path
from langchain_community.chat_models import ChatTongyi
from AgentSkill import create_skill_agent
from config import SkillSystemConfig
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Qianwen model
qianwen_model = ChatTongyi(
    model="qwen-turbo",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0.7,
    top_p=0.8
)

# Create skill agent
agent = create_skill_agent(
    model=qianwen_model,
    config=SkillSystemConfig(
        skills_dir=Path("./skills"),
        state_mode="fifo",
        verbose=True
    )
)

# Use the agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is 25 * 4?"}]
})

print(result["messages"][-1].content)
```

### Run the Example Script

```bash
python example_qianwen_skill_agent.py
```

## Creating Skills

### Skill File Structure

Skills are Python files in the `skills/` directory with the naming pattern `skill_*.py`.

### Basic Skill Template

```python
from langchain_core.tools import tool
from core import SkillMetadata

# Define metadata
metadata = SkillMetadata(
    name="my_skill",
    description="Description of what this skill does",
    tags=["tag1", "tag2"],
    visibility="public",  # "public", "private", or "internal"
    version="1.0.0"
)

# Define the tool
@tool
def my_tool(input: str) -> str:
    """Tool description for the LLM"""
    # Your tool logic here
    return "Result"

# Export the tool (required)
tool = my_tool
```

### Multiple Tools in One Module

You can define multiple tools in a single skill file:

```python
from langchain_core.tools import tool
from core import SkillMetadata

metadata = SkillMetadata(
    name="text_processor",
    description="Text processing tools",
    tags=["text", "utility"],
    visibility="public"
)

@tool
def text_uppercase(text: str) -> str:
    """Convert text to uppercase"""
    return text.upper()

@tool
def text_lowercase(text: str) -> str:
    """Convert text to lowercase"""
    return text.lower()

# Export as a list
tools = [text_uppercase, text_lowercase]

# For compatibility, also export the first tool
tool = text_uppercase
```

## Included Example Skills

The project includes several example skills:

### 1. Calculator (`skill_calculator.py`)
- Performs basic arithmetic operations
- Example: "What is 25 * 4?"

### 2. Text Processor (`skill_text_processor.py`)
- Text manipulation tools
- Functions: uppercase, lowercase, reverse, word count, character count

### 3. Time (`skill_time.py`)
- Get current time and date
- Functions: get_current_time, get_current_date, get_timestamp

### 4. Example (`skill_example.py`)
- Simple example demonstrating the skill system

## Advanced Configuration

### Custom System Prompt

```python
agent = create_skill_agent(
    model=qianwen_model,
    config=config,
    custom_system_prompt="""You are a helpful assistant.
Always be polite and explain your actions clearly."""
)
```

### State Management Modes

The skill agent supports three state management modes:

1. **replace**: Replace state on each step (default)
2. **accumulate**: Accumulate all messages and steps
3. **fifo**: Maintain a fixed-size queue (FIFO)

```python
config = SkillSystemConfig(
    state_mode="fifo",  # or "replace", "accumulate"
    # ... other settings
)
```

### Skill Filtering

Filter skills by visibility or custom criteria:

```python
# Filter by visibility
config = SkillSystemConfig(
    filter_by_visibility=True,
    allowed_visibilities=["public"]  # Only load public skills
)

# Custom filter function
def my_filter(metadata: SkillMetadata) -> bool:
    return "math" in metadata.tags

agent = create_skill_agent(
    model=qianwen_model,
    config=config,
    filter_fn=my_filter
)
```

### Middleware Configuration

Enable or disable dynamic tool filtering:

```python
config = SkillSystemConfig(
    middleware_enabled=True,  # Enable dynamic tool filtering
    verbose=True  # Show filtering decisions
)
```

## Usage Examples

### Example 1: Basic Calculation

```python
result = agent.invoke({
    "messages": [{"role": "user", "content": "Calculate 123 + 456"}]
})
print(result["messages"][-1].content)
```

### Example 2: Text Processing

```python
result = agent.invoke({
    "messages": [{"role": "user", "content": "Convert 'Hello World' to uppercase"}]
})
print(result["messages"][-1].content)
```

### Example 3: Multiple Skills

```python
result = agent.invoke({
    "messages": [{"role": "user", "content": "What time is it and calculate 10 * 5"}]
})
print(result["messages"][-1].content)
```

### Example 4: List Available Skills

```python
# List all skills
skills = agent.list_skills()
print(f"Available skills: {skills}")

# Get skill information
info = agent.get_skill_info("calculator")
print(f"Calculator info: {info.description}")

# Search skills
results = agent.search_skills(query="text", tags=["utility"])
for skill in results:
    print(f"Found: {skill.name} - {skill.description}")
```

## Troubleshooting

### API Key Issues

**Error**: `DASHSCOPE_API_KEY not found`

**Solution**: 
1. Create a `.env` file in the project root
2. Add `DASHSCOPE_API_KEY=your_key_here`
3. Or set it as an environment variable: `export DASHSCOPE_API_KEY=your_key_here`

### No Skills Loaded

**Error**: `No skills loaded! Agent will have no skill capabilities.`

**Solution**:
1. Ensure `skills/` directory exists
2. Create skill files with pattern `skill_*.py`
3. Each skill file must export a `tool` variable
4. Check that `auto_discover=True` in config

### Import Errors

**Error**: `ImportError: attempted relative import with no known parent package`

**Solution**: Make sure you're running scripts from the project root directory, or add the project to Python path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### Model Not Found

**Error**: `Model not exist`

**Solution**: 
1. Check the model name is correct (e.g., "qwen-turbo", "qwen-plus")
2. Verify your API key has access to the model
3. Check DashScope console for available models

## Best Practices

1. **Skill Naming**: Use descriptive names that indicate the skill's purpose
2. **Metadata**: Always provide clear descriptions and relevant tags
3. **Error Handling**: Include error handling in your tools
4. **Documentation**: Document tool parameters and return values clearly
5. **Testing**: Test skills individually before adding to the registry
6. **Visibility**: Use "public" for general skills, "private" for sensitive operations

## Next Steps

1. Create your own custom skills in the `skills/` directory
2. Experiment with different Qianwen models (turbo, plus, max)
3. Customize the system prompt for your use case
4. Add more complex skills that combine multiple operations
5. Integrate with external APIs and services

## Resources

- [DashScope Documentation](https://help.aliyun.com/zh/model-studio/)
- [LangChain Documentation](https://python.langchain.com/)
- [Qianwen Model Information](https://help.aliyun.com/zh/model-studio/developer-reference/model-introduction)
