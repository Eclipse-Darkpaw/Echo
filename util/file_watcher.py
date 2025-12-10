import json
import logging
import os
from filelock import FileLock, Timeout
from util import DirectoryWatcher

_logger = logging.getLogger('utils')

class FileWatcher:
    def __init__ (self, file_path: str):
        self.file_path = os.path.abspath(file_path)

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        if not os.path.exists(self.file_path):
                with open(self.file_path, 'w', encoding="utf-8") as file:
                    json.dump({}, file, indent=4)

        self.file_name = os.path.basename(file_path)
        self.data = self._load()
        DirectoryWatcher.register_watcher(self)
        _logger.info(f'registered FileWatcher for: {file_path}')

    def _load(self):
        """
        Load JSON from file, respecting the file lock to avoid reading during writes.
        """
        lock = FileLock(f'{self.file_path}.lock')
        
        try:
            with lock.acquire(timeout=5):
                with open(self.file_path, 'r') as file:
                    return json.load(file)
        except Timeout:
            _logger.warning(f'Failed to acquire lock for reading: {self.file_path}, using cached data')
            return self.data if hasattr(self, 'data') else {}
        except json.JSONDecodeError:
            _logger.exception(f'Failed to decode JSON: {self.file_path}')
            return self.data if hasattr(self, 'data') else {}
        except FileNotFoundError:
            _logger.exception(f'File not found: {self.file_path}')
            return {}
    
    def reload(self):
        new_data = self._load()
        if new_data:  # Only update if we got valid data
            self.data = new_data
        _logger.info(f'File: {self.file_name} updated')

    def __getitem__(self, key):
        return self.data.get(key, None)
    
    def __repr__(self):
        return f'FileWatcher({self.file_path}) -> {self.data}'