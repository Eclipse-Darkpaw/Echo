import os

from config import Paths
from util import add_to_file

class Repository:
    pass

class JsonRepository(Repository):
    def _get(self, data: dict, *keys: str) -> any:
        try:
            for key in keys:
                if data is None:
                    return None
                data = data[key]
            return data
        except (KeyError, TypeError):
            return None
        
    def _set(self, data: dict, *keys: str, value: any) -> None:
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]

        data[keys[-1]] = value

    def _remove(self, data: dict, *keys) -> None:
        for key in keys[:-1]:
            if key in data:
                data = data[key]
            else:
                pass
        
        if keys[-1] in data:
            del data[keys[-1]]

class LogRepository(Repository):
    def __init__(self):
        os.makedirs(Paths.logs_dir, exist_ok=True)

    def _log(self, log_file_path: str, content: str):
        add_to_file(file_path=log_file_path, content=content)
    
    def log(self, content: str):
        raise NotImplementedError()