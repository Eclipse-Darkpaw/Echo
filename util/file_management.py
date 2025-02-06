import os
from util import FileWatcher

class FilePaths:
    _root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = f'{_root_dir}/data'
    logs_dir = f'{_root_dir}/logs'

    servers_settings = f'{data_dir}/servers.json'
    servers_warns = f'{data_dir}/warns.json'
    artfight_members = f'{data_dir}/artfight-members.json'
    scam_log = f'{logs_dir}/scam.log'
    
    @classmethod
    def get_ref(cls, user_id):
        return f'{cls.data_dir}/refs/{user_id}.refs'
    
    @classmethod
    def get_nsfw_ref(cls, user_id):
        return f'{cls.data_dir}/nsfw/refs/{user_id}.nsfwref'

class WatchedFiles:
    _files = {}

    @classmethod
    def get_file_data(cls, file_path: str):
        if file_path not in cls._files:
            cls._files[file_path] = FileWatcher(file_path)

        return cls._files[file_path]