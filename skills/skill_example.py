"""
Example skill module
This demonstrates how to create a skill for the Skill System
"""
from langchain_core.tools import tool
from core import SkillMetadata

# Define metadata for this skill
metadata = SkillMetadata(
    name="example",
    description="An example skill that demonstrates the skill system",
    tags=["example", "demo"],
    visibility="public",
    version="1.0.0"
)

# Define the tool
@tool
def example_tool(query: str) -> str:
    """
    An example tool that echoes the query
    
    Args:
        query: The input query
    
    Returns:
        A response echoing the query
    """
    return f"Example tool received: {query}"

# Export the tool (required for discovery)
tool = example_tool
