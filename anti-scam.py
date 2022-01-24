import discord
import sys
import time

version_num = '1.2.1'

prefix = '>'
log_channel = 933539437357432892     #channel ID of the channel where logs go
token = 'OTMzNTQwOTg1NjY3OTkzNjcx.YejByw.dISKG7JJOBC2L3BAIPmqEpHHJMQ'          # put the bot token in the quotes

game = discord.Game('Scanning for pings')
client = discord.Client()


async def ping(message):
    '''
    Returns how long it takes the bot to send a message
    :param message: message that called the quit command
    :return:
    '''
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message):
    '''
    Returns the current version of the bot
    :param message: message that called the command
    :return:
    '''
    await message.channel.send('I am currently running version ' + version_num)


async def quit(message):
    '''
    Quits the bot, and closes the program. Replys and updates the game status to alert users to it quitting.
    :param message: message that called the quit command
    :return: N/A. program closes
    '''
    global game
    if message.author.guild_permissions.administrator:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def flag_message(message, code=0, flags=0):
    await message.delete()
    content = message.content.replace('@', '@ ')

    channel = message.guild.get_channel(log_channel)

    embed = discord.Embed(title='Possible scam in #' + str(message.channel.name), color=0xFF0000)
    embed.set_author(name='@' + str(message.author.name), icon_url=message.author.avatar_url)
    embed.add_field(name='message', value=content, inline=False)
    embed.add_field(name='Flags', value=str(flags), inline=False)
    embed.add_field(name='Sender ID', value=message.author.id)
    embed.add_field(name='Channel ID', value=message.channel.id)
    embed.add_field(name='Message ID', value=message.id)
    await channel.send(embed=embed)


@client.event
async def on_ready():
    '''
    Confirms the bot is online, and has started.
    :return: N/A
    '''
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=game)


switcher = {'ping': ping, 'version': version, 'quit': quit}
blacklist = ['@everyone', 'https://', 'gift', 'nitro', 'steam', '@here', 'free']
code = 'plsdontban'     # flag escape code


@client.event
async def on_message(message):
    '''
    When a message happens, it scans the message for
    :param message: the message sent
    :return: n/a
    '''
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        if not message.author.guild_permissions.mention_everyone:
             await flag_message(message)
    content = message.content.lower()
    if content.find(code) != -1:
        pass
    else:
        count = 0
        for word in blacklist:
            index = content.find(word)
            if index != -1:
                count += 1
        if count >= 3:
            await flag_message(message, flags=count)


    if message.content.startswith(prefix):
        command = message.content[1:].lower().split(' ', 1)
        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            pass
        if command[0] == 'print':
            print(message.content)


client.run(token)
