"""
Streamlit UI for Skill Agent with Qianwen Model
Run with: streamlit run skill_agent_ui.py
"""
import streamlit as st
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from AgentSkill import create_skill_agent, SkillAgent
from config import SkillSystemConfig
from core import SkillMetadata

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    load_dotenv(dotenv_path=".env", override=True)


def get_env(key: str, default: str = None) -> str:
    """Get environment variable"""
    value = os.environ.get(key)
    if value is None:
        return default
    return value


def create_qianwen_model(
    model_name: str = "qwen-turbo",
    temperature: float = 0.7,
    top_p: float = 0.8,
    streaming: bool = False
) -> ChatTongyi:
    """Create a Qianwen chat model instance"""
    api_key = get_env("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY not found")
    
    return ChatTongyi(
        model=model_name,
        api_key=api_key,
        temperature=temperature,
        top_p=top_p,
        streaming=streaming,
    )


# Page configuration
st.set_page_config(
    page_title="Skill Agent - Qianwen",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "skills_info" not in st.session_state:
    st.session_state.skills_info = []


# Sidebar
with st.sidebar:
    st.title("🤖 Skill Agent")
    st.markdown("---")
    
    # Model Configuration
    st.subheader("Model Configuration")
    
    model_name = st.selectbox(
        "Qianwen Model",
        ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext"],
        index=0,
        help="Select the Qianwen model to use"
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Controls randomness in responses"
    )
    
    top_p = st.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=0.8,
        step=0.1,
        help="Nucleus sampling parameter"
    )
    
    # Skill System Configuration
    st.markdown("---")
    st.subheader("Skill System Config")
    
    skills_dir = st.text_input(
        "Skills Directory",
        value="./skills",
        help="Directory containing skill modules"
    )
    
    state_mode = st.selectbox(
        "State Mode",
        ["replace", "accumulate", "fifo"],
        index=2,
        help="State management mode"
    )
    
    auto_discover = st.checkbox(
        "Auto Discover Skills",
        value=True,
        help="Automatically discover skills from directory"
    )
    
    middleware_enabled = st.checkbox(
        "Enable Middleware",
        value=True,
        help="Enable dynamic tool filtering"
    )
    
    verbose = st.checkbox(
        "Verbose Logging",
        value=False,
        help="Show detailed logs"
    )
    
    # Initialize Agent Button
    st.markdown("---")
    if st.button("🚀 Initialize Agent", use_container_width=True):
        with st.spinner("Initializing agent..."):
            try:
                # Create model
                qianwen_model = create_qianwen_model(
                    model_name=model_name,
                    temperature=temperature,
                    top_p=top_p,
                    streaming=False
                )
                
                # Create config
                config = SkillSystemConfig(
                    skills_dir=Path(skills_dir),
                    state_mode=state_mode,
                    auto_discover=auto_discover,
                    verbose=verbose,
                    middleware_enabled=middleware_enabled,
                    filter_by_visibility=True,
                    allowed_visibilities=["public"],
                )
                
                # Create agent
                agent = create_skill_agent(
                    model=qianwen_model,
                    config=config,
                    custom_system_prompt="""You are a helpful AI assistant powered by Qianwen (通义千问).
You have access to various skills that can help users accomplish tasks.
Use the available skills to provide the best assistance possible.
Always explain what you're doing and why."""
                )
                
                st.session_state.agent = agent
                st.session_state.messages = []
                
                # Load skills info
                skills_list = agent.list_skills()
                skills_info = []
                for skill_name in skills_list:
                    try:
                        meta = agent.get_skill_info(skill_name)
                        skills_info.append({
                            "name": skill_name,
                            "description": meta.description,
                            "tags": meta.tags,
                            "visibility": meta.visibility
                        })
                    except:
                        skills_info.append({
                            "name": skill_name,
                            "description": "No description available",
                            "tags": [],
                            "visibility": "unknown"
                        })
                
                st.session_state.skills_info = skills_info
                
                st.success(f"✅ Agent initialized with {len(skills_list)} skills!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error initializing agent: {e}")
                st.exception(e)
    
    # Skills Information
    if st.session_state.agent is not None:
        st.markdown("---")
        st.subheader("Available Skills")
        st.info(f"**{len(st.session_state.skills_info)}** skills loaded")
        
        # Skills list
        for skill in st.session_state.skills_info:
            with st.expander(f"🔧 {skill['name']}"):
                st.write(f"**Description:** {skill['description']}")
                if skill['tags']:
                    st.write(f"**Tags:** {', '.join(skill['tags'])}")
                st.write(f"**Visibility:** {skill['visibility']}")
    
    # Clear Chat Button
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# Main chat interface
st.title("💬 Skill Agent Chat")
st.caption("Chat with your Skill Agent powered by Qianwen (通义千问). The agent can use various skills to help you.")

# Check if agent is initialized
if st.session_state.agent is None:
    st.warning("⚠️ Please initialize the agent from the sidebar first!")
    st.info("""
    **Steps to get started:**
    1. Configure the model settings in the sidebar
    2. Set up the skill system configuration
    3. Click "🚀 Initialize Agent" button
    4. Start chatting!
    """)
    
    # Show example skills if available
    skills_dir = Path("./skills")
    if skills_dir.exists():
        st.subheader("📁 Available Skill Files")
        skill_files = list(skills_dir.glob("skill_*.py"))
        if skill_files:
            for skill_file in skill_files:
                st.code(f"skills/{skill_file.name}", language="text")
        else:
            st.info("No skill files found. Create skills in the `skills/` directory with pattern `skill_*.py`")
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question or request a skill..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Invoke agent
                    result = st.session_state.agent.invoke({
                        "messages": [{"role": "user", "content": prompt}]
                    })
                    
                    # Extract response
                    if isinstance(result, dict) and "messages" in result:
                        response = result["messages"][-1].content
                    else:
                        response = str(result)
                    
                    # Display response
                    st.markdown(response)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.exception(e)
    
    # Quick action buttons
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 List Skills"):
            skills_list = st.session_state.agent.list_skills()
            st.info(f"Available skills: {', '.join(skills_list)}")
    
    with col2:
        if st.button("🧮 Calculator"):
            st.session_state.messages.append({"role": "user", "content": "Use the calculator to calculate 25 * 4"})
            st.rerun()
    
    with col3:
        if st.button("⏰ Current Time"):
            st.session_state.messages.append({"role": "user", "content": "What time is it?"})
            st.rerun()
    
    with col4:
        if st.button("ℹ️ Agent Info"):
            info = f"""
            **Agent Information:**
            - Model: {model_name}
            - Skills Loaded: {len(st.session_state.skills_info)}
            - State Mode: {state_mode}
            - Middleware: {'Enabled' if middleware_enabled else 'Disabled'}
            """
            st.info(info)

# Footer
st.markdown("---")
st.caption("💡 Tip: The agent can use skills like calculator, text processing, and time utilities. Ask it to use specific skills!")
