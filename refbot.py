import time
import discord
import os
import sys
from profile import display_profile, set_bio
from refManagement import ref, set_ref, add_ref, oc


prefix = '>'
version_num = '2.0.0'

eclipse_id = 440232487738671124

intents = discord.Intents.default()
intents.members = True

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


def get_user_id(message):
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


async def ping(message):
    start = time.time()
    x = await message.channel.send('Pong!')
    ping_time = time.time() - start
    edit = x.content + ' ' + str(int(ping_time * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message):
    await message.channel.send('I am currently running version ' + version_num)


async def quit(message):
    global game
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def restart(message):
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        os.execl(sys.executable,__file__,'main.py')
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def help(message):
    # square brackets are optional arguments, angle brackets are required
    command = message.content[1:].split(' ')
    if len(command) == 1:
        embed = discord.Embed(title="Refbot Command list", color=0x45FFFF)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
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
        embed.add_field(name='`' + prefix + 'OC []`', value="manages and views a users OCs (not including the ones in ",
                        inline=False)
        embed.add_field(name='Moderator Commands', value='Commands that only mods can use', inline=False)
        embed.add_field(name='`'+prefix+'quit`', value='quits the bot', inline=False)
        await message.channel.send(embed=embed)
    elif command[1] == 'help':
        help_embed = discord.Embed(title="help Command list", color=0x45FFFF)
        help_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        help_embed.add_field(name='`' + prefix + 'help [bot command]`', value="That's this command!", inline=False)
        await message.channel.send(embed=help_embed)
    elif command[1] == 'profile':
        profile_embed = discord.Embed(title='Profile Command list', description='Displays a users profile', color=0x45FFFF)
        profile_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        profile_embed.add_field(name='No argument', value='Displays your profile', inline=False)
        profile_embed.add_field(name='`User ID/Tagged User/Nickname`', value='Searches for a user\'s profile. Tagging the desired user, or using their member ID yeilds the most accurate results.', inline=False)
        profile_embed.add_field(name='`edit <string>`', value='Changes your profile to say what you want. Only emotes from this server can be used.', inline=False)
        await message.channel.send(embed=profile_embed)
    elif command[1] == 'ref':
        ref_embed = discord.Embed(title='`'+prefix+'ref` Command List', description='Displays a users primary ref.', color=0x45FFFF)
        ref_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        ref_embed.add_field(name='No argument', value='Displays your ref', inline=False)
        ref_embed.add_field(name='`User ID/Tagged User/Nickname`', value='Searches for a user\'s profile. Tagging the desired user, or using their member ID yeilds the most accurate results.', inline=False)
        ref_embed.add_field(name='`set <string/ref>`', value='Changes your ref to say what you want. Only emotes from this server can be used.', inline=False)
        await message.channel.send(embed=ref_embed)
    elif command[1] == 'OC':
        embed = discord.Embed(title='`' + prefix + 'OC` Command List', description='Manages a users OC\'s ref.',
                                  color=0x45FFFF)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        embed.add_field(name='add [OC name] [description/attachment]', value='Adds a new OC', inline=False)
        embed.add_field(name='edit [OC name] [description/attachment]', value='Edits an existing OC', inline=False)
        embed.add_field(name='show [OC owner ID/tagged] [OC name]', value='Shows an OC', inline=False)
        embed.add_field(name='tree [OC owner ID/tagged]', value='Shows a users OCs', inline=False)
        await message.channel.send(embed=embed)


async def profile(message):
    command = message.content.split(' ', 2)
    if len(command) == 1:
        await display_profile(message)
    elif command[1] == 'edit':
        try:
            set_bio(message.author, command[2])
            await message.channel.send('Bio set')
        except ValueError:
            await message.channel.send('Error. Bio not set, please use ASCII characters and custom emotes.')
    else:
        await display_profile(message)


async def repeat(message):
    commands = message.content.split(' ', 2)
    iter = int(commands[1])
    text = commands[2]

    for i in range(iter):
        await message.channel.send(text + str(i+1))


@client.event
async def on_ready():
    global guild

    print('We have logged in as {0.user}'.format(client))

    guild = client.get_guild(840181552016261170)
    await client.change_presence(activity=game)
    await guild.get_member(eclipse_id).send('Running, and active')


switcher = {'help': help, 'ping': ping, 'version_num': version, 'quit': quit, 'profile': profile, 'restart': restart,
            'setref': set_ref, 'ref': ref, 'addref': add_ref, 'oc': oc, 'repeat':repeat}


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        pass
    if message.content.startswith(prefix):
        command = message.content[1:].lower().split(' ', 1)
        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            pass
        if command[0] == 'print':
            print(message.content)


def run_refbot():
    inp = int(input('Input a bot num\n1. refbot\n'))
    if inp == 1:
        client.run('ODQyMTk0NDA0NDk2NTA2OTcy.YJxwqQ.M2hEOsoiBbEYcC_kRz4iXWoBoY4')

    pass


if __name__ == '__main__':
    run_refbot()
