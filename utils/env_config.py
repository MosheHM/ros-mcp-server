"""
Environment configuration loader for ROS MCP Server.

This module handles loading environment-specific configuration from .env files
and environment variables, supporting both development and production modes.
"""

import os
from pathlib import Path
from typing import Optional


class EnvironmentConfig:
    """Manages environment-specific configuration for the ROS MCP Server."""

    def __init__(self):
        """Initialize environment configuration."""
        self.environment = os.getenv("ENVIRONMENT", "development")
        self._load_env_file()

    def _load_env_file(self):
        """Load environment variables from .env file based on ENVIRONMENT setting."""
        # Try to import python-dotenv if available
        try:
            from dotenv import load_dotenv
        except ImportError:
            # python-dotenv not available, skip loading .env files
            return

        # Determine which .env file to load
        project_root = Path(__file__).parent.parent
        env_file = project_root / f".env.{self.environment}"

        # Fall back to .env if environment-specific file doesn't exist
        if not env_file.exists():
            env_file = project_root / ".env"

        # Load the environment file if it exists
        if env_file.exists():
            load_dotenv(env_file)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get an environment variable value.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get an environment variable as an integer.

        Args:
            key: Environment variable name
            default: Default value if not found or not an integer

        Returns:
            Environment variable value as integer or default
        """
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get an environment variable as a boolean.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value as boolean or default
        """
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    @property
    def mcp_transport(self) -> str:
        """Get MCP transport setting."""
        default = "stdio" if self.is_development else "http"
        return self.get("MCP_TRANSPORT", default).lower()

    @property
    def mcp_host(self) -> str:
        """Get MCP host setting."""
        default = "127.0.0.1" if self.is_development else "0.0.0.0"
        return self.get("MCP_HOST", default)

    @property
    def mcp_port(self) -> int:
        """Get MCP port setting."""
        return self.get_int("MCP_PORT", 9000)

    @property
    def rosbridge_ip(self) -> str:
        """Get ROS Bridge IP setting."""
        return self.get("ROSBRIDGE_IP", "127.0.0.1")

    @property
    def rosbridge_port(self) -> int:
        """Get ROS Bridge port setting."""
        return self.get_int("ROSBRIDGE_PORT", 9090)

    @property
    def log_level(self) -> str:
        """Get log level setting."""
        default = "DEBUG" if self.is_development else "INFO"
        return self.get("LOG_LEVEL", default).upper()

    @property
    def debug(self) -> bool:
        """Get debug mode setting."""
        return self.get_bool("DEBUG", self.is_development)


# Global environment configuration instance
env_config = EnvironmentConfig()
