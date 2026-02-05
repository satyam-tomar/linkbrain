"""
Custom exceptions for LinkBrain Core (AI/LLM layer).

These exceptions cover LLM interactions, parsing,
and AI-specific operations.
"""


class LLMError(Exception):
    """Base exception for all LLM-related errors."""
    pass


class LLMConnectionError(LLMError):
    """
    Raised when LLM API connection fails.
    
    Examples:
        - Invalid API key
        - Network connection failed
        - API endpoint unreachable
        - Rate limit exceeded
    """
    pass


class LLMGenerationError(LLMError):
    """
    Raised when LLM text generation fails.
    
    Examples:
        - API request failed
        - Model returned error
        - Generation timeout
        - Invalid response format
    """
    pass


class LLMParsingError(LLMError):
    """
    Raised when parsing LLM response fails.
    
    Examples:
        - Invalid JSON format
        - Missing required fields
        - Schema validation failed
        - Unexpected response structure
    """
    pass


class PromptBuildError(LLMError):
    """
    Raised when prompt building fails.
    
    Examples:
        - Missing required context
        - Invalid template format
        - Context too large
    """
    pass


class ActionValidationError(LLMError):
    """
    Raised when action validation fails.
    
    Examples:
        - Unknown device in action
        - Unsupported action type
        - Invalid action parameters
    """
    pass