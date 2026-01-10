"""
Time Skill
Get current time and date information
"""
from langchain_core.tools import tool
from datetime import datetime
from core import SkillMetadata

# Define metadata
metadata = SkillMetadata(
    name="time",
    description="Get current time, date, and timezone information",
    tags=["time", "date", "utility"],
    visibility="public",
    version="1.0.0",
    author="Skill System"
)

@tool
def get_current_time() -> str:
    """Get the current date and time"""
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

@tool
def get_current_date() -> str:
    """Get the current date"""
    now = datetime.now()
    return f"Current date: {now.strftime('%Y-%m-%d')}"

@tool
def get_timestamp() -> str:
    """Get the current Unix timestamp"""
    timestamp = datetime.now().timestamp()
    return f"Unix timestamp: {int(timestamp)}"

# Export tools
tools = [get_current_time, get_current_date, get_timestamp]
tool = get_current_time
