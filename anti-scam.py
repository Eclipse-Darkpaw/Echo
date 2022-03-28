import discord
import os
import sys
import time

version_num = '1.4.0'

prefix = '>'
log_channel = 933539437357432892     # channel ID of the channel where logs go
token = os.environ.get('ANTI-SCAM_TOKEN')      # put the bot token in the quotes

game = discord.Game('Scanning for pings')
client = discord.Client()


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


async def version(message):
    """
    Returns the current version of the bot
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :param message: message that called the command
    :return: None
    """
    await message.channel.send('I am currently running version ' + version_num)


async def quit(message):
    """
    Quits the bot, and closes the program. Replys and updates the game status to alert users to it quitting.
    :param message: message that called the quit command
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :return: N/A. program closes
    """
    global game
    if message.author.guild_permissions.administrator:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def scan_message(message, is_flagged=False):
    """
    The primary anti-scam method. This method is given a message, counts the number of flags in a given message, then
    does nothing if no flags, flags the message as a possible scam if 1-3, or flags and deletes the message at 3+ flags.
    Last docstring edit: -Autumn V1.2.2
    Last method edit: -Autumn V1.2.3
    :param message: the message sent
    :param is_flagged: if the message is flagged for deletion
    :return: None
    """
    flags = 0
    content = message.content.lower()

    for word in blacklist:
        index = content.find(word)
        if index != -1:
            flags += 1

    if flags < 2:
        return
    else:
        if flags >= 3 and is_flagged is False:
            await message.delete()

        content = message.content.replace('@', '@ ')

        channel = message.guild.get_channel(log_channel)

        embed = discord.Embed(title='Possible Scam in #' + str(message.channel.name), color=0xFF0000)
        embed.set_author(name='@' + str(message.author.name), icon_url=message.author.avatar_url)
        embed.add_field(name='message', value=content, inline=False)
        embed.add_field(name='Flags', value=str(flags), inline=False)
        embed.add_field(name='Sender ID', value=message.author.id)
        embed.add_field(name='Channel ID', value=message.channel.id)
        embed.add_field(name='Message ID', value=message.id)

        if flags < 3:
            embed.add_field(name='URL', value=message.jump_url, inline=False)
        await channel.send(embed=embed)


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


switcher = {'ping': ping, 'version': version, 'quit': quit}
blacklist = ['@everyone', 'https://', 'gift', 'nitro', 'steam', '@here', 'free', 'who is first? :)', "who's first? :)"]
code = 'plsdontban'     # flag escape code


@client.event
async def on_message(message):
    """
    When a message happens, it scans the message for
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :param message: the message sent
    :return: n/a
    """
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        if not message.author.guild_permissions.mention_everyone:
            await scan_message(message, True)
            await message.delete()
    content = message.content.lower()
    if content.find(code) != -1 or message.author.guild_permissions.administrator:
        pass
    else:
        await scan_message(message)

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
    inp = int(input('Input a bot num\n1. Anti-scam\n'))
    if inp == 1:
        client.run(token)


if __name__ == '__main__':
    run_antiscam()
