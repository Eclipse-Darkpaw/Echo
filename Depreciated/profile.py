"""
Handles all profile related functions.
File Version:2.0.1
"""
import discord
import json

from fileManagement import resource_file_path
from main import get_user_id, read_line


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
    
    embed = discord.Embed(title=member.display_name, description=profile['bio'])
    try:
        icon_url = member.guild_avatar.url
    except AttributeError:
        icon_url = member.avatar.url
    embed.set_thumbnail(url=icon_url)
    embed.color = member.color
    try:
        for field in profile['fields']:
            embed.add_field(name=field[0], value=field[1], inline=bool(field[2]))
    except KeyError:
        pass
    
    await message.channel.send(embed=embed)


async def add_field(message, client):
    title = ''
    value = ''
    inline = None
    
    # Get field title
    title = await read_line(client,
                            message.channel,
                            'Field title?',
                            message.author,
                            delete_prompt=False,
                            delete_response=False)
    title = title.content
    value = await read_line(client,
                            message.channel,
                            'Field text?',
                            message.author,
                            delete_prompt=False,
                            delete_response=False)
    value = value.content
    while inline is None:
        inline = await read_line(client,
                                 message.channel,
                                 'Field inline? (Y or N)',
                                 message.author,
                                 delete_response=False,
                                 delete_prompt=False)
        inline = inline.content
        
        if inline.lower() == "y" or inline.lower() == 'yes' or inline.lower() == 'true':
            inline = True
        elif inline.lower() == "n" or inline.lower() == 'no' or inline.lower() == 'false':
            inline = False
        else:
            inline = None
    
    with open(file_path) as file:
        data = json.load(file)
    field = (title, value, inline)
    data[str(message.author.id)]['profile']['fields'].append(field)
    
    with open(file_path, 'w') as file:
        file.write(json.dumps(data, indent=4))
    
    await message.reply('Field added!')


async def edit_field(message):
    # >profile field edit field_num name/value/inline <value>
    temp = message.content.split(' ', 5)
    if len(temp) == 6:
        junk0, junk1, junk2, field_num, type, value = message.content.split(' ', 5)
    else:
        await message.reply('Missing required argument')
    
    with open(file_path) as file:
        data = json.load(file)
    
    switch = {'name': 0, 'value': 1, 'inline': 2}
    
    try:
        data[str(message.author.id)]['profile']['fields'][int(field_num)-1][switch[type]] = value
    except KeyError:
        await message.reply("Invalid field section, please select either `name`, `value` or `inline` instead of "
                            + type)
        return
    except IndexError:
        await message.reply("That field doesn't exist!")
        return

    with open(file_path, 'w') as file:
        file.write(json.dumps(data, indent=4))
    
    await message.reply('Field edited successfully')
    

async def delete_field(message):
    # >profile field edit field_num name/value/inline <value>
    temp = message.content.split(' ', 3)
    if len(temp) == 4:
        junk0, junk1, junk2, field_num = message.content.split(' ', 3)
    else:
        raise TypeError('missing required argument`')
    
    with open(file_path) as file:
        data = json.load(file)
    
    temp = data[str(message.author.id)]['profile']['fields']
    
    try:
        del temp[int(field_num)-1]
    except ValueError:
        await message.reply('Please input a field number')
        return
    except IndexError:
        await message.reply("This field doesn't exist!")
        return
    
    data[str(message.author.id)]['profile']['fields'] = temp

    with open(file_path, 'w') as file:
        file.write(json.dumps(data, indent=4))
    
    await message.reply('Field deleted successfully')
