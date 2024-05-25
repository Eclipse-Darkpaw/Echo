import os
import json
import discord
import modules.AntiScam as AntiScam
import modules.General as General
import sys
from main import read_line, eclipse_id
from fileManagement import resource_file_path

version_num = '3.3.1'

prefix = '>'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

game = discord.Game(prefix + "help for commands")
client = discord.Client(intents=intents)


async def setup(message):
    """
    Sets up a server for the bot to run
    Last docstring edit: -Autumn V3.3.0
    Last method edit: -Autumn V3.3.0
    :param message: message that called the bot
    :return:
    """
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
            elif 0 <= i < 1:
                msg += f'\n**{responses[i][0]}:** <#{responses[i][1]}>'
            else:
                msg += f'\n**{responses[i][0]}:** {responses[i][1]}'
        await progress.edit(content=msg)

    channels = ['log']
    channelIDs = {}
    for channel in channels:
        while True:
            response = await read_line(client,
                                       message.channel,
                                       f'Please tag the {channel} channel. The bot will send messages here when a '
                                       f'scam is detected.',
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
                
    server_data = {"name": message.guild.name,
                   "channels": channelIDs}
    
    with open(resource_file_path + 'servers.json') as file:
        data = json.load(file)
    data[str(message.guild.id)] = server_data
    with open(resource_file_path + 'servers.json', 'w') as file:
        file.write(json.dumps(data, indent=4))
    
    await message.reply('Setup complete')


async def ping(message):
    """
    Returns how long it takes the bot to send a message
    Last docstring edit: -Autumn V1.2.2
    Last method edit: -Autumn V3.3.0
    :param message: message that called the quit command
    :return: None
    """
    await General.ping(message)


async def version(message):
    """
    Returns the current version of the bot
    Last docstring edit: -Autumn V1.2.2
    Last method edit: -Autumn V3.3.0
    :param message: message that called the command
    :return: None
    """
    await General.version(message, version_num)


async def quit(message):
    """
    Quits the bot, and closes the program. Replies and updates the game status to alert users to it quitting.
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :param message: message that called the quit command
    :return: N/A. program closes
    """
    await General.quit(message, client)


@client.event
async def on_ready():
    """
    Confirms the bot is online, and has started
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :return: N/A
    """
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=game)
    await client.get_user(eclipse_id).send('Ready and Active')


switcher = {'ping': ping, 'version': version, 'quit': quit, 'setup': setup}


@client.event
async def on_message(message):
    """
    When a message happens, it scans the message for
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :param message: the message sent
    :return: n/a
    """
    
    if message.author.bot:
        return
    
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        if not message.author.guild_permissions.mention_everyone:
            await AntiScam.scan_message(message)
    content = message.content.lower()
    
    if message.guild is None or content.find(AntiScam.code) != -1 or message.author.guild_permissions.administrator:
        pass
    else:
        await AntiScam.scan_message(message, client)
    
    if message.content.startswith(prefix):
        command = message.content[1:].lower().split(' ', 1)
        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            pass
        if command[0] == 'print':
            print(message.content)


def run_antiscam():
    if len(sys.argv) > 1:
        inp = int(sys.argv[1])
    else:
        inp = int(input('Input a bot num\n1. Anti-scam\n'))
    
    if inp == 1:
        client.run(os.environ.get('PUBLIC_ANTI-SCAM_TOKEN'))


if __name__ == '__main__':
    run_antiscam()
