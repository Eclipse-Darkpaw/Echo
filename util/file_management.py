import os
from util import FileWatcher

class FilePaths:
    _bot_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _data_dir = f'{_bot_path}/data'
    _logs_dir = f'{_bot_path}/logs'

    @property
    def servers_settings(cls):
        return f'{cls._data_dir}/servers.json'
    
    @property
    def servers_warns(cls):
        return f'{cls._data_dir}/warns.json'
    
    @property
    def artfight_members(cls):
        return f'{cls._data_dir}/artfight-members.json'
    
    @property
    def scam_log(cls):
        return f'{cls._logs_dir}/scam.log'
    
    @classmethod
    def get_ref_path(cls, user_id):
        return f'{cls._data_dir}/refs/{user_id}.refs'
    
    @classmethod
    def get_nsfw_ref_path(cls, user_id):
        return f'{cls._data_dir}/nsfw/refs/{user_id}.nsfwref'

class WatchedFiles:
    _files = {}

    @classmethod
    def get_file_data(cls, file_path: str):
        if file_path not in cls._files:
            cls._files[file_path] = FileWatcher(file_path)

        return cls._files[file_path]