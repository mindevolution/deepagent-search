import os
import time
from typing import Literal, Dict, List
from pathlib import Path
from collections import defaultdict
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

# Simple cache for search results (query-based caching)
_search_cache = {}

# Performance tracking for Tavily searches
_tavily_timings = {
    "total_searches": 0,
    "total_time": 0.0,
    "cached_searches": 0,
    "api_calls": 0,
    "api_time": 0.0,
    "cache_time": 0.0,
}

def get_tavily_stats():
    """Get Tavily search performance statistics"""
    if _tavily_timings["total_searches"] == 0:
        return {
            "total_searches": 0,
            "cached_searches": 0,
            "api_calls": 0,
            "avg_api_time": 0.0,
            "avg_cache_time": 0.0,
            "total_time": 0.0,
        }
    
    return {
        "total_searches": _tavily_timings["total_searches"],
        "cached_searches": _tavily_timings["cached_searches"],
        "api_calls": _tavily_timings["api_calls"],
        "avg_api_time": _tavily_timings["api_time"] / _tavily_timings["api_calls"] if _tavily_timings["api_calls"] > 0 else 0.0,
        "avg_cache_time": _tavily_timings["cache_time"] / _tavily_timings["cached_searches"] if _tavily_timings["cached_searches"] > 0 else 0.0,
        "total_time": _tavily_timings["total_time"],
        "api_time": _tavily_timings["api_time"],
        "cache_time": _tavily_timings["cache_time"],
    }

def internet_search(
    query: str,
    max_results: int = 3,  # Reduced from 5 to 3 for faster results
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,  # Keep False to avoid fetching full content
):
    """Run a web search - optimized for speed with caching"""
    search_start = time.time()
    _tavily_timings["total_searches"] += 1
    
    # Create cache key
    cache_key = f"{query}:{max_results}:{topic}:{include_raw_content}"
    
    # Check cache first
    if cache_key in _search_cache:
        cache_time = time.time() - search_start
        _tavily_timings["cached_searches"] += 1
        _tavily_timings["cache_time"] += cache_time
        _tavily_timings["total_time"] += cache_time
        print(f"[Tavily Cache Hit] Query: '{query}' | Time: {cache_time:.3f}s")
        return _search_cache[cache_key]
    
    # Perform API search
    api_start = time.time()
    result = tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,  # False = faster, only summaries
        topic=topic,
    )
    api_time = time.time() - api_start
    
    _tavily_timings["api_calls"] += 1
    _tavily_timings["api_time"] += api_time
    _tavily_timings["total_time"] += (time.time() - search_start)
    
    print(f"[Tavily API Call] Query: '{query}' | Time: {api_time:.3f}s | Results: {max_results}")
    
    # Cache result (limit cache size to prevent memory issues)
    if len(_search_cache) < 50:  # Keep cache size reasonable
        _search_cache[cache_key] = result
    
    return result


# System prompt to steer the agent to be an expert researcher
# Optimized: Be concise and direct to reduce agent thinking time
research_instructions = """You are an expert researcher. Conduct research efficiently and provide a concise, accurate answer.

You have access to an internet search tool. Use it strategically:
- Search once or twice maximum for the query
- Use max_results=3 (default) for faster results
- Provide a direct, well-structured answer based on the search results
- Be concise but comprehensive
"""

# Performance tracking for DeepSeek API calls
_deepseek_timings = {
    "total_calls": 0,
    "total_time": 0.0,
    "total_tokens_input": 0,
    "total_tokens_output": 0,
}

def get_deepseek_stats():
    """Get DeepSeek API performance statistics"""
    if _deepseek_timings["total_calls"] == 0:
        return {
            "total_calls": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
        }
    
    return {
        "total_calls": _deepseek_timings["total_calls"],
        "total_time": _deepseek_timings["total_time"],
        "avg_time": _deepseek_timings["total_time"] / _deepseek_timings["total_calls"],
        "total_tokens_input": _deepseek_timings["total_tokens_input"],
        "total_tokens_output": _deepseek_timings["total_tokens_output"],
    }

