"""
Factory for AI service instances.
"""

from functools import lru_cache

from .ai_service import AIService
from .claude_service import ClaudeService


@lru_cache()
def get_ai_service() -> AIService:
    """
    Get the AI service instance.

    Returns:
        AIService instance (currently ClaudeService)
    """
    return ClaudeService()
