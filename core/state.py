"""
State management classes for Skill System
"""
from typing import List, Dict, Any, Optional
from . import SkillState


class SkillStateAccumulative(SkillState):
    """
    Accumulative state - accumulates messages and state over time
    """
    messages: List[Dict[str, Any]] = []
    intermediate_steps: List[Any] = []
    skill_history: List[Dict[str, Any]] = []
    
    def __init__(self, **kwargs):
        """Initialize with optional state"""
        self.messages = kwargs.get("messages", [])
        self.intermediate_steps = kwargs.get("intermediate_steps", [])
        self.skill_history = kwargs.get("skill_history", [])
        super().__init__()
    
    def accumulate(self, new_messages: List[Dict[str, Any]], new_steps: Optional[List[Any]] = None):
        """Accumulate new messages and steps"""
        self.messages.extend(new_messages)
        if new_steps:
            self.intermediate_steps.extend(new_steps)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "messages": self.messages,
            "intermediate_steps": self.intermediate_steps,
            "skill_history": self.skill_history
        }


class SkillStateFIFO(SkillState):
    """
    FIFO state - maintains a fixed-size queue of messages
    """
    messages: List[Dict[str, Any]] = []
    max_size: int = 100
    
    def __init__(self, max_size: int = 100, **kwargs):
        """Initialize with max queue size"""
        self.max_size = max_size
        self.messages = kwargs.get("messages", [])
        super().__init__()
    
    def append(self, new_messages: List[Dict[str, Any]]):
        """Append new messages, maintaining FIFO order"""
        self.messages.extend(new_messages)
        # Keep only the last max_size messages
        if len(self.messages) > self.max_size:
            self.messages = self.messages[-self.max_size:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "messages": self.messages,
            "max_size": self.max_size
        }


__all__ = ["SkillStateAccumulative", "SkillStateFIFO"]
