def get_leaderboard_path(guild_id):
    return 'C:\\Users\\leebe\\Desktop\\Guild-files\\' + str(guild_id) + '\\.leaderboard'

def profile_path(target_id):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\profile\\' + str(target_id) + '.profile'

def ref_path(target_id):
    return 'C:\\Users\\leebe\\Desktop\\Bot-files\\refs\\' + str(target_id) + '.refs'

def joinleave_path(guild_id):
    return 'C:\\Users\\leebe\\Desktop\\Guild-files\\' + str(guild_id.guild.id) + '\\.joinleave'

def member_badges_path(guild_id, target_id):
    return 'C:\\Users\\leebe\\Desktop\\Guild-files\\' + str(guild_id) + '\\'+ str(target_id) + '.badges'

def guild_badges_path(guild_id):
    return 'C:\\Users\\leebe\\Desktop\\Guild-files\\' + str(guild_id) + '\\.badges' 