# __init__.py

from .models import UserResponse  # Importing the UserResponse model
from .auth import AuthService  # Importing authentication service
from .utils import setup_logging, get_env_variable  # Importing utility functions

# Initialize logging when the package is imported
setup_logging()

__version__ = "0.1.0"  # Package version
__author__ = "Jothika"  # Author name
__email__ = "jothika@gmail.com"  # Author email

__all__ = ["UserResponse", "AuthService", "setup_logging", "get_env_variable"]  # Public API
