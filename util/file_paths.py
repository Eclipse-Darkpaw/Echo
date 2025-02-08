import os

class FilePaths:
    _root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = f'{_root_dir}/data'
    logs_dir = f'{_root_dir}/logs'
    artfight_archive_dir = f'{data_dir}/artfight_archive'

    servers_settings = f'{data_dir}/servers.json'
    artfight = f'{data_dir}/artfight.json'
    servers_warns = f'{data_dir}/warns.json'
    scam_log = f'{logs_dir}/scam.log'
    
    @classmethod
    def get_ref(cls, user_id):
        return f'{cls.data_dir}/refs/{user_id}.refs'
    
    @classmethod
    def get_nsfw_ref(cls, user_id):
        return f'{cls.data_dir}/nsfw/refs/{user_id}.nsfwref'