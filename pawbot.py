import discord
import json
import modules.AntiScam as AntiScam
import modules.General as General
import modules.Moderation as Mod
import modules.ServerSettings as Settings
import modules.Verification as Verif
import random
import os
import sys
import time

from fileManagement import server_settings_path
from refManagement import ref, set_ref, add_ref
from main import eclipse_id

# Keep imports in alphabetical order

start_time = time.time()

with open(server_settings_path) as file:
    data = json.load(file)

prefix = '>'
version_num = '3.4.0'


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

game = discord.Game(f'{prefix}help for commands')
client = discord.Client(intents=intents)


async def setup(message):
    """
    sets up the bot for initial usage
    Last docstring edit: -Autumn V3.0.0
    Last method edit: -Autumn V3.2.0
    :param message:
    :return: None
    """
    await Settings.setup(message, client)


async def verify(message):
    """
    The method that primarily handles member verification. All members must verify from this method. Sends DM to user,
    asks user questions, then sends answers to the moderators in a designated chat
    Last docstring edit: -Autumn V1.14.5
    Last method edit: -Autumn V3.0.0
    :param message: Discord message calling the method
    :return: NoneType
    """
    if len(message.content) > 8:
        return
    await Verif.verify(message, client_in=client)


async def setcode(message):
    """
    Sets the server passcode.
    Last docstring edit: -Autumn V3.2.0
    Last method edit: -Autumn V3.1.2
    :param message:
    :return:
    """
    await Verif.setcode(message, message.content.split(' ', 1)[1])


async def ping(message):
    """
    Displays the time it takes for the bot to send a message upon a message being received.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V3.3.0
    :param message: Message calling the bot
    :return: None
    """
    await General.ping(message)


async def uptime(message):
    """
    Displays the time the bot has been running for.
    Last docstring edit: -Autumn V3.3.4
    Last method edit: -Autumn V3.3.4
    :param message: message calling the bot
    :return: None
    """
    days = int(time.strftime('%j', time.gmtime(time.time() - start_time)))
    await message.reply(time.strftime(f'Online for {days - 1} days %H:%M:%S\n Started <t:{int(start_time)}:R>',
                                      time.gmtime(time.time() - start_time)))


async def version(message):
    """
    Displays the version of the bot being used
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V3.3.0
    :param message: Message calling the bot
    :return: None
    """
    General.version(message, version_num)


async def end(message):
    """
    Quits the bot. Sends a message and updates the game status to alert users the bot is quiting.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V3.3.0
    :param message: Message calling the bot
    :return: None
    """
    await General.quit(message, client)


async def modmail(message):
    """
    Sends a message to the moderators. Alerts the user if an error occurs during the process
    Last docstring edit: -Autumn V1.14.4
    Last method edit: Unknown
    :param message: Message that called the bot
    :return: None
    """
    await Mod.modmail(message, client)


async def kick(message):
    """
    Method designed to kick users from the server the command originated.
    >kick [user] [reason]
    Last docstring edit: -Autumn V1.16.0
    Last method edit: -Autumn V1.16.0
    Method added: V1.16.0
    :param message:The message that called the command
    :return: None
    """
    await Mod.kick(message)


async def ban(message):
    """
    Method designed to ban users from the server the command originated. Deletes User messages from the last 24
    hours
    >ban [user] [reason]
    Last docstring edit: -Autumn V1.16.0
    Last method edit: -Autumn V3.3.0
    Method added: -Autumn V1.16.0
    :param message:The message that called the command
    :return: None
    """
    await Mod.ban(message)


