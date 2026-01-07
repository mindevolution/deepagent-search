# Persistent Memory Access Guide

## Overview

The `long-term-memory.py` script uses `InMemoryStore` with `StoreBackend` to store persistent memories in the `/memories/` namespace. This guide explains how to manually access and inspect this memory.

## How to Access Persistent Memory

### Method 1: Using Helper Functions (Recommended)

The script now includes helper functions to inspect memory:

```python
# Inspect all memories
inspect_memories_sync()

# Or use async functions directly
import asyncio

async def check_memories():
    # List all keys
    keys = await list_memories("/memories/")
    print(f"Keys: {keys}")
    
    # Get a specific memory
    memory = await get_memory("preferences.txt")
    print(f"Memory content: {memory}")

# Run async function
asyncio.run(check_memories())
```

### Method 2: Direct Store Access

Since the `store` instance is now accessible, you can use it directly:

```python
import asyncio

async def direct_access():
    # List all keys in /memories/ namespace
    keys = []
    async for key in store.alist("/memories/"):
        keys.append(key)
        print(f"Found key: {key}")
    
    # Get a specific memory
    value = await store.aget("/memories/preferences.txt")
    print(f"Value: {value}")

asyncio.run(direct_access())
```

### Method 3: Interactive Python Session

You can also access the store in an interactive Python session:

```python
# In Python REPL or Jupyter notebook
import asyncio
from long_term_memory import store, inspect_all_memories, get_memory

# Inspect all memories
asyncio.run(inspect_all_memories())

# Get specific memory
memory = asyncio.run(get_memory("preferences.txt"))
print(memory)
```

## Available Functions

### `list_memories(namespace="/memories/")`
- **Purpose**: List all keys in a namespace
- **Returns**: List of keys
- **Usage**: 
  ```python
  keys = await list_memories()
  ```

### `get_memory(key, namespace="/memories/")`
- **Purpose**: Get a specific memory by key
- **Parameters**:
  - `key`: The memory key (e.g., "preferences.txt")
  - `namespace`: The namespace (default: "/memories/")
- **Returns**: The memory value or None if not found
- **Usage**:
  ```python
  memory = await get_memory("preferences.txt")
  ```

### `inspect_all_memories(namespace="/memories/")`
- **Purpose**: Print all memories in a formatted way
- **Usage**:
  ```python
  await inspect_all_memories()
  ```

### `inspect_memories_sync()`
- **Purpose**: Synchronous wrapper for `inspect_all_memories()` (for use in main block)
- **Usage**:
  ```python
  inspect_memories_sync()
  ```

## Store API Methods

The `InMemoryStore` provides these async methods:

- **`alist(namespace)`**: List all keys in a namespace
  ```python
  async for key in store.alist("/memories/"):
      print(key)
  ```

- **`aget(key)`**: Get a value by key
  ```python
  value = await store.aget("/memories/preferences.txt")
  ```

- **`aput(key, value)`**: Put a value (used by agent internally)
  ```python
  await store.aput("/memories/new_key.txt", "content")
  ```

- **`adelete(key)`**: Delete a value
  ```python
  await store.adelete("/memories/old_key.txt")
  ```

## Example: Complete Memory Inspection Script

```python
import asyncio
from long_term_memory import store, inspect_all_memories, get_memory, list_memories

async def full_inspection():
    print("="*60)
    print("FULL MEMORY INSPECTION")
    print("="*60)
    
    # List all memories
    print("\n1. Listing all memory keys:")
    keys = await list_memories()
    for key in keys:
        print(f"   - {key}")
    
    # Inspect all memories
    print("\n2. Inspecting all memories:")
    await inspect_all_memories()
    
    # Get specific memories
    print("\n3. Getting specific memories:")
    if keys:
        for key in keys[:3]:  # First 3 keys
            memory = await get_memory(key)
            print(f"\n   Key: {key}")
            print(f"   Value: {memory}")

# Run inspection
asyncio.run(full_inspection())
```

## Memory Storage Details

- **Storage Type**: In-memory (lost when script exits)
- **Namespace**: `/memories/` (configured in `make_backend()`)
- **Backend**: `StoreBackend` for persistent storage
- **State Backend**: `StateBackend` for ephemeral state (not persistent)

## Notes

1. **In-Memory Storage**: `InMemoryStore` stores data in memory, so it's lost when the script exits. For persistent storage across sessions, consider using a file-based store or database.

2. **Namespace**: All persistent memories are stored under the `/memories/` namespace. Keys should be relative to this namespace (e.g., "preferences.txt" becomes "/memories/preferences.txt").

3. **Async Operations**: Most store operations are async, so use `asyncio.run()` or `await` when calling them.

4. **Thread Safety**: The store is shared across all agent invocations, so memories persist within the same script execution.

## Troubleshooting

### No memories found
- Make sure the agent has actually written to memory
- Check that you're using the correct namespace (`/memories/`)
- Verify the agent successfully completed the write operation

### Key not found
- Check the exact key name (case-sensitive)
- Ensure the key includes the namespace prefix if needed
- List all keys first to see what's available

### Async errors
- Make sure you're using `asyncio.run()` or `await` for async operations
- Check that you're in an async context when using async functions

