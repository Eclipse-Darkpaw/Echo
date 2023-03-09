"""
Refbot main code. Several functions are imported
"""
import time
import discord
import os
import sys

import main
import modules.General as General

# custom imports from other files
from profile import display_profile, set_bio, edit_field, add_field, delete_field
from refManagement import ref, set_ref, add_ref, oc, random_ref
from main import eclipse_id

prefix = '>'
version_num = '3.3.0'

eclipse_id = main.eclipse_id
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

game = discord.Game(prefix + "help for commands")
client = discord.Client(intents=intents)

guild = None


async def ping(message):
    """
    Times how long it takes the bot to edit a message
    Last docstring edit: -Autumn | V2.1.0
    Last function edit: -Autumn | V3.3.0
    :param message:
    :return:
    """
    await General.ping(message)


async def version(message):
    """
    Displays the current file version number
    Last docstring edit: -Autumn | V2.1.0
    Last function edit: -Autumn | V3.3.0
    :param message:
    :return:
    """
    await General.version(message, version_num)


async def end(message):
    """
    Quits the bot.requires admin perms
    Last docstring edit: -Autumn | V2.1.0
    Last function edit: -Autumn | V3.3.0
    :param message:
    :return:
    """
    await General.quit(message, client)


async def help_message(message):
    """
    Displays the help embed
    Last docstring edit: -Autumn | V2.1.0
    Last function edit: -Autumn | V2.1.2
    :param message:
    :return:
    """
    # square brackets are optional arguments, angle brackets are required
    command = message.content[1:].split(' ')
    if len(command) == 1:
        embed = discord.Embed(title="Refbot Command list",
                              color=0x45FFFF)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        embed.set_author(name=client.user.name,
                         icon_url=icon_url)

        embed.add_field(name='Prefix',
                        value=prefix,
                        inline=False)
        embed.add_field(name='`'+prefix+'help`',
                        value="That's this command!",
                        inline=False)
        embed.add_field(name='`'+prefix+'version_num`',
                        value='What version the bot is currently on',
                        inline=False)
        embed.add_field(name='`'+prefix+'profile [member tag/member id]/[edit]`',
                        value="Gets a tagged user's profile or your profile",
                        inline=False)
        embed.add_field(name='`'+prefix+'ref [member tag/member id]`',
                        value="gets a user's ref sheet",
                        inline=False)
        embed.add_field(name='`'+prefix+'setref [ref/description]`',
                        value="Sets a user's ref. Over writes any existing refs",
                        inline=False)
        embed.add_field(name='`' + prefix + 'addref [ref/description]`',
                        value="Adds a ref to the Users's ref list",
                        inline=False)
        embed.add_field(name='`' + prefix + 'OC []`',
                        value="manages and views a users OCs (not including the ones in ",
                        inline=False)
        embed.add_field(name='`' + prefix + 'rr/randomref/random_ref`',
                        value='Gets a random users ref sheet. Alias for `' + prefix + 'ref random`',
                        inline=False)
        embed.add_field(name='Moderator Commands',
                        value='Commands that only mods can use',
                        inline=False)
        embed.add_field(name='`'+prefix+'quit`',
                        value='quits the bot',
                        inline=False)

        await message.channel.send(embed=embed)
    elif command[1] == 'help':
        help_embed = discord.Embed(title="help Command list",
                                   color=0x45FFFF)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        help_embed.set_author(name=client.user.name,
                              icon_url=icon_url)

        help_embed.add_field(name='`' + prefix + 'help [bot command]`',
                             value="That's this command!",
                             inline=False)

        await message.channel.send(embed=help_embed)
    elif command[1] == 'profile':
        profile_embed = discord.Embed(title='Profile Command list',
                                      description='Displays a users profile',
                                      color=0x45FFFF)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        profile_embed.set_author(name=client.user.name,
                                 icon_url=icon_url)

        profile_embed.add_field(name='No argument',
                                value='Displays your profile',
                                inline=False)
        profile_embed.add_field(name='`User ID/Tagged User/Nickname`',
                                value='Searches for a user\'s profile. Tagging the desired user, or using their member '
                                      'ID yeilds the most accurate results.',
                                inline=False)
        profile_embed.add_field(name='`edit <string>`',
                                value='Changes your profile to say what you want. Only emotes from this server can be'
                                      ' used.',
                                inline=False)

        await message.channel.send(embed=profile_embed)
    elif command[1] == 'ref':
        ref_embed = discord.Embed(title='`'+prefix+'ref` Command List',
                                  description='Displays a users primary ref.',
                                  color=0x45FFFF)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        ref_embed.set_author(name=client.user.name,
                             icon_url=icon_url)

        ref_embed.add_field(name='No argument',
                            value='Displays your ref',
                            inline=False)
        ref_embed.add_field(name='`User ID/Tagged User/Nickname`',
                            value='Searches for a user\'s profile. Tagging the desired user, or using their member ID '
                                  'yeilds the most accurate results.',
                            inline=False)
        ref_embed.add_field(name='`set <string/ref>`',
                            value='Changes your ref to say what you want. Only emotes from this server can be used.',
                            inline=False)
        ref_embed.add_field(name='`random [all]`',
                            value="Retrieves a random user's ref sheet. Is limited to members in the guild the message "
                                  "comes from, unless you add `all` to the end of the command or run the command in "
                                  "DMs",
                            inline=False)
        
        await message.channel.send(embed=ref_embed)
    elif command[1] == 'OC':
        embed = discord.Embed(title='`' + prefix + 'OC` Command List',
                              description='Manages a users OC\'s ref.',
                              color=0x45FFFF)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        embed.set_author(name=client.user.name,
                         icon_url=icon_url)

        embed.add_field(name='add [OC name] [description/attachment]',
                        value='Adds a new OC',
                        inline=False)
        embed.add_field(name='edit [OC name] [description/attachment]',
                        value='Edits an existing OC',
                        inline=False)
        embed.add_field(name='show [OC owner ID/tagged] [OC name]',
                        value='Shows an OC',
                        inline=False)
        embed.add_field(name='tree [OC owner ID/tagged]',
                        value='Shows a users OCs',
                        inline=False)

        await message.channel.send(embed=embed)


