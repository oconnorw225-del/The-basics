"""
Safe File Operations Module
Provides secure file I/O with path validation and protection against attacks
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass


class SafeFileOperations:
    """
    Secure file operations with path validation and protection.
    Prevents path traversal and arbitrary file access.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize safe file operations.
        
        Args:
            project_root: Root directory for all operations (defaults to cwd)
        """
        self.project_root = Path(project_root or os.getcwd()).resolve()
        logger.info(f"SafeFileOps initialized with root: {self.project_root}")
    
    def _validate_path(self, filepath: Union[str, Path]) -> Path:
        """
        Validate that path is safe and within project root.
        
        Args:
            filepath: Path to validate
            
        Returns:
            Validated absolute path
            
        Raises:
            SecurityError: If path is invalid or outside project root
        """
        # Convert to Path object and resolve
        path = Path(filepath).resolve()
        
        # Check if path is within project root
        try:
            path.relative_to(self.project_root)
        except ValueError:
            raise SecurityError(
                f"Path traversal attempt blocked: {filepath} "
                f"is outside project root {self.project_root}"
            )
        
        # Check for dangerous patterns
        dangerous_patterns = ['..', '~', '$']
        if any(pattern in str(filepath) for pattern in dangerous_patterns):
            raise SecurityError(f"Dangerous path pattern detected: {filepath}")
        
        return path
    
    def safe_read(self, filepath: str, binary: bool = False) -> Union[str, bytes]:
        """
        Safely read file contents.
        
        Args:
            filepath: Path to file
            binary: Read in binary mode
            
        Returns:
            File contents
            
        Raises:
            SecurityError: If path is invalid
            FileNotFoundError: If file doesn't exist
        """
        path = self._validate_path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if not path.is_file():
            raise SecurityError(f"Not a file: {filepath}")
        
        mode = 'rb' if binary else 'r'
        encoding = None if binary else 'utf-8'
        
        logger.debug(f"Reading file: {path}")
        
        with open(path, mode, encoding=encoding) as f:
            return f.read()
    
    def safe_write(
        self, 
        filepath: str, 
        content: Union[str, bytes, Dict], 
        create_dirs: bool = True
    ) -> None:
        """
        Safely write content to file.
        
        Args:
            filepath: Path to file
            content: Content to write (str, bytes, or dict for JSON)
            create_dirs: Create parent directories if needed
            
        Raises:
            SecurityError: If path is invalid
        """
        path = self._validate_path(filepath)
        
        # Create parent directories if needed
        if create_dirs and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {path.parent}")
        
        # Determine write mode and content
        if isinstance(content, dict):
            mode = 'w'
            write_content = json.dumps(content, indent=2)
        elif isinstance(content, bytes):
            mode = 'wb'
            write_content = content
        else:
            mode = 'w'
            write_content = str(content)
        
        logger.debug(f"Writing file: {path}")
        
        # Write with atomic operation (write to temp, then rename)
        temp_path = path.with_suffix(path.suffix + '.tmp')
        
        try:
            encoding = None if mode == 'wb' else 'utf-8'
            with open(temp_path, mode, encoding=encoding) as f:
                f.write(write_content)
            
            # Atomic rename
            temp_path.replace(path)
            logger.info(f"Successfully wrote: {path}")
            
        except Exception as e:
            # Cleanup temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    def safe_read_json(self, filepath: str) -> Dict:
        """
        Safely read and parse JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            SecurityError: If path is invalid
            json.JSONDecodeError: If JSON is invalid
        """
        content = self.safe_read(filepath)
        return json.loads(content)
    
    def safe_write_json(self, filepath: str, data: Dict, create_dirs: bool = True) -> None:
        """
        Safely write data as JSON file.
        
        Args:
            filepath: Path to JSON file
            data: Data to write
            create_dirs: Create parent directories if needed
        """
        self.safe_write(filepath, data, create_dirs=create_dirs)
    
    def safe_delete(self, filepath: str, require_exists: bool = True) -> bool:
        """
        Safely delete a file.
        
        Args:
            filepath: Path to file
            require_exists: Raise error if file doesn't exist
            
        Returns:
            True if deleted, False if didn't exist
            
        Raises:
            SecurityError: If path is invalid
        """
        path = self._validate_path(filepath)
        
        if not path.exists():
            if require_exists:
                raise FileNotFoundError(f"File not found: {filepath}")
            return False
        
        if not path.is_file():
            raise SecurityError(f"Not a file: {filepath}")
        
        logger.debug(f"Deleting file: {path}")
        path.unlink()
        logger.info(f"Successfully deleted: {path}")
        return True
    
    def safe_list_dir(self, dirpath: str) -> list:
        """
        Safely list directory contents.
        
        Args:
            dirpath: Path to directory
            
        Returns:
            List of filenames
            
        Raises:
            SecurityError: If path is invalid
        """
        path = self._validate_path(dirpath)
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {dirpath}")
        
        if not path.is_dir():
            raise SecurityError(f"Not a directory: {dirpath}")
        
        return [f.name for f in path.iterdir()]
    
    def safe_mkdir(self, dirpath: str, parents: bool = True) -> None:
        """
        Safely create directory.
        
        Args:
            dirpath: Path to directory
            parents: Create parent directories
            
        Raises:
            SecurityError: If path is invalid
        """
        path = self._validate_path(dirpath)
        
        logger.debug(f"Creating directory: {path}")
        path.mkdir(parents=parents, exist_ok=True)
        logger.info(f"Successfully created: {path}")


class SecureConfigManager:
    """
    Manages configuration files securely.
    """
    
    def __init__(self, config_dir: str = '.config'):
        """
        Initialize config manager.
        
        Args:
            config_dir: Directory for config files
        """
        self.file_ops = SafeFileOperations()
        self.config_dir = Path(config_dir)
        
        # Ensure config directory exists
        self.file_ops.safe_mkdir(str(self.config_dir))
    
    def load_config(self, name: str) -> Dict:
        """
        Load configuration file.
        
        Args:
            name: Config file name (without extension)
            
        Returns:
            Configuration dictionary
        """
        filepath = self.config_dir / f"{name}.json"
        
        try:
            return self.file_ops.safe_read_json(str(filepath))
        except FileNotFoundError:
            logger.warning(f"Config not found: {name}")
            return {}
    
    def save_config(self, name: str, config: Dict) -> None:
        """
        Save configuration file.
        
        Args:
            name: Config file name (without extension)
            config: Configuration dictionary
        """
        filepath = self.config_dir / f"{name}.json"
        self.file_ops.safe_write_json(str(filepath), config)
    
    def validate_config(self, config: Dict, required_keys: list) -> bool:
        """
        Validate configuration has required keys.
        
        Args:
            config: Configuration dictionary
            required_keys: List of required keys
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If required keys are missing
        """
        missing = [key for key in required_keys if key not in config]
        
        if missing:
            raise ValueError(f"Missing required config keys: {missing}")
        
        # Check for dangerous default values
        dangerous = ['changeme', 'password', 'secret', 'test', 'demo']
        
        for key, value in config.items():
            if isinstance(value, str):
                if any(d in value.lower() for d in dangerous):
                    logger.warning(f"Config key '{key}' may contain unsafe value")
        
        return True


# Global instance
safe_file_ops = SafeFileOperations()

# Convenience functions
def safe_read(filepath: str, binary: bool = False) -> Union[str, bytes]:
    """Safely read file."""
    return safe_file_ops.safe_read(filepath, binary=binary)


def safe_write(filepath: str, content: Union[str, bytes, Dict], create_dirs: bool = True) -> None:
    """Safely write file."""
    safe_file_ops.safe_write(filepath, content, create_dirs=create_dirs)


def safe_read_json(filepath: str) -> Dict:
    """Safely read JSON file."""
    return safe_file_ops.safe_read_json(filepath)


def safe_write_json(filepath: str, data: Dict, create_dirs: bool = True) -> None:
    """Safely write JSON file."""
    safe_file_ops.safe_write_json(filepath, data, create_dirs=create_dirs)
