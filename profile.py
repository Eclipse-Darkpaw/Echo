"""
Handles all profile related functions.
File Version:2.0.1
"""
import discord
import json

from fileManagement import profile_path, resource_file_path
from main import get_user_id


# name, join date, bio, icon
file_path = resource_file_path + 'global_files.json'


def set_bio(member, bio):
    with open(file_path, 'r') as file:
        data = json.load(file)
    try:
        data[str(member.id)]
    except KeyError:
        data[str(member.id)] = {}
    
    try:
        data[str(member.id)]['profile']
    except KeyError:
        data[str(member.id)]['profile'] = {}
    
    data[str(member.id)]['profile']['bio'] = bio
    
    with open(file_path, 'w') as file:
        file.write(json.dumps(data, indent=4))


async def display_profile(message, client):
    command = message.content.split(' ', 1)
    if len(command) > 1:
        if message.guild is None:
            member = client.get_user(get_user_id(message, 1))
        else:
            member = message.guild.get_member(get_user_id(message, 1))
    else:
        member = message.author
    # member variable is the member who's profile we want to display. I should probably name it target or something more
    # obvious later. for now i just wanna make it work
    
    with open(file_path) as file:
        data = json.load(file)
    
    try:
        profile = data[str(member.id)]['profile']
    except KeyError:
        profile = {'bio': "This user has not set a bio yet"}
    
    embed = discord.Embed(title=member.display_name,
                                  description=profile['bio'])
    embed.set_thumbnail(url=member.avatar_url)
    embed.color = member.color
    try:
        for field in profile['fields']:
            embed.add_field(name=field[0], value=field[1], inline=field[2])
    except KeyError:
        pass
    
    await message.channel.send(embed=embed)


async def add_field(message):
    # TODO: add this function
    await message.reply('This isnt ready yet!\n<@440232487738671124>, Hurry up and fix me!')
    if True:
        return
    title = ''
    with open(file_path) as file:
        data = json.load(file)
    field = (title, value, inline)
    data[str(message.author.id())]['profile']['fields'].append(field)
    
    with open(file_path, 'w') as file:
        file.write(json.dumps(data, indent=4))


async def edit_field(message, field_num, value):
    await message.reply('This isn\'t ready yet!\n<@440232487738671124> Please fix me already!')
    with open(file_path) as file:
        data = json.load(file)
    
    data[str(message.author.id())]['profile']['fields'][field_num][1] = value

    with open(file_path, 'w') as file:
        file.write(json.dumps(data, indent=4))
    

async def delete_field(message):
    # TODO: add this function
    await message.reply('This isnt ready to use yet! Sorry!\n*<@440232487738671124>, hurry up and fix me!*')
    raise NotImplementedError('delete_field is not implemented yet')
