import subprocess
import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Security-related exception"""
    pass

def validate_identifier(identifier: str, field_name: str) -> None:
    """Validate identifier meets security requirements"""
    if not identifier or not isinstance(identifier, str):
        raise SecurityError(f"{field_name} cannot be empty")
    
    if len(identifier) > 100:
        raise SecurityError(f"{field_name} length cannot exceed 100 characters")
    
    # Only allow letters, numbers, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', identifier):
        raise SecurityError(f"{field_name} contains invalid characters")

def safe_execute_command(cmd: List[str], timeout: int = 30) -> Tuple[bool, str]:
    """Safely execute command with comprehensive error handling"""
    try:
        if not cmd or not isinstance(cmd, list):
            return False, "Invalid command format"
        
        # Check if command is in allowed list
        allowed_commands = ["okctl", "kubectl"]
        if cmd[0] not in allowed_commands:
            return False, f"Command not allowed: {cmd[0]}"
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        return True, result.stdout
        
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout: {' '.join(cmd)}")
        return False, "Command execution timeout"
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed: {e.stderr}")
        return False, f"Command failed: {e.stderr}"
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False, f"Execution error: {str(e)}" 