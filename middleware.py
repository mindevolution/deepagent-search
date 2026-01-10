"""
Middleware for Skill System
Implements dynamic tool filtering based on context
"""
from typing import List, Dict, Any, Optional, Callable
import logging
from langchain.agents.middleware import AgentMiddleware
from langchain_core.tools import BaseTool

from core import SkillRegistry, SkillMetadata

logger = logging.getLogger(__name__)


class SkillMiddleware(AgentMiddleware):
    """
    Middleware that dynamically filters available tools based on context
    """
    
    def __init__(
        self,
        skill_registry: SkillRegistry,
        verbose: bool = False,
        filter_fn: Optional[Callable[[SkillMetadata], bool]] = None
    ):
        """
        Args:
            skill_registry: The skill registry to use
            verbose: Whether to log filtering decisions
            filter_fn: Optional function to filter skills by metadata
        """
        super().__init__()
        self.registry = skill_registry
        self.verbose = verbose
        self.filter_fn = filter_fn
    
    def __call__(
        self,
        agent_input: Dict[str, Any],
        agent_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process agent input and filter tools dynamically
        
        Args:
            agent_input: Input to the agent
            agent_config: Agent configuration
            **kwargs: Additional arguments
        
        Returns:
            Modified agent input with filtered tools
        """
        # Get current tools from agent config or input
        current_tools = agent_input.get("tools", [])
        
        # Filter tools based on registry and filter function
        if self.filter_fn:
            filtered_tools = self.registry.get_all_tools(filter_fn=self.filter_fn)
        else:
            filtered_tools = self.registry.get_all_tools()
        
        if self.verbose:
            logger.info(
                f"SkillMiddleware: Filtered {len(current_tools)} tools to {len(filtered_tools)} tools"
            )
        
        # Update agent input with filtered tools
        agent_input["tools"] = filtered_tools
        
        return agent_input
    
    def filter_tools(
        self,
        tools: List[BaseTool],
        context: Optional[Dict[str, Any]] = None
    ) -> List[BaseTool]:
        """
        Filter tools based on context
        
        Args:
            tools: List of tools to filter
            context: Optional context for filtering
        
        Returns:
            Filtered list of tools
        """
        # Use registry's filter function if available
        if self.filter_fn:
            return self.registry.get_all_tools(filter_fn=self.filter_fn)
        return self.registry.get_all_tools()


__all__ = ["SkillMiddleware"]
