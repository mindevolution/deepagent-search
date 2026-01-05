# 快速优化实施指南

基于性能分析建议（465-479行），本指南提供快速实施方案。

## 代码级优化（已部分实施）

### ✅ 已完成的优化

1. **使用 `__slots__`** - 已在 `TimedChatTongyi` 类中实施
2. **优化字符串操作** - 已避免创建大型临时字符串
3. **属性缓存** - 已实施属性缓存机制

### 🔄 可进一步优化的地方

#### 1. 优化搜索缓存实现

**当前实现：**
```python
_search_cache = {}
```

**优化后：**
```python
from collections import deque

class OptimizedSearchCache:
    __slots__ = ('_cache', '_max_size', '_access_order')
    
    def __init__(self, max_size=50):
        self._cache = {}
        self._max_size = max_size
        self._access_order = deque(maxlen=max_size)
    
    def get(self, key):
        if key in self._cache:
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None
    
    def set(self, key, value):
        if len(self._cache) >= self._max_size:
            oldest = self._access_order.popleft()
            del self._cache[oldest]
        self._cache[key] = value
        self._access_order.append(key)

_search_cache = OptimizedSearchCache(max_size=50)
```

**在 `internet_search` 中使用：**
```python
# 替换
if cache_key in _search_cache:
    return _search_cache[cache_key]

# 为
cached_result = _search_cache.get(cache_key)
if cached_result:
    return cached_result

# 替换
_search_cache[cache_key] = result

# 为
_search_cache.set(cache_key, result)
```

#### 2. 使用生成器优化 token 计算

已在 `TimedChatTongyi.invoke` 中实施，无需修改。

#### 3. 减少字典复制

在消息处理中避免不必要的复制：

```python
# 如果可能，直接修改而不是复制
# 注意：需要确保不影响原始数据
```

## 运行时优化

### 1. 使用 Python -O 标志

**运行方式：**
```bash
# 基本优化
python -O search.py

# 移除文档字符串
python -OO search.py
```

**在代码中检测：**
```python
if __debug__:
    # Debug 模式代码
    pass
else:
    # 优化模式代码（-O 标志）
    pass
```

### 2. 使用 PyPy（如果可用）

**安装 PyPy：**
```bash
# macOS
brew install pypy3

# 或下载：https://www.pypy.org/download.html
```

**运行：**
```bash
pypy3 search.py
```

**注意：** 确保所有依赖都兼容 PyPy。

### 3. 启用连接池（如果使用 HTTP 客户端）

如果 Tavily 客户端支持，可以配置连接池：

```python
# 检查 tavily 客户端是否支持连接池配置
# 如果支持，在初始化时配置
```

## 配置优化

### 1. 限制消息历史

**在系统提示中明确：**
```python
research_instructions = """You are an expert researcher. Conduct research efficiently.

IMPORTANT: Keep conversation history minimal. Only include essential context.

You have access to an internet search tool. Use it strategically:
- Search once or twice maximum for the query
- Use max_results=3 (default) for faster results
- Provide a direct, well-structured answer based on the search results
- Be concise but comprehensive
"""
```

### 2. 优化系统提示长度

**当前提示：** 约 150 字符
**优化后：** 可以进一步缩短到 100 字符以内

```python
research_instructions = """Expert researcher. Search efficiently (1-2 times, max_results=3). Provide concise, accurate answers."""
```

### 3. 检查是否可以禁用未使用的功能

**检查 deepagents 文档：**
```python
# 查看 create_deep_agent 的参数
# 看是否可以禁用某些默认功能
# 例如：filesystem tools, subagents, todo features

# 如果支持，可以这样配置：
agent = create_deep_agent(
    model=deepseek_model,
    tools=[internet_search],
    system_prompt=research_instructions,
    # 如果支持，可以添加：
    # disable_default_tools=True,  # 禁用默认工具
    # middleware=[],  # 空中间件列表
)
```

## 快速实施清单

### 立即可以做的（5分钟）

- [ ] 使用 `python -O search.py` 运行
- [ ] 缩短系统提示词
- [ ] 在系统提示中明确限制消息历史

### 需要代码修改的（15分钟）

- [ ] 实施优化的搜索缓存类
- [ ] 检查是否可以禁用未使用的 agent 功能
- [ ] 添加连接池配置（如果支持）

### 需要环境配置的（30分钟）

- [ ] 安装并测试 PyPy
- [ ] 配置性能分析工具
- [ ] 设置持续性能监控

## 性能测试

### 测试优化效果

```bash
# 优化前
python search.py > output_before.txt 2>&1

# 优化后（使用 -O 标志）
python -O search.py > output_after.txt 2>&1

# 对比执行时间
grep "Execution time" output_*.txt
```

### 使用性能分析

```python
# 在 search.py 中添加
import cProfile
import pstats

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 原有代码
    result = agent.invoke(...)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # 显示前20个最耗时的函数
```

## 预期效果

根据优化类型：

| 优化类型 | 预期提升 | 实施难度 |
|---------|---------|---------|
| Python -O 标志 | 5-15% | ⭐ 极简单 |
| 优化缓存类 | 10-20% | ⭐⭐ 简单 |
| 缩短系统提示 | 5-10% | ⭐ 极简单 |
| 限制消息历史 | 10-30% | ⭐⭐ 简单 |
| PyPy | 50-200% | ⭐⭐⭐ 中等 |
| 禁用未使用功能 | 10-25% | ⭐⭐⭐ 中等 |

## 注意事项

1. **测试兼容性**
   - 使用 PyPy 前确保所有依赖兼容
   - 某些 C 扩展可能不兼容

2. **功能完整性**
   - 优化不应影响功能
   - 每次优化后都要测试

3. **可维护性**
   - 保持代码可读性
   - 添加注释说明优化原因

## 参考文件

- `optimization_examples.py` - 详细代码示例
- `SYSTEM_OVERHEAD_OPTIMIZATION.md` - 完整优化指南
- `OPTIMIZATION.md` - 总体优化文档

