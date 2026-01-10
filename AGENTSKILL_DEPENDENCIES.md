# AgentSkill.py Dependencies

## Status

✅ **External dependencies are installed**

## Installed Dependencies

The following packages are required and have been installed:

- `langchain>=1.0.0` - Main LangChain library (v1.2.0 installed)
- `langchain-core>=1.0.0` - Core LangChain components (v1.2.6 installed)

## Verification

All core dependencies are available:
- ✅ `create_agent` from `langchain.agents`
- ✅ `AgentMiddleware` from `langchain.agents.middleware`
- ✅ `BaseChatModel` from `langchain_core.language_models`

## Missing Custom Modules

⚠️ **Note**: `AgentSkill.py` uses relative imports for custom modules that don't exist yet:

```python
from .core import SkillRegistry, SkillState, SkillMetadata
from .core.state import SkillStateAccumulative, SkillStateFIFO
from .middleware import SkillMiddleware
from .config import SkillSystemConfig, load_config
from .utils import setup_logger, generate_system_prompt
```

These modules need to be created for the file to work:
- `core/__init__.py` - Contains `SkillRegistry`, `SkillState`, `SkillMetadata`
- `core/state.py` - Contains `SkillStateAccumulative`, `SkillStateFIFO`
- `middleware.py` - Contains `SkillMiddleware`
- `config.py` - Contains `SkillSystemConfig`, `load_config`
- `utils.py` - Contains `setup_logger`, `generate_system_prompt`

## Installation

To install dependencies:

```bash
pip install -r requirements_agentskill.txt
```

Or manually:

```bash
pip install langchain langchain-core
```

## Optional Dependencies

For different LLM providers, you may also need:

```bash
# OpenAI
pip install langchain-openai

# Anthropic
pip install langchain-anthropic

# Community models (ChatTongyi, etc.)
pip install langchain-community
```

## Usage

Once the custom modules are created, you can use `AgentSkill.py` like this:

```python
from langchain_openai import ChatOpenAI
from AgentSkill import create_skill_agent

# Create agent
model = ChatOpenAI(model="gpt-4")
agent = create_skill_agent(model=model)

# Use agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "Your question"}]
})
```
