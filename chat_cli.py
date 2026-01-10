"""
Command-line Chat Interface for DeepAgent
Run with: python chat_cli.py
"""
import uuid
import sys
from pathlib import Path
import asyncio

# Add current directory to path and import with hyphenated module name
sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location("long_term_memory", Path(__file__).parent / "long-term-memory.py")
long_term_memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(long_term_memory)
agent = long_term_memory.agent
store = long_term_memory.store

def print_header():
    """Print welcome header"""
    print("\n" + "="*60)
    print("🤖 DeepAgent Chat Interface")
    print("="*60)
    print("Type 'help' for commands, 'quit' or 'exit' to exit")
    print("="*60 + "\n")

def print_help():
    """Print help message"""
    print("\nCommands:")
    print("  help              - Show this help message")
    print("  new               - Start a new conversation thread")
    print("  memories          - List all memories")
    print("  memory <key>      - View a specific memory")
    print("  clear             - Clear chat history")
    print("  quit / exit       - Exit the chat")
    print()

def list_memories():
    """List all memories"""
    try:
        async def _list():
            # Use asearch to find all keys in the /memories namespace
            # namespace_prefix must be a tuple: ("memories",) for /memories/
            try:
                results = await store.asearch(("memories",), query=None, limit=100)
                keys = []
                if results:
                    for result in results:
                        # SearchItem has a 'key' attribute
                        if hasattr(result, 'key'):
                            keys.append(result.key)
                        elif hasattr(result, 'id'):
                            keys.append(result.id)
                        elif isinstance(result, dict):
                            keys.append(result.get('key', result.get('id', str(result))))
                        else:
                            keys.append(str(result))
                return keys
            except Exception as e:
                print(f"Search error: {e}")
                return []
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        keys = loop.run_until_complete(_list())
        loop.close()
        
        if keys:
            print(f"\n📚 Found {len(keys)} memory item(s):\n")
            for i, key in enumerate(keys, 1):
                print(f"  {i}. {key}")
        else:
            print("\n📚 No memories found")
        print()
    except Exception as e:
        print(f"\n❌ Error listing memories: {e}\n")

def view_memory(key):
    """View a specific memory"""
    try:
        async def _get():
            # Try different key formats
            key_variants = [
                key if key.startswith("/") else f"/memories/{key}",
                key
            ]
            for full_key in key_variants:
                try:
                    value = await store.aget(full_key)
                    if value is not None:
                        return value
                except Exception:
                    continue
            return None
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        value = loop.run_until_complete(_get())
        loop.close()
        
        if value is not None:
            print(f"\n📄 Memory: {key}\n")
            print("-" * 60)
            if isinstance(value, (str, bytes)):
                print(str(value))
            else:
                print(value)
            print("-" * 60)
        else:
            print(f"\n❌ Memory '{key}' not found\n")
    except Exception as e:
        print(f"\n❌ Error reading memory: {e}\n")

def chat_loop():
    """Main chat loop"""
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    messages = []
    
    print_header()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Goodbye!\n")
                break
            
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            elif user_input.lower() == 'new':
                thread_id = str(uuid.uuid4())
                config = {"configurable": {"thread_id": thread_id}}
                messages = []
                print(f"\n🆕 New thread started: {thread_id[:8]}...\n")
                continue
            
            elif user_input.lower() == 'clear':
                messages = []
                print("\n🗑️  Chat history cleared\n")
                continue
            
            elif user_input.lower() == 'memories':
                list_memories()
                continue
            
            elif user_input.lower().startswith('memory '):
                key = user_input[7:].strip()
                if key:
                    view_memory(key)
                else:
                    print("\n❌ Usage: memory <key>\n")
                continue
            
            # Process user message
            print("\n🤖 Agent: ", end="", flush=True)
            
            # Invoke agent
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config
            )
            
            # Get and display response
            response = result["messages"][-1].content
            print(response)
            print()
            
            # Store in conversation history
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    try:
        chat_loop()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)

