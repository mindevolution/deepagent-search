"""
优化实施示例
展示如何应用代码级、运行时和配置级优化
"""

import os
import time
from typing import Literal
from functools import lru_cache
from collections import deque  # 使用 deque 代替 list 用于高效追加

# ============================================================================
# 代码级优化示例
# ============================================================================

# 1. 使用 __slots__ 减少内存开销
class OptimizedSearchCache:
    """优化的搜索缓存类 - 使用 __slots__"""
    __slots__ = ('_cache', '_max_size', '_access_order')
    
    def __init__(self, max_size=50):
        self._cache = {}
        self._max_size = max_size
        self._access_order = deque(maxlen=max_size)  # 使用 deque 代替 list
    
    def get(self, key):
        if key in self._cache:
            # 更新访问顺序（deque 自动处理大小限制）
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None
    
    def set(self, key, value):
        if len(self._cache) >= self._max_size:
            # 移除最旧的项
            oldest = self._access_order.popleft()
            del self._cache[oldest]
        self._cache[key] = value
        self._access_order.append(key)


# 2. 重用对象而不是创建新对象
class ObjectPool:
    """对象池 - 重用对象减少创建开销"""
    def __init__(self, factory, max_size=10):
        self._factory = factory
        self._pool = deque(maxlen=max_size)
        self._max_size = max_size
    
    def acquire(self):
        """获取对象（从池中或创建新对象）"""
        if self._pool:
            return self._pool.popleft()
        return self._factory()
    
    def release(self, obj):
        """释放对象回池中"""
        if len(self._pool) < self._max_size:
            # 重置对象状态
            if hasattr(obj, 'reset'):
                obj.reset()
            self._pool.append(obj)


# 3. 最小化字典/列表复制操作
def optimized_message_processing(messages):
    """优化的消息处理 - 避免不必要的复制"""
    # ❌ 不好的做法：创建新列表
    # processed = list(messages)
    # processed.append(new_msg)
    
    # ✅ 好的做法：如果可能，直接修改
    # 或者使用生成器
    def process_messages():
        for msg in messages:
            # 处理消息但不复制
            yield process_single_message(msg)
    
    return list(process_messages())  # 只在需要时转换为列表


def process_single_message(msg):
    """处理单个消息"""
    # 避免创建中间字典
    if isinstance(msg, dict):
        # 直接访问，不复制
        return {
            'role': msg.get('role'),
            'content': msg.get('content', '')[:1000]  # 限制长度
        }
    return msg


# 4. 使用生成器代替列表
def optimized_token_estimation(messages):
    """优化的 token 估算 - 使用生成器"""
    # ❌ 不好的做法：创建完整字符串
    # text = " ".join(str(msg.get("content", "")) for msg in messages)
    # tokens = len(text) // 4
    
    # ✅ 好的做法：直接计算长度
    total_length = sum(
        len(str(msg.get("content", ""))) if isinstance(msg, dict) else len(str(msg))
        for msg in messages
    )
    return total_length // 4


# 5. 缓存计算结果
@lru_cache(maxsize=100)
def cached_search_key(query: str, max_results: int, topic: str) -> str:
    """缓存的搜索键生成"""
    return f"{query}:{max_results}:{topic}"


# ============================================================================
# 运行时优化示例
# ============================================================================

# 1. 使用 Python -O 标志的说明
"""
运行优化：
python -O search.py  # 基本优化
python -OO search.py  # 移除文档字符串

在代码中检查优化模式：
if __debug__:
    print("Debug mode")
else:
    print("Optimized mode (-O flag)")
"""

# 2. 连接池示例（用于 API 客户端）
try:
    import httpx
    
    # 创建连接池
    _http_client = None
    
    def get_http_client():
        """获取或创建 HTTP 客户端（连接池）"""
        global _http_client
        if _http_client is None:
            _http_client = httpx.Client(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
            )
        return _http_client
    
    def close_http_client():
        """关闭 HTTP 客户端"""
        global _http_client
        if _http_client is not None:
            _http_client.close()
            _http_client = None

except ImportError:
    # httpx 不可用时使用默认实现
    def get_http_client():
        return None


# 3. 异步操作示例
try:
    import asyncio
    import aiohttp
    
    async def async_search_queries(queries):
        """异步执行多个搜索查询"""
        async with aiohttp.ClientSession() as session:
            tasks = [async_single_search(session, query) for query in queries]
            results = await asyncio.gather(*tasks)
            return results
    
    async def async_single_search(session, query):
        """单个异步搜索"""
        # 实现异步搜索逻辑
        pass

except ImportError:
    pass


# ============================================================================
# 配置优化示例
# ============================================================================

# 1. 限制消息历史大小
def limit_message_history(messages, max_messages=10):
    """限制消息历史大小"""
    if len(messages) <= max_messages:
        return messages
    
    # 保留系统消息和最近的 N 条消息
    system_messages = [msg for msg in messages if msg.get('role') == 'system']
    other_messages = [msg for msg in messages if msg.get('role') != 'system']
    
    # 只保留最近的 N 条非系统消息
    recent_messages = other_messages[-max_messages:]
    
    return system_messages + recent_messages


# 2. 优化的系统提示（更短更直接）
OPTIMIZED_SYSTEM_PROMPT = """You are a research assistant. Answer concisely.

Search tool usage:
- Use max_results=3
- Search 1-2 times max
- Provide direct answers"""


# 3. 优化的 agent 配置
def create_optimized_agent(model, tools, system_prompt=None):
    """创建优化的 agent（如果 deepagents 支持）"""
    # 注意：实际参数取决于 deepagents 的 API
    # 这里展示可能的优化配置
    
    agent_config = {
        'model': model,
        'tools': tools,
    }
    
    if system_prompt:
        agent_config['system_prompt'] = system_prompt
    
    # 如果支持，可以禁用某些功能
    # agent_config['disable_features'] = ['filesystem', 'subagents']  # 示例
    
    # 如果支持，限制消息历史
    # agent_config['max_message_history'] = 10  # 示例
    
    return agent_config


# ============================================================================
# 性能监控工具
# ============================================================================

def profile_code(func):
    """性能分析装饰器"""
    import cProfile
    import pstats
    from io import StringIO
    
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        # 输出性能统计
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # 显示前20个最耗时的函数
        print(s.getvalue())
        
        return result
    
    return wrapper


# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    # 示例：使用优化的缓存
    cache = OptimizedSearchCache(max_size=50)
    cache.set("test_key", "test_value")
    print(f"Cached value: {cache.get('test_key')}")
    
    # 示例：限制消息历史
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Message 1"},
        {"role": "user", "content": "Message 2"},
        # ... 更多消息
    ]
    limited = limit_message_history(messages, max_messages=5)
    print(f"Limited messages: {len(limited)}")
    
    # 示例：优化的 token 估算
    token_count = optimized_token_estimation(messages)
    print(f"Estimated tokens: {token_count}")

