import os
from typing import Literal
from pathlib import Path
from dotenv import load_dotenv
from tavily import TavilyClient
from deepagents import create_deep_agent
from langchain_community.chat_models import ChatTongyi
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
import uuid

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

# Simple cache for search results (query-based caching)
_search_cache = {}

def internet_search(
    query: str,
    max_results: int = 3,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search with caching"""
    # Create cache key
    cache_key = f"{query}:{max_results}:{topic}:{include_raw_content}"
    
    # Check cache first
    if cache_key in _search_cache:
        return _search_cache[cache_key]
    
    # Perform API search
    result = tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    
    # Cache result (limit cache size to prevent memory issues)
    if len(_search_cache) < 50:
        _search_cache[cache_key] = result
    
    return result

deepseek_model = ChatTongyi(
    model=get_env("DASHSCOPE_MODEL", "deepseek-v3"),  # Default to deepseek-v3
    api_key=get_env("DASHSCOPE_API_KEY"),
    temperature=0.7,
    top_p=0.8,
    streaming=False,
)

checkpointer = MemorySaver()

# Create store instance and keep reference for manual access
store = InMemoryStore()

def make_backend(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),  # Ephemeral storage
        routes={
            "/memories/": StoreBackend(runtime)  # Persistent storage
        }
    )

# Create agent
agent = create_deep_agent(
    store=store,  # Required for StoreBackend
    backend=make_backend,
    checkpointer=checkpointer,
    model=deepseek_model,
    tools=[internet_search],
    system_prompt="""You have a file at /memories/instructions.txt with additional
    instructions and preferences.

    Read this file at the start of conversations to understand user preferences.

    When users provide feedback like "please always do X" or "I prefer Y",
    update /memories/instructions.txt using the edit_file tool."""
)

if __name__ == "__main__":
    # Thread 1: Write to long-term memory
    config1 = {"configurable": {"thread_id": str(uuid.uuid4())}}

    agent.invoke({
        "messages": [{"role": "user", "content": "Save my preferences to /memories/preferences.txt"}]
    }, config=config1)

    # Print the agent's response
    # INSERT_YOUR_CODE
    def print_agent_response(result):
        print("\n" + "="*60)
        print("AGENT RESPONSE:")
        print("="*60)
        print(result["messages"][-1].content)
        print("="*60)
    
    # Conversation 1: Learn about a project
    result = agent.invoke({
        "messages": [{"role": "user", "content": "We're building a web app with React. Save project notes."}]
    }, config=config1)
    print_agent_response(result)

    # Conversation 2: Use that knowledge
    result = agent.invoke({
        "messages": [{"role": "user", "content": "What framework are we using?"}]
    }, config=config1)
    print_agent_response(result)
    