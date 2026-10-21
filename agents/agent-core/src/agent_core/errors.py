"""Shared exception types."""


class AgentError(Exception):
    """Base class for framework errors."""


class ConfigError(AgentError):
    pass


class SkillError(AgentError):
    pass


class IntakeError(AgentError):
    """Raised when an incoming request fails validation."""