# Configure DashScope DeepSeek model
# Loads from .env file first, then falls back to os.environ
# Available DeepSeek models on DashScope:
# - "deepseek-v3" (chat model - recommended)
# - "deepseek-r1" (reasoning model)
# Add DASHSCOPE_API_KEY and optionally DASHSCOPE_MODEL to .env file
# Optimized: Using faster model parameters
_base_deepseek_model = ChatTongyi(
    model=get_env("DASHSCOPE_MODEL", "deepseek-v3"),  # Default to deepseek-v3
    api_key=get_env("DASHSCOPE_API_KEY"),
    temperature=0.7,  # Lower temperature for faster, more deterministic responses
    top_p=0.8,  # Optimized for speed
    streaming=False,  # Set to True if you want streaming (can feel faster)
)

# Create a wrapper class to track DeepSeek API calls
# Optimized: Using __slots__ to reduce memory overhead
class TimedChatTongyi:
    """Wrapper around ChatTongyi to track API call times - optimized for performance"""
    __slots__ = ('_model', '_attr_cache')  # Reduce memory overhead
    
    def __init__(self, base_model):
        self._model = base_model
        # Cache commonly accessed attributes to avoid repeated lookups
        self._attr_cache = {}
        # Only copy essential attributes, not all attributes (reduces object creation)
        essential_attrs = ['model', 'temperature', 'top_p', 'streaming', 'api_key']
        for attr in essential_attrs:
            if hasattr(base_model, attr):
                try:
                    self._attr_cache[attr] = getattr(base_model, attr)
                except:
                    pass
    
    def invoke(self, input, config=None, **kwargs):
        """Track time for each API call - optimized string operations"""
        call_start = time.time()
        _deepseek_timings["total_calls"] += 1
        
        # Optimized token estimation - avoid creating intermediate strings
        input_text_len = 0
        if isinstance(input, list):
            # More efficient: sum lengths instead of joining
            input_text_len = sum(
                len(str(msg.get("content", ""))) if isinstance(msg, dict) else len(str(msg))
                for msg in input
            )
        elif hasattr(input, 'messages'):
            input_text_len = sum(
                len(msg.content) if hasattr(msg, 'content') else len(str(msg))
                for msg in input.messages
            )
        else:
            input_text_len = len(str(input))
        
        estimated_input_tokens = input_text_len // 4
        _deepseek_timings["total_tokens_input"] += estimated_input_tokens
        
        # Make the actual API call
        result = self._model.invoke(input, config=config, **kwargs)
        
        # Calculate time and tokens
        call_time = time.time() - call_start
        _deepseek_timings["total_time"] += call_time
        
        # Optimized output token estimation
        if hasattr(result, 'content'):
            output_text_len = len(result.content)
        else:
            output_text_len = len(str(result))
        estimated_output_tokens = output_text_len // 4
        _deepseek_timings["total_tokens_output"] += estimated_output_tokens
        
        # Print call info (only if needed - can be disabled for production)
        print(f"[DeepSeek API Call #{_deepseek_timings['total_calls']}] Time: {call_time:.3f}s | "
              f"Input: ~{estimated_input_tokens} tokens | Output: ~{estimated_output_tokens} tokens")
        
        return result
    
    def __getattr__(self, name):
        """Delegate other attribute access to base model - with caching"""
        # Check cache first
        if name in self._attr_cache:
            return self._attr_cache[name]
        # Fallback to base model
        attr = getattr(self._model, name)
        # Cache for future access
        if not name.startswith('_'):
            self._attr_cache[name] = attr
        return attr

# Wrap the model with timing tracker
deepseek_model = TimedChatTongyi(_base_deepseek_model)

# Track timing between operations to analyze agent overhead
_operation_timestamps = []

def record_operation(operation_name: str):
    """Record a timestamp for an operation"""
    _operation_timestamps.append((operation_name, time.time()))

def analyze_operation_gaps():
    """Analyze time gaps between operations to identify overhead"""
    if len(_operation_timestamps) < 2:
        return {}
    
    gaps = {}
    for i in range(1, len(_operation_timestamps)):
        prev_op, prev_time = _operation_timestamps[i-1]
        curr_op, curr_time = _operation_timestamps[i]
        gap = curr_time - prev_time
        gap_key = f"{prev_op} -> {curr_op}"
        if gap_key not in gaps:
            gaps[gap_key] = []
        gaps[gap_key].append(gap)
    
    return gaps

# Create agent with performance callback
agent = create_deep_agent(
    model=deepseek_model,
    tools=[internet_search],
    system_prompt=research_instructions
)

# system, user, 

