import time
import discord
import os
import sys

# from profile import profile
from refManagement import ref, set_ref, add_ref


prefix = '>'
version_num = '2.0.0'


eclipse_id = 749443249302929479

intents = discord.Intents.default()
intents.members = True

game = discord.Game(prefix + "help for commands")
client = discord.Client(intents=intents)

tree = discord.app_commands.CommandTree(client)

guild = None


@tree.command(name="ping", description="Checks the bot's ping", guild=discord.Object(id=791392423704133653))
async def ping(interaction):
    start = time.time()
    x = await interaction.response.send_message('Pong!')
    ping = time.time() - start
    edit = 'Pong! ' + str(int(ping * 1000)) + 'ms'
    await interaction.response.edit_message(content=edit)


@tree.command(name="version", description='Displays the current version', guild=discord.Object(id=791392423704133653))
async def version(interaction):
    await interaction.response.send_message('I am currently running version ' + version_num)


@tree.command(name='verify', description='Applys for membership in the server', guild=discord.Object(id=791392423704133653), eph)
async def verify(interaction, password: str):
    if password == 'password':
        await interaction


async def quit(message):
    global game
    if message.author.id == eclipse_id or message.author.guild_permissions.administrator:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def help(message):
    embed = discord.Embed(title="Echo Command list", color=0x45FFFF)
    embed.add_field(name='Prefix', value=prefix, inline=False)
    embed.add_field(name='`'+prefix+'help`', value="That's this command!", inline=False)
    embed.add_field(name='`'+prefix+'version_num`', value='What version the bot is currently on', inline=False)
    embed.add_field(name='`'+prefix+'profile [member tag/member id]/[edit]`',
                    value="Gets a tagged user's profile or your profile", inline=False)
    embed.add_field(name='`'+prefix+'ref [member tag/member id]`', value="gets a user's ref sheet", inline=False)
    embed.add_field(name='`'+prefix+'setref [ref/description]`',
                    value="Sets a user's ref. Over writes any existing refs", inline=False)
    embed.add_field(name='`' + prefix + 'addref [ref/description]`', value="Adds a ref to the Users's ref list",
                    inline=False)

    embed.add_field(name='Moderator Commands', value='Commands that only mods can use', inline=False)
    embed.add_field(name='`'+prefix+'quit`', value='quits the bot', inline=False)
    await message.channel.send(embed=embed)


@tree.command(name="setup", description="begins setup of the bot.", guild=discord.Object(id=791392423704133653))
async def setup(interaction, ):
    pass


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=791392423704133653))

    print('We have logged in as {0.user}'.format(client))

    await client.change_presence(activity=game)
    await guild.get_member(eclipse_id).send('Running, and active')


switcher = {'help': help, 'ping': ping, 'setref': set_ref,
            'ref': ref, 'addref': add_ref, 'quit': quit}


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        pass
    if message.content.startswith(prefix):
        command = message.content[1:].split(' ', 1)
        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            pass
        if command[0] == 'print':
            print(message.content)
    # most_active.score(message)


client.run(os.environ.get('TESTBOT_TOKEN'))
