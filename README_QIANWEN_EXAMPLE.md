# Qianwen Skill Agent Example - Quick Reference

## Quick Start

1. **Set up environment**:
   ```bash
   # Create .env file
   echo "DASHSCOPE_API_KEY=your_key_here" > .env
   echo "DASHSCOPE_MODEL=qwen-turbo" >> .env
   ```

2. **Run the example**:
   ```bash
   python example_qianwen_skill_agent.py
   ```

## What's Included

### Main Example Script
- **`example_qianwen_skill_agent.py`**: Complete example showing how to create and use a Qianwen skill agent

### Example Skills
- **`skills/skill_calculator.py`**: Basic arithmetic calculator
- **`skills/skill_text_processor.py`**: Text manipulation tools (5 tools)
- **`skills/skill_time.py`**: Time and date utilities (3 tools)
- **`skills/skill_example.py`**: Simple example skill

## Usage in Your Code

```python
from example_qianwen_skill_agent import create_qianwen_model
from AgentSkill import create_skill_agent
from config import SkillSystemConfig
from pathlib import Path

# Create model
model = create_qianwen_model(model_name="qwen-turbo")

# Create agent
agent = create_skill_agent(
    model=model,
    config=SkillSystemConfig(skills_dir=Path("./skills"))
)

# Use agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "Your question"}]
})
```

## Available Skills

After running the example, you'll have access to:

1. **calculator**: `"Calculate 25 * 4"`
2. **text_processor_***: `"Convert 'hello' to uppercase"`
3. **time_***: `"What time is it?"`
4. **example**: `"Use example skill with 'test'"`

## Next Steps

- Read `QIANWEN_SKILL_AGENT_GUIDE.md` for detailed documentation
- Create your own skills in `skills/skill_*.py`
- Customize the system prompt and configuration
- Experiment with different Qianwen models
