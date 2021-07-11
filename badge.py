from disord import Embed
from fileManagement import guild_badges_path, member_badges_path

# STAT: DEPRECIATED. WILL NOT BE USED.
# REQ: DISCONNECT AND DELETE FILE.

class Badge:
    def __init__(self, icon, name, explanation, message):
        self.__icon = icon
        self.__name = name
        self.__explanation = explanation
        filename = guild_badges_path(message.guild.id)
        with open(filename,'a') as file:
            file.write(self.save_string())

    def get_icon(self):
        return self.__icon

    def get_name(self):
        return self.__icon + ' - ' + self.__name

    def get_explanation(self):
        return self.__explanation

    def save_string(self):
        return self.__icon + ',' + self.__name + ',' + self.__explanation + '\n'

    def award(self, target):
        pass

    def save(self, message):
        fp = guild_badges_path(message.guild.id)
        with open(fp, 'a') as file:
            file.write(self.save_string())


def award(guild_id, target_id, badge_num):
    fp = member_badges_path(guild_id, target_id)
    with open(fp) as file:
        lines = file.readlines()
    lines[badge_num]='True\n'
    with open(fp,'w'):
        for line in lines:
            file.write(line)


def load_badge(guild_id, badge_num):
    fp = guild_badges_path(guild_id)
    with open(fp) as file:
        badges = file.readlines()
        badge = badges[badge_num].split('|')
    return Badge(badge[0], badge[1], badge[2])


def show_badge(guild_id,badge_num):
    fp = guild_badges_path(guild_id)
    with open(fp) as file:
        badges = file.readlines()
        return


def display_badges(message, guild_id=message.guild.id):
    fp = guild_badges_path(guild_id)
    embed = Embed()
    with open(fp) as file:
        badges = file.readlines()
        for i in range(len(badges)):
            badges[i] = badges[i].split('|')
            embed.add_field(name=str(badges[badge_num][0]) + str(badges[badge_num][1]),value=badges[badge_num][2])
    message.channel.send(embed=embed)
