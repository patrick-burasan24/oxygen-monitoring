import os
from pathlib import Path
from dotenv import load_dotenv, set_key

APP_DIR = Path.home() / ".o2m"

APP_DIR.mkdir(parents=True, exist_ok=True)

ENV_PATH = APP_DIR / ".env"

load_dotenv(ENV_PATH)

def get_env(key, default=""):
    """Retrieves the key from the standard .env file. Returns null string if empty."""
    return os.getenv(key, default)

def set_env(key: str, value: str):
    """Sets key to be value. Is persistent across the entire program."""
    set_key(ENV_PATH, key_to_set=key, value_to_set=value)
    os.environ[key] = str(value)

def valid_parameter(parameter: str):
    """Check if given parameter (which by default is a str) is not null."""
    return parameter and parameter != "" and parameter.strip() != ""