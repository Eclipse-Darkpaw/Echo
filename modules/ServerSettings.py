import discord
import json

from main import read_line
from fileManagement import resource_file_path


async def setup(message, client):
    """
    sets up the bot for initial usage
    Last docstring edit: -Autumn V3.0.0
    Last method edit: -Autumn V3.2.0
    :param message: message calling the bot
    :param client: bot client
    :return: None
    """
    progress = await message.channel.send("**__Assignments__**")
    responses = []
    
    async def update_progress():
        msg = "**__Assignments__**"
        for i in range(len(responses)):
            if str(responses[i][1]).lower() == 'none':
                msg += f'\n**{responses[i][0]}:** {responses[i][1]}'
            elif 0 <= i < 5:
                msg += f'\n**{responses[i][0]}:** <#{responses[i][1]}>'
            elif 5 <= i < 10:
                msg += f'\n**{responses[i][0]}:** <@&{responses[i][1]}>'
            else:
                msg += f'\n**{responses[i][0]}:** {responses[i][1]}'
        await progress.edit(content=msg)

    channels = ['application', 'questioning', 'mailbox', 'log', 'warn log']
    channelIDs = {}
    for channel in channels:
        while True:
            response = await read_line(client,
                                       message.channel,
                                       f'Please tag the {channel} channel, or "None" if it doesnt exist',
                                       target=message.author,
                                       delete_prompt=True,
                                       delete_response=True)
            if response.content.lower() == 'none':

                responses.append((channel, "none"))
                await update_progress()
                break
            try:
                channelIDs[channel] = response.channel_mentions[0].id
                responses.append((channel, response.channel_mentions[0].id))
                await update_progress()
                break
            except IndexError:
                await message.reply('No channels were mentioned')
    
    roles = ['member', 'unverified', 'questioning', 'suspended', 'mod']
    roleIDs = {}
    for role in roles:
        while True:
            response = await read_line(client,
                                       message.channel,
                                       f'Please tag the {role} role, or "None" if it doesnt exist',
                                       target=message.author,
                                       delete_prompt=True,
                                       delete_response=True)
            if response.content.lower() == 'none':
                responses.append((role, 'none'))
                await update_progress()
                break
            
            try:
                roleIDs[role] = response.role_mentions[0].id
                responses.append((role, response.role_mentions[0].id))
                await update_progress()
                break
            except IndexError:
                await message.reply('No channels were mentioned')
    
    codeword = -1
    while codeword == -1:
        response = await read_line(client,
                                   message.channel,
                                   f'What is the server codeword/password? Input "None" if there isnt one',
                                   target=message.author,
                                   delete_prompt=True,
                                   delete_response=True)

        responses.append((channel, response.content))
        await update_progress()
        if response.content.lower() == 'none':
            codeword = None
            break
        else:
            codeword = response.content
    
    server_data = {"name": message.guild.name,
                   "codeword": codeword,
                   "channels": channelIDs,
                   "roles": roleIDs}
    
    with open(resource_file_path + 'servers.json') as file:
        data = json.load(file)
    data[str(message.guild.id)] = server_data
    with open(resource_file_path + 'servers.json', 'w') as file:
        file.write(json.dumps(data, indent=4))
    
    await message.reply('Setup complete')
