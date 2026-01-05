# Search.py 性能优化文档

## 优化概述

本文档记录了针对 `search.py` 的性能优化措施，目标是将搜索执行时间从 16 秒优化到更快的响应时间。

## 优化措施

### 1. 减少搜索结果数量

**优化前：**
```python
max_results: int = 5
```

**优化后：**
```python
max_results: int = 3  # Reduced from 5 to 3 for faster results
```

**效果：** 减少 API 响应时间和数据传输量，预计节省 1-2 秒

---

### 2. 禁用原始内容获取

**优化：**
```python
include_raw_content: bool = False  # Keep False to avoid fetching full content
```

**说明：** 只获取搜索结果摘要，不获取完整网页内容，大幅减少数据传输和处理时间

**效果：** 预计节省 2-3 秒

---

### 3. 添加搜索缓存机制

**实现：**
```python
# Simple cache for search results (query-based caching)
_search_cache = {}

def internet_search(...):
    cache_key = f"{query}:{max_results}:{topic}:{include_raw_content}"
    
    # Check cache first
    if cache_key in _search_cache:
        return _search_cache[cache_key]
    
    # Perform search and cache result
    result = tavily_client.search(...)
    if len(_search_cache) < 50:  # Keep cache size reasonable
        _search_cache[cache_key] = result
    
    return result
```

**效果：**
- 首次查询：正常速度
- 重复查询：预计从 16s 降至 2-4s（缓存命中）

---

### 4. 优化系统提示词

**优化前：**
```
You are an expert researcher. Your job is to conduct thorough research and then write a polished report.
```

**优化后：**
```
You are an expert researcher. Conduct research efficiently and provide a concise, accurate answer.

You have access to an internet search tool. Use it strategically:
- Search once or twice maximum for the query
- Use max_results=3 (default) for faster results
- Provide a direct, well-structured answer based on the search results
- Be concise but comprehensive
```

**效果：** 引导 agent 减少不必要的搜索和思考时间，预计节省 1-2 秒

---

### 5. 优化模型参数

**配置：**
```python
deepseek_model = ChatTongyi(
    model=get_env("DASHSCOPE_MODEL", "deepseek-v3"),
    api_key=get_env("DASHSCOPE_API_KEY"),
    temperature=0.7,  # Lower temperature for faster, more deterministic responses
    top_p=0.8,  # Optimized for speed
    streaming=False,  # Set to True if you want streaming (can feel faster)
)
```

**参数说明：**
- `temperature=0.7`：降低温度值，生成更快、更确定的响应
- `top_p=0.8`：优化采样策略，平衡速度和质量

**效果：** 预计节省 1-2 秒

---

### 6. 添加执行时间监控

**实现：**
```python
if __name__ == "__main__":
    start_time = time.time()
    result = agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})
    elapsed_time = time.time() - start_time
    
    print(result["messages"][-1].content)
    print(f"\n[Execution time: {elapsed_time:.2f}s]")
```

**效果：** 便于监控和评估优化效果

---

## 性能预期

### 首次查询
- **优化前：** ~16 秒
- **优化后：** 预计 10-12 秒
- **提升：** 约 25-37% 的性能提升

### 重复查询（缓存命中）
- **优化前：** ~16 秒
- **优化后：** 预计 2-4 秒
- **提升：** 约 75-87% 的性能提升

---

## 进一步优化建议

如果还需要更快的响应速度，可以考虑以下方案：

### 1. 启用流式输出
```python
streaming=True  # 可以提升感知速度，用户感觉响应更快
```

### 2. 使用更轻量的模型
- 如果可用，尝试更快的模型变体
- 权衡速度和质量

### 3. 并行处理
- 如果 agent 需要执行多次搜索，可以考虑并行化处理
- 使用 `asyncio` 或 `concurrent.futures` 实现

### 4. 预加载和预热
- 对于常用查询，可以预先加载结果
- 在应用启动时进行模型预热

### 5. 结果摘要优化
- 如果不需要完整搜索结果，可以只获取关键信息
- 使用更简洁的结果格式

---

## 代码变更总结

### 主要修改文件
- `search.py`

### 关键变更点
1. ✅ 减少 `max_results` 默认值（5 → 3）
2. ✅ 保持 `include_raw_content=False`
3. ✅ 添加搜索缓存机制
4. ✅ 优化系统提示词，引导 agent 更高效
5. ✅ 调整模型参数（temperature, top_p）
6. ✅ 添加执行时间监控

---

## 使用说明

### 环境变量配置
确保 `.env` 文件包含：
```bash
TAVILY_API_KEY=your-tavily-key
DASHSCOPE_API_KEY=your-dashscope-key
DASHSCOPE_MODEL=deepseek-v3  # 可选，默认为 deepseek-v3
```

### 运行
```bash
python search.py
```

### 查看性能
运行后会显示执行时间：
```
[Execution time: X.XXs]
```

---

## 注意事项

1. **缓存限制：** 缓存大小限制为 50 条，防止内存占用过大
2. **结果质量：** 减少搜索结果数量可能会影响信息完整性，根据需求调整
3. **模型参数：** 降低 temperature 可能使响应更确定但可能缺乏创造性
4. **网络延迟：** 实际性能还受网络状况和 API 响应时间影响

---

## 更新日期
2025-01-04

## 版本
v1.0 - 初始优化版本

