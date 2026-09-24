"""Configuration management for Wander CLI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Config(BaseModel):
    """Wander configuration."""
    repos: list[str] = Field(default_factory=list, description="Repositories to watch (owner/repo)")
    token: Optional[str] = Field(default=None, description="GitHub token")
    notify: bool = Field(default=True, description="Enable macOS notifications")
    agent_trigger: bool = Field(default=True, description="Auto-trigger agent on CI events")
    daemon: bool = Field(default=False, description="Run as background daemon")


class Settings(BaseSettings):
    """Settings loaded from config file and environment."""
    repos: list[str] = Field(default_factory=list)
    token: Optional[str] = None
    notify: bool = True
    agent_trigger: bool = True
    daemon: bool = False
    
    class Config:
        env_prefix = "WANDER_"
        env_file = ".env"
        env_file_encoding = "utf-8"


CONFIG_PATHS = [
    Path.home() / ".config" / "wander" / "config.yaml",
    Path.home() / ".wander.yaml",
    Path.cwd() / ".wander.yaml",
]


def find_config_path(explicit_path: Optional[Path] = None) -> Optional[Path]:
    """Find config file in standard locations."""
    if explicit_path and explicit_path.exists():
        return explicit_path
    for path in CONFIG_PATHS:
        if path.exists():
            return path
    return None


def load_config(explicit_path: Optional[Path] = None) -> Config:
    """Load configuration from file, environment, and defaults."""
    config_path = find_config_path(explicit_path)
    
    # Start with defaults
    settings = Settings()
    
    # Override with config file if found
    if config_path:
        with open(config_path) as f:
            file_config = yaml.safe_load(f) or {}
        for key, value in file_config.items():
            if hasattr(settings, key) and value is not None:
                setattr(settings, key, value)
    
    # Convert to Config model
    return Config(
        repos=settings.repos,
        token=settings.token,
        notify=settings.notify,
        agent_trigger=settings.agent_trigger,
        daemon=settings.daemon,
    )


def save_config(config: Config, path: Optional[Path] = None) -> Path:
    """Save configuration to file."""
    if path is None:
        path = CONFIG_PATHS[0]
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "repos": config.repos,
        "notify": config.notify,
        "agent_trigger": config.agent_trigger,
        "daemon": config.daemon,
        # token not saved to file (use env var)
    }
    
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    
    return path