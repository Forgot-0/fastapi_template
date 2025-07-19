from dataclasses import dataclass
from typing import List, Literal
import logging
import sys
from pathlib import Path

HandlerType = Literal['stream', 'file']


@dataclass
class LogService:
    level: str = 'INFO'
    handlers: List[HandlerType] = None
    
    def __post_init__(self):
        """Initialize logging configuration."""
        if self.handlers is None:
            self.handlers = ['stream']
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Convert string level to logging level
        log_level = getattr(logging, self.level.upper(), logging.INFO)
        
        # Create logger
        self.logger = logging.getLogger('app')
        self.logger.setLevel(log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Add handlers based on configuration
        if 'stream' in self.handlers:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setLevel(log_level)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)
        
        if 'file' in self.handlers:
            # Create logs directory if it doesn't exist
            logs_dir = Path('logs')
            logs_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(logs_dir / 'app.log')
            file_handler.setLevel(log_level)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)