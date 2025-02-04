import os
from util import FileWatcher

class FilePaths:
    _bot_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _data_dir = f'{_bot_path}/data'
    _logs_dir = f'{_bot_path}/logs'

    servers_settings = f'{_data_dir}/servers.json'
    servers_warns = f'{_data_dir}/warns.json'
    artfight_members = f'{_data_dir}/artfight-members.json'
    scam_log = f'{_logs_dir}/scam.log'
    
    @classmethod
    def get_ref(cls, user_id):
        return f'{cls._data_dir}/refs/{user_id}.refs'
    
    @classmethod
    def get_nsfw_ref(cls, user_id):
        return f'{cls._data_dir}/nsfw/refs/{user_id}.nsfwref'

class WatchedFiles:
    _files = {}

    @classmethod
    def get_file_data(cls, file_path: str):
        if file_path not in cls._files:
            cls._files[file_path] = FileWatcher(file_path)

        return cls._files[file_path]