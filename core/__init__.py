"""
Core module for Skill System
Contains SkillRegistry, SkillState, and SkillMetadata
"""
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import importlib.util
import logging
from dataclasses import dataclass, field
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


@dataclass
class SkillMetadata:
    """Metadata for a skill"""
    name: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    visibility: str = "public"  # "public", "private", "internal"
    version: str = "1.0.0"
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "visibility": self.visibility,
            "version": self.version,
            "author": self.author,
            "dependencies": self.dependencies
        }


class SkillState:
    """Base state class for agent state management"""
    pass


class SkillRegistry:
    """
    Registry for managing skills (tools)
    Discovers and loads skills from a directory
    """
    
    def __init__(self):
        self._skills: Dict[str, SkillMetadata] = {}
        self._tools: Dict[str, BaseTool] = {}
        self._modules: Dict[str, Any] = {}
    
    def register(
        self,
        name: str,
        tool: BaseTool,
        metadata: Optional[SkillMetadata] = None
    ) -> None:
        """Register a skill"""
        if metadata is None:
            metadata = SkillMetadata(
                name=name,
                description=tool.description or ""
            )
        self._skills[name] = metadata
        self._tools[name] = tool
        logger.debug(f"Registered skill: {name}")
    
    def discover_and_load(
        self,
        skills_dir: Path,
        module_name: str = "skill"
    ) -> int:
        """
        Discover and load skills from a directory
        
        Args:
            skills_dir: Directory containing skill modules
            module_name: Name pattern for skill modules (e.g., "skill" for skill_*.py)
        
        Returns:
            Number of skills loaded
        """
        if not skills_dir.exists():
            logger.warning(f"Skills directory does not exist: {skills_dir}")
            return 0
        
        loaded_count = 0
        
        # Look for Python files matching the pattern
        pattern = f"{module_name}_*.py"
        for skill_file in skills_dir.glob(pattern):
            try:
                # Load the module
                spec = importlib.util.spec_from_file_location(
                    skill_file.stem,
                    skill_file
                )
                if spec is None or spec.loader is None:
                    continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for tools in the module
                # Common patterns: tool, skill, get_tool, create_tool
                tool = None
                metadata = None
                
                # Try to find tools (support both single tool and multiple tools)
                tools_to_register = []
                
                # Check for multiple tools first
                if hasattr(module, "tools") and isinstance(module.tools, list):
                    tools_to_register = module.tools
                # Then check for single tool
                elif hasattr(module, "tool"):
                    tools_to_register = [module.tool]
                elif hasattr(module, "skill"):
                    tools_to_register = [module.skill]
                elif hasattr(module, "get_tool"):
                    tools_to_register = [module.get_tool()]
                elif hasattr(module, "create_tool"):
                    tools_to_register = [module.create_tool()]
                
                # Try to find metadata
                if hasattr(module, "metadata"):
                    metadata = module.metadata
                elif hasattr(module, "METADATA"):
                    metadata = module.METADATA
                else:
                    metadata = None
                
                if tools_to_register:
                    base_skill_name = skill_file.stem.replace(f"{module_name}_", "")
                    
                    # Register each tool
                    for idx, tool in enumerate(tools_to_register):
                        if len(tools_to_register) == 1:
                            # Single tool: use base name
                            skill_name = base_skill_name
                        else:
                            # Multiple tools: append tool name or index
                            tool_name = getattr(tool, "name", f"tool_{idx}")
                            skill_name = f"{base_skill_name}_{tool_name}"
                        
                        # Create metadata for this tool
                        if metadata is None:
                            tool_metadata = SkillMetadata(
                                name=skill_name,
                                description=getattr(tool, "description", "") or ""
                            )
                        else:
                            # Clone metadata and update name
                            tool_metadata = SkillMetadata(
                                name=skill_name,
                                description=metadata.description or getattr(tool, "description", "") or "",
                                tags=metadata.tags.copy() if metadata.tags else [],
                                visibility=metadata.visibility,
                                version=metadata.version,
                                author=metadata.author,
                                dependencies=metadata.dependencies.copy() if metadata.dependencies else []
                            )
                        
                        self.register(skill_name, tool, tool_metadata)
                        loaded_count += 1
                        logger.info(f"Loaded skill: {skill_name} from {skill_file.name}")
                    
                    self._modules[base_skill_name] = module
                else:
                    logger.warning(f"No tool found in {skill_file.name}")
                    
            except Exception as e:
                logger.error(f"Error loading skill from {skill_file}: {e}", exc_info=True)
        
        return loaded_count
    
    def list_skills(
        self,
        filter_fn: Optional[Callable[[SkillMetadata], bool]] = None
    ) -> List[str]:
        """List all registered skill names"""
        if filter_fn is None:
            return list(self._skills.keys())
        return [
            name for name, meta in self._skills.items()
            if filter_fn(meta)
        ]
    
    def get_metadata(self, skill_name: str) -> Optional[SkillMetadata]:
        """Get metadata for a skill"""
        return self._skills.get(skill_name)
    
    def search(
        self,
        query: str = "",
        tags: Optional[List[str]] = None
    ) -> List[SkillMetadata]:
        """
        Search for skills by query and tags
        
        Args:
            query: Search query (searches in name and description)
            tags: List of tags to filter by
        
        Returns:
            List of matching SkillMetadata
        """
        results = []
        query_lower = query.lower()
        
        for metadata in self._skills.values():
            # Filter by query
            if query:
                matches_query = (
                    query_lower in metadata.name.lower() or
                    query_lower in metadata.description.lower()
                )
                if not matches_query:
                    continue
            
            # Filter by tags
            if tags:
                matches_tags = any(tag in metadata.tags for tag in tags)
                if not matches_tags:
                    continue
            
            results.append(metadata)
        
        return results
    
    def get_all_tools(
        self,
        filter_fn: Optional[Callable[[SkillMetadata], bool]] = None
    ) -> List[BaseTool]:
        """Get all tools, optionally filtered"""
        if filter_fn is None:
            return list(self._tools.values())
        
        return [
            tool for name, tool in self._tools.items()
            if name in self._skills and filter_fn(self._skills[name])
        ]
    
    def get_tool(self, skill_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self._tools.get(skill_name)
    
    def __len__(self) -> int:
        """Return number of registered skills"""
        return len(self._skills)
    
    def __contains__(self, skill_name: str) -> bool:
        """Check if a skill is registered"""
        return skill_name in self._skills
    
    def __repr__(self) -> str:
        return f"SkillRegistry({len(self._skills)} skills)"


# Export main classes
__all__ = ["SkillRegistry", "SkillState", "SkillMetadata"]
