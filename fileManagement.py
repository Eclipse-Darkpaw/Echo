def get_leaderboard_path(guild_id):
    return 'C:\\Users\\leebe\\Desktop\\Guild-files\\{}\\.leaderboard'.format(guild_id)


def profile_path(target_id):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\profile\\{}.profile'.format(target_id)


def ref_path(target_id):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\{}.refs'.format(target_id)


def oc_folder_path(target_id):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\{}'.format(target_id)


def oc_path(target_id, oc_name):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\{}\\{}.ref'.format(target_id, oc_name)


def sona_path(target_id):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\' + str(target_id) + '\\00.refs'


def char_path(target_id, char):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\' + str(target_id) + '\\' + str(char) + '.refs'


def folder_path(target_id, folder):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\{}\\{}'.format(target_id, folder)


# Unused feature. Safe to remove.
def member_badges_path(guild_id, target_id):
    return 'C:\\Users\\leebe\\Desktop\\Guild-files\\' + str(guild_id) + '\\'+ str(target_id) + '.badges'


# Unused feature. Safe to remove
def guild_badges_path(guild_id):
    return 'C:\\Users\\leebe\\Desktop\\Guild-files\\' + str(guild_id) + '\\.badges'
