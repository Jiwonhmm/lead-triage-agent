"""Optional Langfuse tracing.

Tracing is on only when LANGFUSE_PUBLIC_KEY is set (locally, in .env).
In tests and CI the key is missing, so no callbacks are added and nothing is sent.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def tracing_callbacks() -> list:
    """Return a fresh Langfuse callback handler, or an empty list if tracing is off."""
    if not os.getenv("LANGFUSE_PUBLIC_KEY"):
        return []
    from langfuse.langchain import CallbackHandler

    return [CallbackHandler()]


def flush_traces() -> None:
    """Send buffered traces before a short script exits. Does nothing if tracing is off."""
    if not os.getenv("LANGFUSE_PUBLIC_KEY"):
        return
    from langfuse import get_client

    get_client().flush()
