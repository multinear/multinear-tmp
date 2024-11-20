import sys
import logging
import time
import re


class OutputCapture:
    def __init__(self):
        self.logs = []
        self._original_stdout = None
        self._log_handler = None
        # Regex pattern for ANSI escape codes
        self._ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    def _create_log_handler(self):
        handler = logging.Handler()
        handler.setLevel(logging.DEBUG)
        
        def emit(record):
            self.logs.append({
                'level': record.levelname,
                'message': handler.format(record),
                'timestamp': record.created,
                'module': record.module
            })
        handler.emit = emit
        return handler
    
    def write(self, text):
        if text.strip():
            # Strip ANSI escape codes before storing
            clean_text = self._ansi_escape.sub('', text.strip())
            self.logs.append({
                'level': 'PRINT',
                'message': clean_text,
                'timestamp': time.time(),
                'module': 'stdout'
            })
        self._original_stdout.write(text)

    def flush(self):
        self._original_stdout.flush()

    def __enter__(self):
        # Setup stdout capture
        self._original_stdout = sys.stdout
        sys.stdout = self
        
        # Setup logging capture
        self._log_handler = self._create_log_handler()
        logging.getLogger().addHandler(self._log_handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore stdout
        sys.stdout = self._original_stdout
        
        # Remove log handler
        if self._log_handler:
            logging.getLogger().removeHandler(self._log_handler)
