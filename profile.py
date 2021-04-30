import discord


class Badge:
    def __init__(self, icon, name, explanation, message):
        self.__icon = icon
        self.__name = name
        self.__explanation = explanation
        filename = str(message.guild.id) + '.badges'
        with open(filename,'a') as file:
            file.write(self.save_string())

    def get_icon(self):
        return self.__icon

    def get_name(self):
        return self.__icon + ' - ' + self.__name

    def get_explanation(self):
        return self.__explanation

    def save_string(self):
        return self.__icon + ',' + self.__name + ',' + self.__explanation


# name, join date, bio, icon


def create_profile(message):
    member = message.author
    try:
        open(member.id+'.profile','x')
    except FileExistsError:
        await message.channel.send('You already have a profile!')
        return
    bio = 'This user has not set a bio yet'
    name_history = member.name
    ref_location = ''
    badges = ''
    lines = [bio,name_history,0,ref_location,badges]
    with open(member.id+'.profile','w') as profile:
        profile.writelines(lines)


def set_bio(member, bio):
    with open(member+'.profile') as profile:
        lines = profile.readlines()
    lines[0] = bio
    with open(member+'.profile','w') as profile:
        for line in lines:
            profile.write(line)


def name_change(member):
    with open(member.id+'.profile') as profile:
        lines = profile.readlines()
    lines[1] = lines[1] + '->' + member.name
    with open(member+'.profile','w') as profile:
        for line in lines:
            profile.write(line)


def member_leave(member):
    with open(member.id+'.profile') as profile:
        lines = profile.readlines()
    lines[2] = str(int(lines[2]) + 1)
    with open(member+'.profile','w') as profile:
        for line in lines:
            profile.write(line)


def set_ref(message):
    raise NotImplementedError('Figure out how to save a file as a specific name')

def display_profile(member):
    embed = discord.Embed()
    embed.set_author(name=member.name)

def member_leave(member):
    pass
