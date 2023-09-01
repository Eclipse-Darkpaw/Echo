import discord
import sys
import time

import main


async def ping(message):
    """
    Returns how long it takes the bot to send a message
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :param message: message that called the quit command
    :return: None
    """
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message, version_num):
    """
    Returns the current version of the bot
    Last docstring edit: -Autumn V1.2.2
    Last method edit: -Autumn V3.3.0
    :param message: message that called the command
    :return: None
    """
    await message.channel.send('I am currently running version ' + version_num)


async def quit(message, client, c=None):
    """
    Quits the bot, and closes the program. Replys and updates the game status to alert users to it quitting.
    :param message: message that called the quit command
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :return: N/A. program closes
    """
    global game
    
    if message.author.id == main.eclipse_id or message.author.guild_permissions.administrator:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        if c is not None:
            c.send(b'quit()')
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')