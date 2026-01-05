# 系统开销优化指南

## 概述

当性能分析显示"Python/System overhead"较高时（通常 > 1秒），说明系统层面的开销占据了显著的时间。本文档提供详细的优化方案。

## 问题诊断

### 常见原因

1. **对象创建开销**
   - 频繁创建临时对象
   - 大量字典/列表复制操作
   - 字符串连接操作

2. **Python 解释器开销**
   - CPython 的字节码执行较慢
   - 动态类型检查开销
   - 垃圾回收暂停

3. **序列化/反序列化**
   - 消息对象的序列化
   - 状态对象的转换
   - JSON 处理

4. **内存管理**
   - 频繁的内存分配/释放
   - 对象引用追踪

## 代码级优化

### 1. 使用 `__slots__` 减少内存开销

**优化前：**
```python
class TimedChatTongyi:
    def __init__(self, base_model):
        self._model = base_model
        # 动态属性创建
```

**优化后：**
```python
class TimedChatTongyi:
    __slots__ = ('_model', '_attr_cache')  # 固定属性，减少内存
    
    def __init__(self, base_model):
        self._model = base_model
        self._attr_cache = {}
```

**效果：** 减少 30-50% 的内存使用，提升访问速度

### 2. 优化字符串操作

**优化前：**
```python
input_text = " ".join(str(msg.get("content", "")) for msg in input)
estimated_tokens = len(input_text) // 4
```

**优化后：**
```python
# 直接计算长度，避免创建中间字符串
input_text_len = sum(
    len(str(msg.get("content", ""))) if isinstance(msg, dict) else len(str(msg))
    for msg in input
)
estimated_tokens = input_text_len // 4
```

**效果：** 避免创建大型临时字符串，节省内存和时间

### 3. 属性缓存

**优化前：**
```python
def __getattr__(self, name):
    return getattr(self._model, name)  # 每次都查找
```

**优化后：**
```python
def __getattr__(self, name):
    if name in self._attr_cache:
        return self._attr_cache[name]  # 缓存查找
    attr = getattr(self._model, name)
    self._attr_cache[name] = attr
    return attr
```

**效果：** 减少重复的属性查找开销

### 4. 减少对象复制

**优化前：**
```python
result = list(messages)  # 创建新列表
result.append(new_message)
```

**优化后：**
```python
messages.append(new_message)  # 直接修改（如果可能）
# 或使用生成器
```

**效果：** 避免不必要的对象复制

### 5. 使用生成器代替列表

**优化前：**
```python
results = [process(item) for item in large_list]
```

**优化后：**
```python
results = (process(item) for item in large_list)  # 生成器
```

**效果：** 延迟计算，减少内存占用

## 运行时优化

### 1. 使用 PyPy

PyPy 使用 JIT 编译，通常比 CPython 快 2-10 倍。

**安装：**
```bash
# 使用 PyPy
pypy3 -m pip install -r requirements.txt
pypy3 search.py
```

**效果：** 2-10x 性能提升（取决于代码特性）

### 2. 使用 Python 优化标志

**运行：**
```bash
python -O search.py  # -O 优化字节码
python -OO search.py  # -OO 移除文档字符串
```

**效果：** 5-15% 性能提升

### 3. 使用 Cython

对于关键路径，使用 Cython 编译为 C 扩展。

**示例：**
```python
# performance.pyx
def fast_token_count(text):
    return len(text) // 4
```

**效果：** 关键函数 10-100x 提升

### 4. 启用 asyncio

对于 I/O 密集型操作，使用异步处理。

**示例：**
```python
import asyncio

async def async_search(query):
    # 异步搜索
    pass
```

**效果：** 并发操作时显著提升

## 配置优化

### 1. 减少中间件层

**优化前：**
```python
agent = create_deep_agent(
    model=model,
    tools=tools,
    # 默认包含多个中间件
)
```

**优化后：**
```python
# 如果不需要某些功能，可以禁用
# 注意：需要检查 deepagents 是否支持禁用中间件
```

**效果：** 减少每步的处理开销

### 2. 限制消息历史

**优化：**
```python
# 在系统提示中明确限制
research_instructions = """...
Keep conversation history minimal.
Only include essential context.
"""
```

**效果：** 减少消息处理时间

### 3. 连接池

**优化：**
```python
# 重用 HTTP 连接
import httpx

client = httpx.Client()  # 重用连接
```

**效果：** 减少连接建立开销

### 4. 禁用未使用的功能

如果不需要某些 agent 功能，考虑：
- 禁用文件系统工具
- 禁用子 agent
- 禁用 TODO 功能

## 性能监控

### 使用 cProfile

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# 运行代码
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # 显示前20个最耗时的函数
```

### 使用 line_profiler

```bash
pip install line_profiler
kernprof -l -v search.py
```

## 优化优先级

根据开销大小，优化优先级：

1. **> 5秒系统开销**
   - 考虑使用 PyPy
   - 优化关键路径代码
   - 减少中间件层

2. **2-5秒系统开销**
   - 代码级优化（__slots__, 字符串优化）
   - 属性缓存
   - 减少对象复制

3. **1-2秒系统开销**
   - 使用 Python -O 标志
   - 优化字符串操作
   - 启用连接池

4. **< 1秒系统开销**
   - 通常可以接受
   - 可以进一步微调

## 实际优化示例

### 已实施的优化

在 `search.py` 中已实施：

1. ✅ **使用 `__slots__`** - 减少 TimedChatTongyi 内存开销
2. ✅ **优化字符串操作** - 避免创建大型临时字符串
3. ✅ **属性缓存** - 缓存常用属性访问
4. ✅ **减少属性复制** - 只复制必要属性

### 预期效果

- 内存使用：减少 30-50%
- 对象创建开销：减少 20-40%
- 属性访问：提升 10-30%

## 进一步优化建议

### 如果系统开销仍然很高

1. **分析具体瓶颈**
   ```bash
   python -m cProfile -o profile.stats search.py
   python -m pstats profile.stats
   ```

2. **使用 PyPy**
   ```bash
   pypy3 search.py
   ```

3. **考虑重写关键部分**
   - 使用 Cython
   - 使用 C 扩展
   - 使用 Rust (通过 PyO3)

4. **架构优化**
   - 使用异步处理
   - 实现连接池
   - 批量处理请求

## 注意事项

1. **权衡**
   - 优化可能增加代码复杂度
   - 某些优化可能影响可读性
   - 需要测试确保功能正常

2. **测量**
   - 优化前后都要测量
   - 使用真实数据测试
   - 关注实际性能提升

3. **维护性**
   - 保持代码可读性
   - 添加注释说明优化原因
   - 文档化优化措施

## 参考资源

- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [PyPy Documentation](https://www.pypy.org/)
- [Cython Documentation](https://cython.readthedocs.io/)
- [Python Profiling Guide](https://docs.python.org/3/library/profile.html)

