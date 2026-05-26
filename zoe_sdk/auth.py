"""
Authentication helpers for ZOE Pilot SDK
AXT Labs | https://axtlabs.co
"""

import os


ZOE_API_KEY_ENV = "ZOE_API_KEY"


class AuthenticationError(Exception):
    """Raised when API key is missing or invalid."""
    pass


def resolve_api_key(api_key: str | None = None) -> str:
    """
    Resolve the ZOE API key from argument or environment variable.

    Priority order:
    1. Explicitly passed api_key argument
    2. ZOE_API_KEY environment variable

    Args:
        api_key: Optional API key string passed directly

    Returns:
        Resolved API key string

    Raises:
        AuthenticationError: If no API key can be found
    """
    key = api_key or os.getenv(ZOE_API_KEY_ENV)
    if not key:
        raise AuthenticationError(
            f"No ZOE API key found. "
            f"Pass api_key= to ZOEClient or set the {ZOE_API_KEY_ENV} environment variable.\n"
            f"Contact pilot@axtlabs.co to receive your pilot API key."
        )
    if not key.startswith("zoe_"):
        import warnings
        warnings.warn(
            "API key does not match expected format (should begin with 'zoe_'). "
            "Verify your key at pilot@axtlabs.co",
            UserWarning,
            stacklevel=3,
        )
    return key