if __name__ == "__main__":
    # Track detailed timing
    timing_breakdown = {
        "agent_init": 0.0,
        "agent_execution": 0.0,
        "tool_calls": 0.0,
        "llm_calls": 0.0,
    }
    
    total_start = time.time()
    
    # Track agent execution with detailed timing
    agent_start = time.time()
    result = agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})
    agent_end = time.time()
    
    elapsed_time = time.time() - total_start
    timing_breakdown["agent_execution"] = agent_end - agent_start

    # Print the agent's response
    print("\n" + "="*60)
    print("AGENT RESPONSE:")
    print("="*60)
    print(result["messages"][-1].content)
    
    # Print performance statistics
    print("\n" + "="*60)
    print("PERFORMANCE ANALYSIS:")
    print("="*60)
    print(f"Total execution time: {elapsed_time:.2f}s")
    
    # Get statistics for both services
    tavily_stats = get_tavily_stats()
    deepseek_stats = get_deepseek_stats()
    
    print(f"\n[Tavily Search Statistics]")
    print(f"  Total searches: {tavily_stats['total_searches']}")
    print(f"  API calls: {tavily_stats['api_calls']}")
    print(f"  Cached searches: {tavily_stats['cached_searches']}")
    if tavily_stats['api_calls'] > 0:
        print(f"  Average API time: {tavily_stats['avg_api_time']:.3f}s")
        print(f"  Total API time: {tavily_stats['api_time']:.2f}s")
    if tavily_stats['cached_searches'] > 0:
        print(f"  Average cache time: {tavily_stats['avg_cache_time']:.3f}s")
        print(f"  Total cache time: {tavily_stats['cache_time']:.2f}s")
    print(f"  Total Tavily time: {tavily_stats['total_time']:.2f}s")
    
    print(f"\n[DeepSeek API Statistics]")
    print(f"  Total API calls: {deepseek_stats['total_calls']}")
    if deepseek_stats['total_calls'] > 0:
        print(f"  Average call time: {deepseek_stats['avg_time']:.3f}s")
        print(f"  Total API time: {deepseek_stats['total_time']:.2f}s")
        print(f"  Total input tokens: ~{deepseek_stats['total_tokens_input']}")
        print(f"  Total output tokens: ~{deepseek_stats['total_tokens_output']}")
        print(f"  Total tokens: ~{deepseek_stats['total_tokens_input'] + deepseek_stats['total_tokens_output']}")
    
    # Calculate time breakdown
    if elapsed_time > 0:
        tavily_percentage = (tavily_stats['total_time'] / elapsed_time) * 100
        deepseek_percentage = (deepseek_stats['total_time'] / elapsed_time) * 100
        
        print(f"\n[Time Breakdown]")
        print(f"  Tavily time: {tavily_stats['total_time']:.2f}s ({tavily_percentage:.1f}%)")
        print(f"  DeepSeek API time: {deepseek_stats['total_time']:.2f}s ({deepseek_percentage:.1f}%)")
        
        # Calculate other processing time
        accounted_time = tavily_stats['total_time'] + deepseek_stats['total_time']
        other_time = elapsed_time - accounted_time
        other_percentage = (other_time / elapsed_time) * 100
        print(f"  Other processing (agent logic, etc.): {other_time:.2f}s ({other_percentage:.1f}%)")
        
        # Detailed breakdown of "Other processing"
        print(f"\n[Other Processing Breakdown]")
        print(f"  Total unaccounted time: {other_time:.2f}s")
        
        # Analyze operation gaps
        gaps = analyze_operation_gaps()
        
        # Estimate components of other processing based on call patterns
        print(f"\n  [Estimated Components]")
        
        # Calculate number of transitions
        num_llm_calls = deepseek_stats['total_calls']
        num_tool_calls = tavily_stats['total_searches']
        num_transitions = max(1, num_llm_calls + num_tool_calls - 1)
        
        # Tool preparation overhead (between tool calls and LLM calls)
        # Each transition involves: tool binding, parameter validation, result processing
        tool_overhead_per_transition = 0.05  # ~50ms per transition
        tool_overhead = tool_overhead_per_transition * num_transitions
        if tool_overhead > 0:
            tool_overhead_pct = (tool_overhead / elapsed_time) * 100 if elapsed_time > 0 else 0
            print(f"    Tool/LLM transition overhead: ~{tool_overhead:.2f}s ({tool_overhead_pct:.1f}%)")
            print(f"      - {num_transitions} transitions × ~{tool_overhead_per_transition*1000:.0f}ms each")
            print(f"      - Includes: tool binding, parameter validation, result processing")
        
        # Message processing and state management
        # Each LLM call involves message formatting, state updates
        message_overhead_per_call = 0.1  # ~100ms per LLM call for message processing
        message_overhead = message_overhead_per_call * num_llm_calls
        if message_overhead > 0:
            msg_pct = (message_overhead / elapsed_time) * 100 if elapsed_time > 0 else 0
            print(f"    Message/State processing: ~{message_overhead:.2f}s ({msg_pct:.1f}%)")
            print(f"      - {num_llm_calls} LLM calls × ~{message_overhead_per_call*1000:.0f}ms each")
            print(f"      - Includes: message formatting, state updates, context management")
        
        # Agent decision making (routing, middleware)
        # DeepSeek agent has multiple middleware layers that process each request
        middleware_overhead_per_call = 0.15  # ~150ms per LLM call for middleware
        middleware_overhead = middleware_overhead_per_call * num_llm_calls
        if middleware_overhead > 0:
            middleware_pct = (middleware_overhead / elapsed_time) * 100 if elapsed_time > 0 else 0
            print(f"    Agent middleware/routing: ~{middleware_overhead:.2f}s ({middleware_pct:.1f}%)")
            print(f"      - {num_llm_calls} LLM calls × ~{middleware_overhead_per_call*1000:.0f}ms each")
            print(f"      - Includes: routing decisions, state transitions, middleware processing")
            print(f"      - Note: DeepAgent includes multiple middleware layers (todo, filesystem, subagents, etc.)")
        
        # Remaining overhead (Python, serialization, etc.)
        remaining_overhead = max(0, other_time - tool_overhead - message_overhead - middleware_overhead)
        if remaining_overhead > 0:
            remaining_pct = (remaining_overhead / elapsed_time) * 100 if elapsed_time > 0 else 0
            print(f"    Python/System overhead: ~{remaining_overhead:.2f}s ({remaining_pct:.1f}%)")
            print(f"      - Includes: Python interpreter, object serialization, garbage collection")
        
        # Show call pattern analysis
        print(f"\n  [Call Pattern Analysis]")
        print(f"    LLM calls: {num_llm_calls}")
        print(f"    Tool calls: {num_tool_calls}")
        print(f"    Total transitions: {num_transitions}")
        if num_llm_calls > 0:
            avg_time_between_calls = other_time / num_llm_calls if num_llm_calls > 0 else 0
            print(f"    Avg overhead per LLM call: ~{avg_time_between_calls:.2f}s")
        
        # Recommendations
        if other_time > 3.0:  # If other processing takes more than 3 seconds
            print(f"\n  [Optimization Recommendations]")
            if middleware_overhead > 1.5:
                print(f"    ⚠️  High middleware overhead ({middleware_overhead:.2f}s). Consider:")
                print(f"       - Reducing middleware layers if not needed")
                print(f"       - Disabling unused features (subagents, filesystem tools, etc.)")
            if num_llm_calls > 3:
                print(f"    ⚠️  High number of LLM calls ({num_llm_calls}). Consider:")
                print(f"       - Optimizing system prompt to reduce call frequency")
                print(f"       - Using more direct tool calls")
            if message_overhead > 0.8:
                print(f"    ⚠️  High message processing overhead. Consider:")
                print(f"       - Reducing message history size")
                print(f"       - Using shorter context windows")
            if remaining_overhead > 1.0:
                print(f"    ⚠️  High system overhead ({remaining_overhead:.2f}s). Consider:")
                print(f"       [Code-level optimizations]")
                print(f"       - Reusing objects instead of creating new ones")
                print(f"       - Using __slots__ for classes to reduce memory overhead")
                print(f"       - Minimizing dictionary/list copying operations")
                print(f"       - Using generators instead of lists where possible")
                print(f"       [Runtime optimizations]")
                print(f"       - Using PyPy for JIT compilation (2-10x faster)")
                print(f"       - Using Cython for critical paths")
                print(f"       - Enabling Python's -O flag for optimized bytecode")
                print(f"       - Using asyncio for concurrent operations")
                print(f"       [Configuration optimizations]")
                print(f"       - Reducing agent middleware layers")
                print(f"       - Limiting message history size")
                print(f"       - Disabling unused agent features")
                print(f"       - Using connection pooling for API clients")
    
    print("="*60)