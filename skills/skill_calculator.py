"""
Calculator Skill
A simple calculator tool for basic arithmetic operations
"""
from langchain_core.tools import tool
from core import SkillMetadata

# Define metadata
metadata = SkillMetadata(
    name="calculator",
    description="Perform basic arithmetic calculations (addition, subtraction, multiplication, division)",
    tags=["math", "calculator", "arithmetic"],
    visibility="public",
    version="1.0.0",
    author="Skill System"
)

@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression safely
    
    Args:
        expression: A mathematical expression (e.g., "2 + 2", "10 * 5", "100 / 4")
    
    Returns:
        The result of the calculation or an error message
    """
    try:
        # Only allow basic arithmetic operations for safety
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Only basic arithmetic operations (+, -, *, /) are allowed"
        
        # Evaluate the expression
        result = eval(expression)
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {str(e)}"

# Export the tool
tool = calculator
