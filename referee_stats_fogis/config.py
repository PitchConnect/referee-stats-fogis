"""Configuration settings for the referee stats application."""

import os
from pathlib import Path
from typing import Any, Optional

import yaml


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize the configuration manager.

        Args:
            config_path: Path to the configuration file. If None, uses default
                locations.
        """
        self.config: dict[str, Any] = {}
        self._load_config(config_path)

    def _load_config(self, config_path: Optional[Path] = None) -> None:
        """Load configuration from file.

        Args:
            config_path: Path to the configuration file. If None, uses default
                locations.
        """
        # Default configuration
        self.config = {
            "database": {
                "path": "data/referee_stats.db",
                "type": "sqlite",
            },
            "web": {
                "base_url": "https://fogis.se",
                "timeout": 30,
                "user_agent": "Referee Stats FOGIS",
            },
            "logging": {
                "level": "INFO",
                "file": "logs/referee_stats.log",
            },
        }

        # Try to load from config file
        paths_to_try = [
            config_path,
            Path("config.yaml"),
            Path("config.yml"),
            Path(os.path.expanduser("~/.referee_stats_fogis/config.yaml")),
        ]

        for path in paths_to_try:
            if path and path.exists():
                with open(path) as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        self._update_nested_dict(self.config, file_config)
                break

        # Check for local config override
        local_config = Path("config.local.yaml")
        if local_config.exists():
            with open(local_config) as f:
                local_file_config = yaml.safe_load(f)
                if local_file_config:
                    self._update_nested_dict(self.config, local_file_config)

    def _update_nested_dict(self, d: dict[str, Any], u: dict[str, Any]) -> None:
        """Update a nested dictionary with another nested dictionary.

        Args:
            d: Dictionary to update
            u: Dictionary with updates
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Dot-separated path to the configuration value
            default: Default value to return if the key is not found

        Returns:
            The configuration value or the default
        """
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


# Global configuration instance
config = Config()
