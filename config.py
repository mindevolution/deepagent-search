"""
Configuration module for Skill System
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field, asdict
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class SkillSystemConfig:
    """Configuration for Skill System"""
    
    # Directory settings
    skills_dir: Path = field(default_factory=lambda: Path("./skills"))
    skill_module_name: str = "skill"  # Pattern for skill files: skill_*.py
    
    # State management
    state_mode: str = "replace"  # "replace", "accumulate", "fifo"
    
    # Discovery settings
    auto_discover: bool = True
    
    # Filtering settings
    filter_by_visibility: bool = True
    allowed_visibilities: List[str] = field(default_factory=lambda: ["public"])
    
    # Middleware settings
    middleware_enabled: bool = True
    
    # Logging settings
    verbose: bool = False
    log_level: str = "INFO"
    
    # Performance settings
    max_concurrent_skills: int = 5
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure skills_dir is a Path object
        if isinstance(self.skills_dir, str):
            self.skills_dir = Path(self.skills_dir)
        
        # Validate state_mode
        valid_modes = ["replace", "accumulate", "fifo"]
        if self.state_mode not in valid_modes:
            raise ValueError(
                f"state_mode must be one of {valid_modes}, got {self.state_mode}"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        # Convert Path to string for JSON serialization
        result["skills_dir"] = str(self.skills_dir)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillSystemConfig":
        """Create from dictionary"""
        # Convert string path back to Path
        if "skills_dir" in data and isinstance(data["skills_dir"], str):
            data["skills_dir"] = Path(data["skills_dir"])
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "SkillSystemConfig":
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save(self, path: Path) -> None:
        """Save configuration to file"""
        with open(path, "w") as f:
            f.write(self.to_json())
        logger.info(f"Saved configuration to {path}")
    
    @classmethod
    def load(cls, path: Path) -> "SkillSystemConfig":
        """Load configuration from file"""
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)


def load_config(config_path: Optional[Path] = None) -> SkillSystemConfig:
    """
    Load configuration from file or return default
    
    Args:
        config_path: Optional path to configuration file
    
    Returns:
        SkillSystemConfig instance
    """
    if config_path is None:
        # Try default locations
        default_paths = [
            Path("skill_config.json"),
            Path(".skill_config.json"),
            Path("config/skill_config.json")
        ]
        
        for path in default_paths:
            if path.exists():
                logger.info(f"Loading configuration from {path}")
                return SkillSystemConfig.load(path)
        
        # Return default config
        logger.info("Using default configuration")
        return SkillSystemConfig()
    
    if config_path.exists():
        logger.info(f"Loading configuration from {config_path}")
        return SkillSystemConfig.load(config_path)
    else:
        logger.warning(f"Configuration file not found: {config_path}, using defaults")
        return SkillSystemConfig()


__all__ = ["SkillSystemConfig", "load_config"]
