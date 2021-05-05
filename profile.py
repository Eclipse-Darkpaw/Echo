import discord
from fileManagement import profile_path, member_badges_path



# name, join date, bio, icon


async def create_profile(member, message):
    try:
        open(profile_path(str(member.id)), 'x')
    except FileExistsError:
        await message.channel.send('You already have a profile!')
        return
    bio = 'This user has not set a bio yet\n'
    name_history = member.name+'\n'
    badges = ''
    lines = [bio,name_history,'0',badges]
    with open(profile_path(str(member.id)), 'w') as profile:
        for line in lines:
            profile.write(line)


def set_bio(member, bio):
    bio = bio.replace('\n','/n')
    with open(profile_path(str(member))) as profile:
        lines = profile.readlines()
    lines[0] = bio+'\n'
    with open(profile_path(str(member)), 'w') as profile:
        for line in lines:
            profile.write(line)


def name_change(member):
    with open(profile_path(str(member.id))) as profile:
        lines = profile.readlines()
    lines[1] = lines[1] + '->' + member.name
    with open(profile_path(str(member.id)), 'w') as profile:
        for line in lines:
            profile.write(line)

# Todo: remove feature
def member_leave(member):
    with open(profile_path(str(member.id))) as profile:
        lines = profile.readlines()
        lines[2] = str(int(lines[2]) + 1) + '\n'
    with open(profile_path(str(member.id)), 'w') as profile:
        for line in lines:
            profile.write(line)


async def display_profile(message, member=None):
    if member is None:
        member = message.author
    try:
        file = open(profile_path(str(member.id)))
        file.close()
    except FileNotFoundError:
        await create_profile(member, message)
    with open(profile_path(str(member.id))) as file:
        lines = file.readlines()

        lines[0]=lines[0].replace('/n','\n')
        embed = discord.Embed()
        embed.set_author(name=member.name,icon_url=member.avatar_url)
        embed.color = member.color
        embed.add_field(name='Bio',value=lines[0],inline=False)
        embed.add_field(name='Name History',value=lines[1])
        embed.add_field(name='Times Left',value=lines[2])
        #embed.add_field(name='Badges',value=badges)
        await message.channel.send(embed=embed)
