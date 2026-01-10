"""
Text Processor Skill
Tools for text manipulation and processing
"""
from langchain_core.tools import tool
from core import SkillMetadata

# Define metadata
metadata = SkillMetadata(
    name="text_processor",
    description="Process and manipulate text (uppercase, lowercase, reverse, word count, etc.)",
    tags=["text", "processing", "utility"],
    visibility="public",
    version="1.0.0",
    author="Skill System"
)

@tool
def text_uppercase(text: str) -> str:
    """Convert text to uppercase"""
    return text.upper()

@tool
def text_lowercase(text: str) -> str:
    """Convert text to lowercase"""
    return text.lower()

@tool
def text_reverse(text: str) -> str:
    """Reverse the text"""
    return text[::-1]

@tool
def text_word_count(text: str) -> str:
    """Count words in the text"""
    words = text.split()
    return f"Word count: {len(words)}"

@tool
def text_character_count(text: str) -> str:
    """Count characters in the text"""
    return f"Character count: {len(text)}"

# Export all tools as a list (registry will handle multiple tools)
tools = [text_uppercase, text_lowercase, text_reverse, text_word_count, text_character_count]

# For compatibility, export the first tool as 'tool'
tool = text_uppercase