async def num_servers(message):
    """
    Returns the number of servers the bot is in
    :param message:
    :return:
    """
    await message.reply(str(len(client.guilds)))


async def list_servers(message):
    """
    Prints the list of servers the bot is in
    :param message:
    :return:
    """
    servers = '**__Server List__**\n'
    for guild in client.guilds:
        servers += '`' + str(guild.id) + '` - ' + guild.name + '\n'
    await message.reply(servers)


async def profile(message):
    """
    Displays a users profile
    Last docstring edit: -Autumn | V2.1.0
    Last function edit: -Autumn | Unknown Version
    :param message: message calling the bot
    :return: None
    """
    command = message.content.split(' ', 2)
    if len(command) == 1:
        await display_profile(message, client)
    elif command[1] == 'edit':
        try:
            set_bio(message.author, command[2])
            await message.channel.send('Bio set')
        except KeyError:
            await message.channel.send('Error. Bio not set, please use ASCII characters and custom emotes.')
    elif command[1] == 'field':
        command = message.content.split(' ', 3)
        if command[2] == 'add':
            await add_field(message, client)
        elif command[2] == 'edit':
            await edit_field(message)
        elif command[2] == 'delete':
            await delete_field(message)
        else:
            await message.channel.send()
    else:
        await display_profile(message, client)


@client.event
async def on_ready():
    """
    Function called when the bot connects to discord and is ready.
    Last docstring edit: -Autumn | V2.1.0
    Last function edit: -Autumn | Unknown Version
    :return:
    """
    global guild

    print('We have logged in as {0.user}'.format(client))

    await client.change_presence(activity=game)
    await client.get_user(eclipse_id).send('Running, and active')


switcher = {'help': help_message, 'ping': ping, 'version_num': version, 'quit': end, 'profile': profile, 'ref': ref,
            'setref': set_ref, 'addref': add_ref, 'oc': oc, 'random_ref': random_ref,
            'randomref': random_ref, 'rr': random_ref, 'num_servers': num_servers, 'list_servers': list_servers}


@client.event
async def on_message(message):
    """
    Function called by the bot whenever a message is recieved in a server or DMs.
    Last docstring edit: -Autumn | V2.1.0
    Last function edit: -Autumn | Unknown Version
    :param message: message object recieved
    :return: None
    """
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
    """
    Allows the bot to run, and enables the bot to use a test environment instead on start
    Last docstring edit: -Autumn | V2.1.0
    Last function edit: -Autumn | Unknown Version
    :return: None
    """

    tokens = ['REFBOT_TOKEN', 'TESTBOT_TOKEN', 'TOKEN']
    if len(sys.argv) > 1:
        inp = int(sys.argv[1]) - 1
    else:
        inp = int(input('Input a bot num\n1. refbot\n2. testbot\n')) - 1
        
    client.run(os.environ.get(tokens[inp]))

if __name__ == '__main__':
    run_refbot()
