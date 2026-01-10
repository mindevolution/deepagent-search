"""
Streamlit Chat UI for DeepAgent
Run with: streamlit run chat_ui.py
"""
import streamlit as st
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

# Page configuration
st.set_page_config(
    page_title="DeepAgent Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Sidebar
with st.sidebar:
    st.title("🤖 DeepAgent Chat")
    st.markdown("---")
    
    # Thread management
    st.subheader("Thread Management")
    if st.button("🆕 New Thread", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.config = {"configurable": {"thread_id": st.session_state.thread_id}}
        st.session_state.messages = []
        st.rerun()
    
    st.info(f"**Thread ID:**\n`{st.session_state.thread_id[:8]}...`")
    
    st.markdown("---")
    
    # Memory inspection
    st.subheader("Memory Management")
    
    if st.button("🔍 Inspect Memories", use_container_width=True):
        with st.spinner("Loading memories..."):
            try:
                async def list_memories():
                    # Use asearch to find all keys in the /memories namespace
                    # namespace_prefix must be a tuple: ("memories",) for /memories/
                    try:
                        results = await store.asearch(("memories",), query=None, limit=100)
                        # Extract keys from search results
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
                        # Return empty list if search fails
                        return []
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                keys = loop.run_until_complete(list_memories())
                loop.close()
                
                if keys:
                    st.success(f"Found {len(keys)} memory item(s)")
                    for key in keys:
                        with st.expander(f"📄 {key}"):
                            try:
                                async def get_memory(key):
                                    return await store.aget(key)
                                
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                value = loop.run_until_complete(get_memory(key))
                                loop.close()
                                
                                if isinstance(value, (str, bytes)):
                                    st.text(str(value)[:1000])
                                else:
                                    st.json(value)
                            except Exception as e:
                                st.error(f"Error reading: {e}")
                else:
                    st.info("No memories found")
            except Exception as e:
                st.error(f"Error: {e}")
                st.exception(e)
    
    st.markdown("---")
    
    # Settings
    st.subheader("Settings")
    st.caption("Chat interface for DeepAgent with persistent memory")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.title("💬 DeepAgent Chat")
st.caption("Ask questions and chat with your AI agent. The agent has access to web search and persistent memory.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Invoke agent
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": prompt}]},
                    config=st.session_state.config
                )
                
                # Get response
                response = result["messages"][-1].content
                
                # Display response
                st.markdown(response)
                
                # Add assistant response to chat
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.caption("💡 Tip: The agent remembers information across conversations using persistent memory at `/memories/`")

