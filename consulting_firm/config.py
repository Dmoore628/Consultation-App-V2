import os
from typing import Any

try:
    # optional dependency; if installed, loads .env into environment
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def get(key: str, default: Any = None) -> Any:
    """Get configuration from environment with optional default."""
    return os.environ.get(key, default)


MODEL_PROVIDER = get("MODEL_PROVIDER", "mock")  # mock | openai | ollama
MODEL_NAME = get("MODEL_NAME", "gpt-4o")
MODEL_TEMPERATURE = float(get("MODEL_TEMPERATURE", 0.2))
MODEL_MAX_TOKENS = int(get("MODEL_MAX_TOKENS", 1500))
OUTPUT_PATH = get("OUTPUT_PATH", "outputs")
TEMPLATES_PATH = get("TEMPLATES_PATH", "templates")
