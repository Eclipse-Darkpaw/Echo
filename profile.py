import discord
from fileManagement import profile_path
from main import get_user_id


# name, join date, bio, icon


def create_profile(member):
    try:
        open(profile_path(str(member.id)), 'x')
    except FileExistsError:
        return
    bio = 'This user has not set a bio yet\n'
    lines = [bio]
    with open(profile_path(str(member.id)), 'w') as profile:
        for line in lines:
            profile.write(line)


def set_bio(member, bio):
    error = 0
    bio = bio.replace('\n','/n')
    try:
        file = open(profile_path(str(member.id)))
        file.close()
    except FileNotFoundError:
        create_profile(member)
    with open(profile_path(str(member))) as profile:
        lines = profile.readlines()
    lines[0] = bio+'\n'
    with open(profile_path(str(member)), 'w') as profile:
        for line in lines:
            try:
                print(line)
                profile.write(line)
            except UnicodeEncodeError: 
                profile.write('null\n')
                print(line)
                error = 1
    if error > 0:
        raise ValueError('Operation failed')


async def display_profile(message):
    member = message.guild.get_member(get_user_id(message))
    try:
        file = open(profile_path(str(member)))
        file.close()
    except FileNotFoundError:
        create_profile(member)
    with open(profile_path(str(member.id))) as file:
        lines = file.readlines()

        lines[0]=lines[0].replace('/n','\n')
        embed = discord.Embed()
        embed.set_author(name=member.name,icon_url=member.avatar_url)
        embed.color = member.color
        embed.add_field(name='Bio',value=lines[0],inline=False)
        await message.channel.send(embed=embed)