async def help_message(message):
    """
    Displays the Bot's help message. Square brackets are optional arguments, angle brackets are required.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.14.8
    :param message:
    :return:
    """
    # TODO: USE A SWITCH HERE!!!
    # TODO: UPDATE FOR BEANSBOT!!!!!!!!!
    command = message.content[1:].split(' ')
    if len(command) == 1:
        embed = discord.Embed(title="Beansbot Command list",
                              description='Square brackets are optional arguments. Angle brackets are required '
                                          'arguments',
                              color=message.author.color)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        embed.set_author(name=client.user.name, icon_url=icon_url)
        
        embed.add_field(name='`' + prefix + 'help`',
                        value="That's this command!",
                        inline=False)
        embed.add_field(name=f'`{prefix}uptime`',
                        value='displays how long the bot has been active for',
                        inline=False)
        embed.add_field(name=f'`{prefix}ping`',
                        value='returns the time it takes the bot to edit a message',
                        inline=False)
        embed.add_field(name=f'`{prefix}version_num/version`',
                        value='displays the bots current version.',
                        inline=False)
        embed.add_field(name=f'`{prefix}ref [member tag/member id]`',
                        value="gets a user's ref sheet",
                        inline=False)
        embed.add_field(name='`'+prefix+'setref [ref/description]`',
                        value="Sets a user's ref. Over writes any existing refs",
                        inline=False)
        embed.add_field(name='`' + prefix + 'addref [ref/description]`',
                        value="Adds a ref to the Users's ref list",
                        inline=False)
        embed.add_field(name='`' + prefix + 'verify`',
                        value='Verifies an un verified member.',
                        inline=False)
        embed.add_field(name='`' + prefix + 'modmail`',
                        value='Sends a private message to the moderators.',
                        inline=False)
        embed.add_field(name='`' + prefix + 'huh`',
                        value='???',
                        inline=False)
        if message.guild is not None and message.author.guild_permissions.manage_roles:
            embed.add_field(name='`' + prefix + 'quit`',
                            value='quits the bot.\n Mod only.',
                            inline=False)
            embed.add_field(name=f'`{prefix}fuck`',
                            value='Emergency stops the bot in the event of catastrophic failure',
                            inline=False)
            embed.add_field(name=f'`{prefix}warn <User> <reason>`',
                            value='warns a user for the given reason',
                            inline=False)
            embed.add_field(name=f'`{prefix}listwarns <User>`',
                            value='Lists the given users warns',
                            inline=False)
            embed.add_field(name=f'`{prefix}removewarn <user> <warn number to remove>`',
                            value='removes a given users warn',
                            inline=False)
            embed.add_field(name=f'`{prefix}kick <user> [reason]`',
                            value='Kicks a user from the server, with the given reason',
                            inline=False)
            embed.add_field(name=f'`{prefix}ban <user> [reason]`',
                            value='Bans a user from the server with the given reason',
                            inline=False)
            embed.add_field(name=f'`{prefix}setcode <new code>`',
                            value='Sets the server passcode to the new code',
                            inline=False)
            embed.add_field(name=f'`{prefix}setup`',
                            value='Sets the bot up for normal use',
                            inline=False)
            '''embed.add_field(name=f'`{prefix}`',
                            value='',
                            inline=False)'''
        await message.channel.send(embed=embed)
    elif command[1] == 'help':
        help_embed = discord.Embed(title="Beansbot Command list",
                                   color=message.author.color)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        help_embed.set_author(name=client.user.name, icon_url=icon_url)
        help_embed.add_field(name='`' + prefix + 'help [bot command]`', value="That's this command!", inline=False)
        await message.channel.send(embed=help_embed)
    elif command[1] == 'warn' and message.guild is not None and message.author.guild_permissions.manage_roles:
            warn_embed = discord.Embed(title=f'Beansbot `{prefix}warn` Command',
                                       description='>warn <user> <reason>',
                                       color=message.author.color)
            warn_embed.add_field(name='User',
                            value='The user to be warned, Use their Name, discord ID or tag them.',
                            inline=False)
            warn_embed.add_field(name='reason',
                            value='the reason for the warn that will be logged',
                            inline=False)
            await message.reply(embed=warn_embed)
    elif command[1] == 'listwarns' and message.guild is not None and message.author.guild_permissions.manage_roles:
        list_embed = discord.Embed(title=f'Beansbot `{prefix}listwarns` Command',
                                   description='>listwarns <user>',
                                   color=message.author.color)
        list_embed.add_field(name='User',
                             value='The user to search for')
        await message.reply(embed=list_embed)
    elif command[1] == 'removewarn' and message.guild is not None and message.author.guild_permissions.manage_roles:
        remove_embed = discord.Embed(title=f'Beansbot `{prefix}removewarn` Command',
                                     description=f'{prefix}removewarn <user> <warn number>',
                                     color=message.author.color)
        remove_embed.add_field(name='User',
                               value='User who you want to remove a warn from',
                               inline=False)
        remove_embed.add_field(name='Warn number',
                               value='Which warn to remove from the user',
                               inline=False)
        await message.reply(embed=remove_embed)
    elif command[1] == 'kick' and (message.guild is not None and message.author.guild_permissions.kick_members):
        kick_embed = discord.Embed(title=f'Beansbot `{prefix}kick` Command',
                                   description=f'{prefix}kick <user> [reason]',
                                   color=message.author.color)
        kick_embed.add_field(name='User',
                             value='the user to kick',
                             inline=False)
        kick_embed.add_field(name='Reason (optional)',
                             value='The reason for the kick. This will show up in the audit log',
                             inline=False)
        await message.reply(embed=kick_embed)
    elif command[1] == 'ban' and (message.guild is not None and message.author.guild_permissions.ban_members):
        kick_embed = discord.Embed(title=f'Beansbot `{prefix}ban` Command',
                                   description=f'{prefix}ban <user> [reason]',
                                   color=message.author.color)
        kick_embed.add_field(name='User',
                             value='the user to ban',
                             inline=False)
        kick_embed.add_field(name='Reason (optional)',
                             value='The reason for the ban. This will show up in the audit log',
                             inline=False)
        await message.reply(embed=kick_embed)
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
        

