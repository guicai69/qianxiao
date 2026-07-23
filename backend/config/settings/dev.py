"""Development environment settings."""
from .base import *  # noqa: F401, F403

# Quicker token lifetimes for dev
from datetime import timedelta

SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(hours=4)  # longer for dev convenience
