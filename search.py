import os
from typing import Literal
from pathlib import Path
from dotenv import load_dotenv
from tavily import TavilyClient
from deepagents import create_deep_agent
from langchain_community.chat_models import ChatTongyi

# Load environment variables from .env file if it exists
# Use override=True to ensure .env file values take precedence over system environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    # Also try loading from current directory as fallback
    load_dotenv(dotenv_path=".env", override=True)

def get_env(key: str, default: str = None) -> str:
    """Get environment variable from .env file (loaded into os.environ) or system env"""
    value = os.environ.get(key)
    if value is None:
        return default
    return value

tavily_client = TavilyClient(api_key=get_env("TAVILY_API_KEY"))

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


# System prompt to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

# Configure DashScope DeepSeek model
# Loads from .env file first, then falls back to os.environ
# Available DeepSeek models on DashScope:
# - "deepseek-v3" (chat model - recommended)
# - "deepseek-r1" (reasoning model)
# Add DASHSCOPE_API_KEY and optionally DASHSCOPE_MODEL to .env file
deepseek_model = ChatTongyi(
    model=get_env("DASHSCOPE_MODEL", "deepseek-v3"),  # Default to deepseek-v3
    api_key=get_env("DASHSCOPE_API_KEY")
)

agent = create_deep_agent(
    model=deepseek_model,
    tools=[internet_search],
    system_prompt=research_instructions
)

# system, user, 

result = agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})

# Print the agent's response
print(result["messages"][-1].content)