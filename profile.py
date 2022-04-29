import discord
from fileManagement import profile_path
from main import get_user_id


# name, join date, bio, icon


def create_profile(member, bio='This user has not set a bio yet\n'):
    try:
        open(profile_path(str(member.id)), 'x')
    except FileExistsError:
        return
    lines = [bio]
    with open(profile_path(str(member.id)), 'w') as profile:
        for line in lines:
            profile.write(line)


def set_bio(member, bio):
    """Sets a member's bio"""
    status = 0
    bio = bio.replace('\n', '/n')
    try:
        file = open(profile_path(str(member.id)))
        file.close()
    except FileNotFoundError:
        create_profile(member, bio)
        return
    with open(profile_path(str(member.id))) as profile:
        lines = profile.readlines()
    lines[0] = bio+'\n'
    with open(profile_path(str(member.id)), 'w') as profile:
        for line in lines:
            try:
                print(line)
                profile.write(line)
            except UnicodeEncodeError: 
                profile.write('null\n')
                print(line)
                status = -1
    if status == -1:
        raise ValueError('Operation failed, please use ASCII characters')


async def display_profile(message, client):
    command = message.content.split(' ', 1)
    if len(command) > 1:
        member = client.get_user(get_user_id(message, 1))
    else:
        member = message.author
    try:
        file = open(profile_path(str(member.id)))
        file.close()
    except FileNotFoundError:
        create_profile(member)
    with open(profile_path(str(member.id))) as file:
        lines = file.readlines()

        lines[0] = lines[0].replace('/n', '\n')
        embed = discord.Embed()
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.color = member.color
        embed.add_field(name='Bio',
                        value=lines[0],
                        inline=False)
        await message.channel.send(embed=embed)


async def profile(message):
    """
    Displays a users profile
    Last docstring edit: -Autumn | V2.1.0
    Last function edit: -Autumn | Unknown Version
    :param message: message calling the bot
    :return: None
    """
    command = message.content.split(' ', 2)
    if command[1] == 'edit':
        try:
            set_bio(message.author, command[2])
            await message.channel.send('Bio set')
        except ValueError:
            await message.channel.send('Error. Bio not set, please use ASCII characters and custom emotes.')
    else:
        await display_profile(message, client)
