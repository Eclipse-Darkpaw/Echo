import discord

version_num = '1.1.0'

prefix = 'as!'
log_channel = 933539437357432892     #channel ID of the channel where logs go
token = 'OTMzNTQwOTg1NjY3OTkzNjcx.YejByw.dISKG7JJOBC2L3BAIPmqEpHHJMQ'          # put the bot token in the quotes

game = discord.Game('Scanning for pings')
client = discord.Client()


async def ping(message):
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message):
    await message.channel.send('I am currently running version ' + version_num)


async def quit(message):
    global game
    if message.author.guild_permissions.administrator:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=game)
    await guild.get_member(440232487738671124).send('Running, and active')


switcher = {'ping': ping, 'version': version, 'quit': quit}


@client.event
async def on_message(message):
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        if message.author.guild_permissions.mention_everyone:
            pass
        else:
            await message.delete()
            content = message.content.replace('@', '@ ')

            channel = message.guild.get_channel(log_channel)

            embed = discord.Embed(title='Attempted ping in <#' + str(message.channel.id) + '>')
            embed.set_author(name='<@' + str(message.author.id) + '>', icon_url=message.author.avatar_url)
            embed.add_field(name=message, value=content)
            await channel.send(embed=embed)
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