async def huh(message):
    """
    Easter egg
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V 3.4.0
    :param message:
    :return: None
    """
    await message.reply("We're no Strangers to love\n"
                        "You know the rules and so do I!~\n"
                        "A full commitments what I'm thinkin' of\n"
                        "You wouldn't get this from, Any other guy.\n"
                        "\n"
                        "I just wanna tell you how I'm feeling\n"
                        "gotta make you, understand!\n"
                        "\n"
                        "Never gonna give you up, Never gonna let you down\n"
                        "Never gonna run around, and desert you\n"
                        "Never gonna make you cry, Never gonna say goodbye\n"
                        "Never gonna tell a lie, and hurt you")


async def nsfw_ref(message):
    await ref(message, nsfw=True)


async def nsfw_add_ref(message):
    await add_ref(message, nsfw=True)


async def nsfw_set_ref(message):
    await set_ref(message, nsfw=True)


@client.event
async def on_ready():
    """
    Method called when the bot boots and is fully online
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.16.3
    :return: None
    """
    
    print('We have logged in as {0.user}'.format(client))
    
    await client.change_presence(activity=game)
    await client.get_user(eclipse_id).send('Running, and active')


switcher = {'help': help_message, 'ping': ping, 'version_num': version, 'version': version, 'verify': verify,
            'setcode': setcode, 'modmail': modmail, 'quit': end, 'fuck': sys.exit, 'huh': huh, 'kick': kick,
            'ban': ban, 'setup': setup, 'uptime': uptime, 'warn': Mod.warn, 'listwarns': Mod.show_warns,
            'removewarn': Mod.remove_warn, 'ref': nsfw_ref, 'setref': nsfw_set_ref, 'addref': nsfw_add_ref}

scan_ignore = [1054172309147095130]


@client.event
async def on_message(message):
    """
    The primary method called. This method determines what was called, and calls the appropriate message, as well as
    handling all message scanning. This is called every time a message the bot can see is sent.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V3.3.0
    :param message:
    :return: None
    """
    if message.author.bot:
        return
    
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        if not message.author.guild_permissions.mention_everyone:
            await AntiScam.scan_message(message)
    content = message.content.lower()
    
    if message.guild is None or content.find(AntiScam.code) != -1 or message.channel.id in scan_ignore:
        pass
    else:
        await AntiScam.scan_message(message)
    try:
        if content[0] == prefix:
            
            # split the message to determine what command is being called
            command = message.content[1:].lower().split(' ', 1)
            
            # search the switcher for the command called. If the command is not found, do nothing
            try:
                method = switcher[command[0]]
            except KeyError:
                return
            
            await method(message)
            if command[0] == 'print':
                # Used to transfer data from Discord directly to the command line. Very simple shortcut
                print(message.content)
    except IndexError:
        pass


@client.event
async def on_member_update(before, after):
    if (before.guild.id == 1054121991365468281 and
            before.guild.get_role(1054160602349703188) not in before.roles and
            before.guild.get_role(1054160602349703188) in after.roles):
        welcome = [f"<@{after.id}> is our newest bean lover",
                   f"<@{after.id}> has stumbled into the bean sanctuary",
                   f"<@{after.id}> has arrived looking for beans"]

        await before.guild.get_channel(1054137434725691393).send(content=f"~ {random.choice(welcome)}. Please "
                                                                         f"remember to stop by <#1054672645527969802> for your roles.")


def run_pawbot():
    """
    Function allows the host to pick whether to run the live bot, or run the test bot in a closed environment, without
    switching programs. This allows the live code to run parallel to the testing code and prevent constant restarts to
    test new features.
    Last docstring edit: -Autumn V1.16.3
    Last function edit: Unknown
    :return: None
    """
    global prefix
    
    if len(sys.argv) > 1:
        inp = int(sys.argv[1])
    else:
        inp = int(input('input token num\n'
                        '1. Pawbot\n'
                        '2. Testing Environment\n'))
    
    if inp == 1:
        # Main bot client. Do not use for tests
        
        client.run(os.environ.get('PAWBOT_TOKEN'))  # must say client.run(os.environ.get('SUNREEK_TOKEN'))
    
    elif inp == 2:
        # Test Bot client. Allows for tests to be run in a secure environment.
        
        client.run(os.environ.get('TESTBOT_TOKEN'))  # must say client.run(os.environ.get('TESTBOT_TOKEN'))


if __name__ == '__main__':
    run_pawbot()
