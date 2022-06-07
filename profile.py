"""
File Version:2.0.0
"""
import discord
import json

from fileManagement import profile_path, resource_file_path
from main import get_user_id


# name, join date, bio, icon
file_path = resource_file_path + 'global_files.json'

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
    with open(file_path,'r') as file:
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
            embed.add_field(field)
    except KeyError:
        pass
    
    await message.channel.send(embed=embed)



