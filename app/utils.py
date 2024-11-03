import os
import logging
import re
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def get_env_variable(var_name: str) -> str:
    """Fetch an environment variable."""
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable '{var_name}' not set.")
    return value

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def validate_username(username: str) -> bool:
    """Validate username (must be alphanumeric and between 3-20 characters)."""
    return bool(re.match(r'^[a-zA-Z0-9]{3,20}$', username))

def validate_password(password: str) -> bool:
    """Validate password (must be at least 8 characters)."""
    return len(password) >= 8

def save_file(file_path: str, data: bytes):
    """Save binary data to a file."""
    with open(file_path, "wb") as f:
        f.write(data)

def load_file(file_path: str) -> bytes:
    """Load binary data from a file."""
    with open(file_path, "rb") as f:
        return f.read()

def handle_exception(exc: Exception, detail: str):
    """Handle exceptions uniformly."""
    raise HTTPException(status_code=500, detail=detail)
