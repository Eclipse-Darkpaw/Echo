from os import path

bot_path = path.dirname(path.abspath(__file__))
resource_file_path = f'{bot_path}/resources/'
server_settings_path = resource_file_path + 'servers.json'
server_warns_path = resource_file_path + 'warns.json'
log_path = f'{bot_path}/logs'


def get_leaderboard_path(guild_id):
    return resource_file_path + 'Guild-files/{}/.leaderboard'.format(guild_id)


def profile_path(target_id):
    return resource_file_path + 'profile/{}.profile'.format(target_id)


def ref_path(target_id):
    return resource_file_path + 'refs/{}.refs'.format(target_id)


def oc_folder_path(target_id):
    return resource_file_path + 'refs/{}'.format(target_id)


def oc_path(target_id, oc_name):
    return resource_file_path + 'refs/{}/{}.ref'.format(target_id, oc_name)


def sona_path(target_id):
    return resource_file_path + 'refs/' + str(target_id) + '/00.refs'


def char_path(target_id, char):
    return resource_file_path + 'refs/' + str(target_id) + '/' + str(char) + '.refs'


def nsfw_ref_path(target_id):
    return resource_file_path + f'nsfw/refs/{target_id}.nsfwref'


def folder_path(target_id, folder):
    return resource_file_path + 'refs/{}/{}'.format(target_id, folder)


def artfight_scores():
    return resource_file_path + 'artfight/artfight.scores'


def warn_log_path(user_id):
    return resource_file_path + 'warns/{}'.format(user_id)


def ref_folder_path():
    return resource_file_path + 'refs'


def scam_log_path():
    return f'{log_path}/scam.log'

def artfight_members_path():
    return f'{resource_file_path}/artfight-members.json'
