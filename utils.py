"""
Utility functions for Skill System
"""
from typing import List, Optional
import logging
import sys

logger = logging.getLogger(__name__)


def setup_logger(
    level: str = "INFO",
    format_string: Optional[str] = None
) -> None:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Optional custom format string
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger.info(f"Logger configured with level: {level}")


def generate_system_prompt(
    available_skill_names: List[str],
    custom_instructions: str = ""
) -> str:
    """
    Generate system prompt for the agent
    
    Args:
        available_skill_names: List of available skill names
        custom_instructions: Custom instructions to append
    
    Returns:
        System prompt string
    """
    base_prompt = """You are a helpful AI assistant with access to various skills and tools.

You can use the following skills to help users:
"""
    
    # Add skill list
    if available_skill_names:
        skill_list = "\n".join(
            f"- {skill_name}" for skill_name in available_skill_names
        )
        base_prompt += skill_list + "\n\n"
    else:
        base_prompt += "No skills are currently available.\n\n"
    
    base_prompt += """When a user asks you to do something:
1. Determine which skill(s) would be most appropriate
2. Use the skill(s) to accomplish the task
3. Provide a clear explanation of what you did

If you're unsure which skill to use, you can try multiple skills or ask the user for clarification.
"""
    
    # Add custom instructions
    if custom_instructions:
        base_prompt += f"\n\nAdditional instructions:\n{custom_instructions}\n"
    
    return base_prompt


__all__ = ["setup_logger", "generate_system_prompt"]
