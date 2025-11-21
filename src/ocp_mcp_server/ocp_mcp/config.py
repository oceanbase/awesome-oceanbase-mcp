"""Configuration management for OCP MCP Server."""

import logging
import os

from dotenv import load_dotenv
from pydantic import BaseModel

logger = logging.getLogger(__name__)

load_dotenv()


class Config(BaseModel):
    """Configuration model."""
    ocp_url: str
    ocp_access_key_id: str
    ocp_access_key_secret: str


def get_config() -> Config:
    """
    Get configuration from environment variables.
    
    Returns:
        Configuration object
    
    Raises:
        ValueError: If required environment variables are missing
    """
    ocp_url = os.getenv("OCP_URL")
    ocp_access_key_id = os.getenv("OCP_ACCESS_KEY_ID")
    ocp_access_key_secret = os.getenv("OCP_ACCESS_KEY_SECRET")

    
    if not ocp_url:
        raise ValueError("OCP_URL environment variable is required")
    if not ocp_access_key_id:
        raise ValueError("OCP_ACCESS_KEY_ID environment variable is required")
    if not ocp_access_key_secret:
        raise ValueError("OCP_ACCESS_KEY_SECRET environment variable is required")
    
    return Config(
        ocp_url=ocp_url,
        ocp_access_key_id=ocp_access_key_id,
        ocp_access_key_secret=ocp_access_key_secret,
    )