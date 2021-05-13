import time
import discord
import os
import sys
from dotenv import load_dotenv
from profile import display_profile, set_bio
from fileManagement import joinleave_path, profile_path
from refManagement import ref, set_ref
load_dotenv()


prefix = '>'
cmdlog = 'command.log'
version_num = '1.5.1'


eclipse_id = 440232487738671124
game = discord.Game(prefix + "help for commands")
client = discord.Client(intents=intents)
guild = None


async def read_line(channel, prompt, target, delete_prompt=True, delete_response=True):
    show = await channel.send(prompt)

    def check(msg):
        return msg.author != client.user and (msg.author == target or msg.channel == channel)

    msg = await client.wait_for('message', check=check)

    if delete_response:
        try:
            await msg.delete()
        finally:
            pass
    if delete_prompt:
        await show.delete()

    return msg


def get_user_id(message, id):
    command = message.content.split()
    if len(command) == 1:
        return message.author.id
    elif len(command[1]) == 18:
        return int(command[1])
    elif len(command[1]) == 21:
        return int(command[2:-2])
    elif len(command[1]) == 22:
        return int(command[3:-2])
    raise discord.InvalidArgument('Not a valid user!')


def log(message):
    to_log = '[' + str(message.created_at) + 'Z] ' + str(message.guild) + \
             '\n' + message.content + '\n' + \
             'channel ID:' + str(message.channel.id) + ' Author ID:' + str(message.author.id) + '\n\n'
    with open(cmdlog, 'a') as file:
        file.write(to_log)


async def ping(message):
    log(message)
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message):
    log(message)
    await message.channel.send('I am currently running version ' + version_num)


async def quit(message):
    global game
    log(message)
    # await save(message)
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def restart(message):
    log(message)
    # await save(message)
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        os.execl(sys.executable,__file__,'main.py')
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def help(message):
    embed = discord.Embed(title="Refbot Command list", color=0x45FFFF)
    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embed.add_field(name='Prefix', value=prefix, inline=False)
    embed.add_field(name='`'+prefix+'help`', value="That's this command!", inline=False)
    embed.add_field(name='`'+prefix+'version_num`', value='What version the bot is currently on', inline=False)
    embed.add_field(name='`'+prefix+'profile [member tag/member id]/[edit]`',
                    value="Gets a tagged user's profile or your profile", inline=False)
    embed.add_field(name='`'+prefix+'ref [member tag/member id]`', value="gets a user's ref sheet", inline=False)
    embed.add_field(name='`'+prefix+'set_ref`', value="Sets a user's ref", inline=False)

    embed.add_field(name='Moderator Commands', value='Commands that only mods can use', inline=False)
    embed.add_field(name='`'+prefix+'quit`', value='quits the bot', inline=False)
    await message.channel.send(embed=embed)


async def profile(message):
    command = message.content[1:].split(' ', 2)
    if len(command) == 1:
        await display_profile(message)
    elif command[1] == 'edit':
        set_bio(str(message.author.id), command[2])
        await message.channel.send('Bio set')
    else:
        if len(command[1]) == 18:
            target = message.guild.get_member(int(command[1]))
        else:
            target = message.mentions[0]
        await display_profile(message, target)


@client.event
async def on_ready():
    global guild

    print('We have logged in as {0.user}'.format(client))

    guild = client.guilds[0]
    await client.change_presence(activity=game)
    await guild.get_member(eclipse_id).send('Running, and active')


switcher = {'help': help, 'ping': ping, 'version_num': version,
            'quit': quit, 'profile': profile, 'restart': restart, 'setref': set_ref, 'ref': ref}


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

'''
@client.event
async def on_member_join(member):
    file = open(joinleave_path(member), 'a')
    file.write('->' + str(member.name))
    await member.send('Hello, and welcome to the server! Please read over the rules before verifying yourself!')
    embed = discord.Embed(title='Member Join')
    embed.set_author(name=member.name, icon_url=member.avatar_url)
    embed.add_field(name='Created at', value=member.created_at)
    embed.set_footer(text=str(member.id))
    await join_leave_log.send(embed=embed)


@client.event
async def on_member_remove(member):
    with open(profile_path(member.id)) as file:
        pass
    print(str(member) + ' left the server')
    file = open('Echo/member_leave.log', 'a')
    to_log = str(member.id) + ', ['
    roles = member.roles
    for i in range(len(roles)):
        if i == 0:
            to_log += str(member.guild.id)
        else:
            to_log += str(roles[i].id)
        if i < (len(roles) - 1):
            to_log += ', '
    to_log += ']\n'
    file.write(to_log)
    file.close()
    print(to_log)
    role_tags = ''
    for i in range(len(roles)):
        if i == 0:
            pass
        else:
            role_tags += '<@&' + str(roles[i].id) + '>'
    footer = 'ID:' + str(member.id)
    # •
    leave = discord.Embed(title='Member Leave')
    leave.set_author(name=member.name, icon_url=member.avatar_url)
    if len(role_tags) == 0:
        role_tags = 'None'
    leave.add_field(name='Roles', value=role_tags)
    leave.set_footer(text=footer)
    await join_leave_log.send(embed=leave)
'''

token = os.getenv('REFBOT')
client.run(token)
'''RNG base on a string a human creates then converts each word into an int by using its position on the list of words.
add each int and mod '''