"""
Example: Skill Agent with DashScope Qianwen (通义千问) Model

This example demonstrates how to create a skill agent using Qianwen chat model
from DashScope (阿里云通义千问).

Requirements:
- DASHSCOPE_API_KEY in .env file or environment variable
- Skills directory with skill modules

Usage:
    python example_qianwen_skill_agent.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi

from AgentSkill import create_skill_agent, SkillAgent
from config import SkillSystemConfig

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
    """
    Create a Qianwen chat model instance
    
    Available Qianwen models on DashScope:
    - "qwen-turbo" - Fast and cost-effective (recommended for most use cases)
    - "qwen-plus" - More capable, better for complex tasks
    - "qwen-max" - Most capable, best quality
    - "qwen-max-longcontext" - For long context tasks
    
    Args:
        model_name: Model name (default: "qwen-turbo")
        temperature: Sampling temperature (0.0-1.0)
        top_p: Nucleus sampling parameter (0.0-1.0)
        streaming: Whether to enable streaming
    
    Returns:
        ChatTongyi model instance
    """
    api_key = get_env("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError(
            "DASHSCOPE_API_KEY not found. Please set it in .env file or environment variable."
        )
    
    return ChatTongyi(
        model=model_name,
        api_key=api_key,
        temperature=temperature,
        top_p=top_p,
        streaming=streaming,
    )


def main():
    """Main example function"""
    print("=" * 60)
    print("Qianwen Skill Agent Example")
    print("=" * 60)
    print()
    
    # 1. Create Qianwen model
    print("Step 1: Creating Qianwen model...")
    try:
        qianwen_model = create_qianwen_model(
            model_name=get_env("DASHSCOPE_MODEL", "qwen-turbo"),
            temperature=0.7,
            top_p=0.8,
            streaming=False
        )
        # Get model name from the model_name attribute or use the parameter
        model_name_display = getattr(qianwen_model, 'model_name', None) or get_env("DASHSCOPE_MODEL", "qwen-turbo")
        print(f"✓ Qianwen model created: {model_name_display}")
    except Exception as e:
        print(f"✗ Error creating model: {e}")
        print("\nPlease ensure:")
        print("1. DASHSCOPE_API_KEY is set in .env file")
        print("2. You have valid DashScope API credentials")
        return
    print()
    
    # 2. Configure skill system
    print("Step 2: Configuring skill system...")
    config = SkillSystemConfig(
        skills_dir=Path("./skills"),
        state_mode="fifo",  # Use FIFO state management
        auto_discover=True,  # Automatically discover skills
        verbose=True,  # Enable verbose logging
        middleware_enabled=True,  # Enable dynamic tool filtering
        filter_by_visibility=True,
        allowed_visibilities=["public"],  # Only load public skills
    )
    print(f"✓ Configuration loaded:")
    print(f"  - Skills directory: {config.skills_dir}")
    print(f"  - State mode: {config.state_mode}")
    print(f"  - Auto-discover: {config.auto_discover}")
    print()
    
    # 3. Create skill agent
    print("Step 3: Creating skill agent...")
    try:
        agent = create_skill_agent(
            model=qianwen_model,
            config=config,
            custom_system_prompt="""You are a helpful AI assistant powered by Qianwen (通义千问).
You have access to various skills that can help users accomplish tasks.
Use the available skills to provide the best assistance possible.
Always explain what you're doing and why."""
        )
        print(f"✓ Skill agent created successfully")
        print(f"  - Total skills loaded: {len(agent.registry)}")
        print(f"  - Available skills: {', '.join(agent.list_skills())}")
    except Exception as e:
        print(f"✗ Error creating agent: {e}")
        import traceback
        traceback.print_exc()
        return
    print()
    
    # 4. Example interactions
    print("Step 4: Example interactions")
    print("-" * 60)
    
    examples = [
        "Hello! What skills do you have available?",
        "Can you use the example skill to process 'test message'?",
    ]
    
    for i, user_input in enumerate(examples, 1):
        print(f"\nExample {i}:")
        print(f"User: {user_input}")
        print("Agent: ", end="", flush=True)
        
        try:
            result = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })
            
            # Extract response
            if isinstance(result, dict) and "messages" in result:
                response = result["messages"][-1].content
            else:
                response = str(result)
            
            print(response)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nYou can now use the agent interactively:")
    print("  agent.invoke({'messages': [{'role': 'user', 'content': 'Your question'}]})")


if __name__ == "__main__":
    main()
