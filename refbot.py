import time
import discord
import os
import sys
from dotenv import load_dotenv
from profile import display_profile, set_bio
from fileManagement import joinleave_path, profile_path
from refManagement import ref, set_ref, add_ref

load_dotenv()


prefix = '>'
cmdlog = 'command.log'  # ???: why is this a thing? it just takes up space on the HDD. Remove to save several KB
version_num = '1.8.2'


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


def log(message):
    to_log = '[' + str(message.created_at) + 'Z] ' + str(message.guild.id) + \
             '\n' + message.content + '\n' + \
             'channel ID:' + str(message.channel.id) + ' Author ID:' + str(message.author.id) + '\n\n'
    with open(cmdlog, 'a') as file:
        file.write(to_log)


async def ping(message):
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit       )


async def version(message):
    await message.channel.send('I am currently running version ' + version_num)


async def quit(message):
    global game
    # await save (message)
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

# TODO: update to be refbot specific
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
        embed.add_field(name='Moderator Commands', value='Commands that only mods can use', inline=False)
        embed.add_field(name='`'+prefix+'quit`', value='quits the bot', inline=False)
        await message.channel.send(embed=embed)
    elif command[1] == 'help':
        help_embed = discord.Embed(title="SunReek Command list", color=0x45FFFF)
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
        await message.channel.send(embed=profile_embed)


# FIXME: Allow users to search for other users profiles. Feature is not working properly
# TODO: update to handle emojis properly
async def profile(message):
    command = message.content[1:].split(' ', 2)
    if len(command) == 1:
        await display_profile(message)
    elif command[1] == 'edit':
        try:
            set_bio(str(message.author.id), command[2])
            await message.channel.send('Bio set')
        except ValueError:
            await message.channel.send('Error. Bio not set, please use ASCII characters and custom emotes.')
    else:
        await display_profile(message)

@client.event
async def on_ready():
    global guild

    print('We have logged in as {0.user}'.format(client))

    guild = client.get_guild(840181552016261170)
    await client.change_presence(activity=game)
    await guild.get_member(eclipse_id).send('Running, and active')


switcher = {'help': help, 'ping': ping, 'version_num': version, 'quit': quit, 'profile': profile, 'restart': restart,
            'setref': set_ref, 'ref': ref, 'addref': add_ref}


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


token = os.getenv('REFBOT')
client.run(token)
'''RNG base on a string a human creates then converts each word into an int by using its position on the list of words.
add each int and mod '''