def get_leaderboard_path(guild_id):
    return 'C:\\Users\\leebe\\Desktop\\Guild-files\\' + str(guild_id) + '\\.leaderboard'


def profile_path(target_id):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\profile\\' + str(target_id) + '.profile'


def ref_path(target_id):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\' + str(target_id) + '.refs'


def oc_folder_path(target_id):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\' + str(target_id)

def oc_path(target_id, oc_name):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\' + str(target_id) + '\\' + str(oc_name)


def sona_path(target_id):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\' + str(target_id) + '\\00.refs'


def char_path(target_id, char):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\' + str(target_id) + '\\' + str(char) + '.refs'


def folder_path(target_id, folder):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\' + str(target_id) + '\\' + folder


def member_badges_path(guild_id, target_id):
    return 'C:\\Users\\leebe\\Desktop\\Guild-files\\' + str(guild_id) + '\\'+ str(target_id) + '.badges'


def guild_badges_path(guild_id):
    return 'C:\\Users\\leebe\\Desktop\\Guild-files\\' + str(guild_id) + '\\.badges'
