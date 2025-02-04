import json
import logging
import os
from util import DirectoryWatcher

_logger = logging.getLogger('utils')

class FileWatcher:
    def __init__ (self, file_path: str):
        self.file_path = os.path.abspath(file_path)

        if not os.path.exists(self.file_path):
            _logger.error(f'File not found: {file_path}')
            self.data = {}
            return

        self.file_name = os.path.basename(file_path)
        self.data = self._load()
        DirectoryWatcher.register_watcher(self)
        _logger.info(f'registered FileWatcher for: {file_path}')

    def _load(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            _logger.exception(f'Failed to load: {self.file_path}')
            return {}
    
    def reload(self):
        self.data = self._load()
        _logger.info(f'File: {self.file_name} updated')

    def __getitem__(self, key):
        return self.data.get(key, None)
    
    def __repr__(self):
        return f'FileWatcher({self.file_path}) -> {self.data}'