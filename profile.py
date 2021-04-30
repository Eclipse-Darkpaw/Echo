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


async def create_profile(member, message):
    try:
        open('profile\\'+str(member.id)+'.profile','x')
    except FileExistsError:
        await message.channel.send('You already have a profile!')
        return
    bio = 'This user has not set a bio yet\n'
    name_history = member.name+'\n'
    badges = ''
    lines = [bio,name_history,'0',badges]
    with open('profile/'+str(member.id)+'.profile','w') as profile:
        for line in lines:
            profile.write(line)


def set_bio(member, bio):
    with open('profile/'+member+'.profile') as profile:
        lines = profile.readlines()
    lines[0] = bio+'\n'
    with open('profile/'+member+'.profile','w') as profile:
        for line in lines:
            profile.write(line)


def name_change(member):
    with open('profile/'+member.id+'.profile') as profile:
        lines = profile.readlines()
    lines[1] = lines[1] + '->' + member.name
    with open('profile/'+member+'.profile','w') as profile:
        for line in lines:
            profile.write(line)


def member_leave(member):
    with open('profile/'+str(member.id)+'.profile') as profile:
        lines = profile.readlines()
    lines[2] = str(int(lines[2]) + 1)
    with open('profile/'+str(member.id)+'.profile','w') as profile:
        for line in lines:
            profile.write(line)

async def display_profile(message, member=None):
    if member is None:
        member = message.author
    try:
        file = open('profile/'+str(member.id)+'.profile')
        file.close()
    except FileNotFoundError:
        await create_profile(member, message)
    with open('profile/'+str(member.id)+'.profile') as file:
        lines = file.readlines()
        if len(lines) == 3:
            lines.append('None')
        embed = discord.Embed()
        embed.set_author(name=member.name,icon_url=member.avatar_url)
        embed.color = member.color
        embed.add_field(name='Bio',value=lines[0],inline=False)
        embed.add_field(name='Name History',value=lines[1])
        embed.add_field(name='Times Left',value=lines[2])
        embed.add_field(name='Badges',value=lines[3])
        await message.channel.send(embed=embed)

def member_leave(member):
    pass
