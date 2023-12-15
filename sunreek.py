import discord
import json
import main
import modules.AntiScam as AntiScam
import modules.Artfight as Artfight
import modules.General as General
import modules.Moderation as Mod
import modules.ServerSettings as Settings
import modules.Verification as Verif
import os
import sys
import time

from fileManagement import resource_file_path
#from profile import display_profile, set_bio
from modules.refManagement import ref, set_ref, add_ref, oc, random_ref
# Keep imports in alphabetical order

start_time = time.time()

with open(resource_file_path + 'servers.json') as file:
    data = json.load(file)

prefix = '}'
version_num = '3.4.2'

eclipse_id = main.eclipse_id

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

game = discord.Game(f'with some tests')
client = discord.Client(intents=intents)

artfight_enabled = False


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
    await message.reply(time.strftime(f'Online for {days-1} days %H:%M:%S\n Started <t:{int(start_time)}:R>',
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
    command = message.content[1:].split(' ')
    if len(command) == 1:
        embed = discord.Embed(title="SunReek Command list",
                              description='Square brackets are optional arguments. Angle brackets are required '
                                          'arguments',
                              color=0x45FFFF)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        embed.set_author(name=client.user.name, icon_url=icon_url)

        embed.add_field(name='`'+prefix+'help`',
                        value="That's this command!",
                        inline=False)
        embed.add_field(name='`'+prefix+'verify`',
                        value='Verifies an un verified member.',
                        inline=False)
        embed.add_field(name='`'+prefix+'modmail`',
                        value='Sends a private message to the moderators.',
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
        embed.add_field(name='`'+prefix+'setref <attachment>`',
                        value="Sets a user's ref. Overwrites all current ref data",
                        inline=False)
        embed.add_field(name='`'+prefix+'addref <attachment>`',
                        value="Adds another ref to your file.",
                        inline=False)
        embed.add_field(name='`'+prefix+'crsdky [arguments]`',
                        value='commands for the CursedKeys game. will show the list of cursed keys if argument is left '
                              'off',
                        inline=False)
        embed.add_field(name='`'+prefix+'OC`',
                        value="Manages a users OCs",
                        inline=False)
        embed.add_field(name='`'+prefix+'quit`',
                        value='quits the bot.\n Mod only.',
                        inline=False)
        embed.add_field(name='`' + prefix + 'join_pos [target ID]`',
                        value='Shows the position a member joined in. shows message author if target is left blank',
                        inline=False)
        embed.add_field(name='`' + prefix + 'artfight`',
                        value='Commands for the annual artfight',
                        inline=False)
        embed.add_field(name='`' + prefix + 'huh`',
                        value='???',
                        inline=False)
        embed.add_field(name='`' + prefix + 'random_ref`',
                        value='Same as `' + prefix + 'ref random`',
                        inline='False')
        await message.channel.send(embed=embed)
    elif command[1] == 'help':
        help_embed = discord.Embed(title="SunReek Command list", color=0x45FFFF)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        help_embed.set_author(name=client.user.name, icon_url=icon_url)
        help_embed.add_field(name='`' + prefix + 'help [bot command]`', value="That's this command!", inline=False)
        await message.channel.send(embed=help_embed)
    elif command[1] == 'profile':
        profile_embed = discord.Embed(title='Profile Command list',
                                      description='Displays a users profile',
                                      color=0x45FFFF)

        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        profile_embed.set_author(name=client.user.name, icon_url=icon_url)

        profile_embed.add_field(name='No argument',
                                value='Displays your profile',
                                inline=False)
        profile_embed.add_field(name='`User ID/Tagged User/Nickname`',
                                value='Searches for a user\'s profile. Tagging the desired user, or using their member '
                                      'ID yields the most accurate results.',
                                inline=False)
        profile_embed.add_field(name='`edit <string>`',
                                value='Changes your profile to say what you want. Only emotes from this server can be '
                                      'used.',
                                inline=False)
        await message.channel.send(embed=profile_embed)
    elif command[1] == 'crsdky':
        crsdky_embed = discord.Embed(title="`}crsdky Command list", color=0x45FFFF)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        crsdky_embed.set_author(name=client.user.name, icon_url=icon_url)

        crsdky_embed.add_field(name='Notes',
                               value='Used by going `}crsdky [argument]`, ',
                               inline=False)
        crsdky_embed.add_field(name='`rules` or no argument',
                               value='Give an overview of the game Cursd Ky',
                               inline=False)
        crsdky_embed.add_field(name='`list`',
                               value='lists the current cursed keys',
                               inline=False)
        crsdky_embed.add_field(name='`join`',
                               value='Joins the game of crsdky. Users cannot join after the game starts.',
                               inline=False)
        crsdky_embed.add_field(name='`leave`',
                               value='leaves the game of crsdky',
                               inline=False)
        crsdky_embed.add_field(name='`numleft`',
                               value='Shows the number of players left.',
                               inline=False)
        await message.channel.send(embed=crsdky_embed)
        if message.author.guild_permissions.manage_roles:
            mod_crsdky_embed = discord.Embed(title='`}crsdky` Mod Commands', color=message.author.color)
            mod_crsdky_embed.add_field(name='Notes',
                                       value='All these commands require the user to have moderator permissions.',
                                       inline=False)
            mod_crsdky_embed.add_field(name='`set <char list>`',
                                       value='Sets the cursed keys. Takes lowercase letters and symbols.',
                                       inline=False)
            mod_crsdky_embed.add_field(name='`start`',
                                       value='Starts the round, and prevents new players from joining',
                                       inline=False)
            mod_crsdky_embed.add_field(name='`stop`',
                                       value='Pauses the round until the `start` command is recieved',
                                       inline=False)
            mod_crsdky_embed.add_field(name='`resetPlayer`',
                                       value='Removes all players from the game',
                                       inline=False)
            await message.channel.send(embed=mod_crsdky_embed)
    elif command[1] == 'ref':
        ref_embed = discord.Embed(title='`'+prefix+'ref` Command List',
                                  description='Displays a users primary ref.',
                                  color=0x45FFFF)
        try:
            icon_url = client.user.guild_avatar.url
        except AttributeError:
            icon_url = client.user.avatar.url
        ref_embed.set_author(name=client.user.name, icon_url=icon_url)
        ref_embed.add_field(name='No argument',
                            value='Displays your ref',
                            inline=False)
        ref_embed.add_field(name='`User ID/Tagged User/Nickname`',
                            value='Searches for a user\'s profile. Tagging the desired user, or using their member ID '
                                  'yields the most accurate results.',
                            inline=False)
        ref_embed.add_field(name='`set <string/ref>`',
                            value='Changes your ref to say what you want. Only emotes from this server can be used.',
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
        embed.set_author(name=client.user.name, icon_url=icon_url)
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
                        value='Shows a user\'s OCs',
                        inline=False)
        await message.channel.send(embed=embed)
    elif command[1] == 'artfight':
        artfight_embed = discord.Embed(title='`'+prefix+'artfight` Command List',
                                       description='This is the commands for the annual Art Fight',
                                       color=0x45FFFF)
        artfight_embed.add_field(name='join',
                                 value='Assigns a user to a team ',
                                 inline=False)
        artfight_embed.add_field(name='scores',
                                 value='shows the team scores',
                                 inline=False)
        artfight_embed.add_field(name='submit',
                                 value='This is how you submit art. See <#787316128614973491> for scoring.',
                                 inline=False)
        artfight_embed.add_field(name='remove [1/2] [score to remove]',
                                 value='Takes score away from a team (1/2). Use negative numbers to add '
                                       'score.\nMod only.',
                                 inline=False)
        await message.channel.send(embed=artfight_embed)


cursed_keys_running = False
blessed_keys_running = False
crsd_keys = []
blessed_keys = []
player_role_id = 863630913686077450


async def cursed_keys(message):
    """
    Handles all crsdky game functions and methods.
    Last docstring edit: -Autumn V1.14.5
    Last method edit: -Autumn V1.14.8
    :param message:
    :return:
    """
    # TODO: USE A SWITCH HERE DUMBASS!!!
    global cursed_keys_running
    global crsd_keys

    command = message.content[1:].split(' ', 2)
    if len(command) == 1 or command[1] == 'help':
        overview = discord.Embed(title='Cursd Ky Overview',
                                 description='Welcome, to a brutal game called "CURSD KY" (Idea by Reek and Isybel)\n\n'
                                             ' The main of the game is to avoid a certain key/letter on your keyboard '
                                             '(mostly vowels), But still try to make sure everyone understands what you'
                                             ' are trying to say. The last survivor standing wins and will be given a '
                                             'custom role',
                                 color=0x45ffff)
        overview.add_field(name='RULES',
                           value="-You can't the leave the game until you lose and the bot will remove your roles to "
                                 "get rid of the curse"
                                 "\n-Once you make a mistake, you will be instantly disqualified"
                                 "\n-This challenge will apply to every chat on this server, so be careful"
                                 "\n-you have to use an alt word to describe what you want to say rather censor that "
                                 "word"
                                 "\n-Abusing rule loop hole is not allowed"
                                 "\n-Using emoji contain that key also not allowed"
                                 "\n-If you don't talk in general, you'll also lose (we check)",
                           inline=False)
        await message.reply(embed=overview)
        overview.add_field(name='QnA', value='', inline=False)
        overview.add_field(name='Q: What does "crsd ky" mean?',
                           value='A: It\'s "Cursed Key" but get rid of the vowels cause they are cursed.')
        overview.add_field(name='Q: What made you come up with this game?',
                           value='A: Isybel is upset she can\'t curse in my server, so she cursed me by removing my '
                                 'ability to use the letter "a" and I took it as a challenge xD (But I lost rip) ')
        overview.add_field(name='Q: What do I do if i got removed but dont think I should\'ve been?',
                           value='A: contact a moderator, and we\'ll look into your case and determine if you should '
                                 'still be in the game or not')
    elif command[1] == 'list':
        if len(crsd_keys) == 0:
            await message.reply('there are no cursed keys')
        else:
            await message.reply('cursed keys are: '+str(crsd_keys))
    elif command[1] == 'join':
        if not cursed_keys_running:
            if message.guild.get_role(player_role_id) in message.author.roles:
                await message.reply('You are already a part of this game!')
            else:
                await message.author.add_roles(message.guild.get_role(player_role_id))
                await message.reply('Joined the game!')
        else:
            await message.reply("Unable to join. a game is already running")
    elif command[1] == 'leave':
        await message.author.remove_roles(message.guild.get_role(player_role_id))
        await message.reply('You have been removed from the game')
    elif command[1] == 'set':
        chars = command[2].split(' ')
        keys = []
        for char in chars:
            if len(char) > 1:
                pass
            else:
                keys.append(char.lower())
                crsd_keys = keys
        await message.reply('Cursed Keys set: ' + str(crsd_keys))
    elif command[1] == 'start':
        if message.author.guild_permissions.manage_roles:
            cursed_keys_running = True
            if len(crsd_keys) == 0:
                await message.reply('Unable to start game! No Cursed Keys set!')
            else:
                await message.reply('<@&863630913686077450> The game is starting! Cursed Keys are ' + str(crsd_keys))
        else:
            await message.reply('Invalid permissions')
    elif command[1] == 'resetPlayers':
        if message.author.guild_permissions.manage_roles:
            for member in message.guild.get_role(player_role_id).members:
                await member.remove_roles(message.guild.get_role(player_role_id))
        await message.reply('Players reset')
    elif command[1] == 'stop':
        if message.author.guild_permissions.manage_roles:
            cursed_keys_running = False
            await message.reply('Game Stopped')
        else:
            await message.reply('Invalid Permissions')
    elif command[1] == 'numleft':
        await message.reply(str(len(message.guild.get_role(player_role_id).members)))


async def blessed_keys(message):
    """
        Handles all Blessed Key game functions and methods.
        Last docstring edit: -Autumn V3.5.0
        Last method edit: -Autumn V3.5.0
        :param message:
        :return:
    """
    # TODO: USE A SWITCH HERE DUMBASS!!!
    global cursed_keys_running
    global blessed_keys
    
    command = message.content[1:].split(' ', 2)
    if len(command) == 1 or command[1] == 'help':
        overview = discord.Embed(title='Blessed Ky Overview',
                                 description='Welcome, to a brutal game called "Blessed Key" (Idea by Reek)\n\n'
                                             'The main of the game is to use a certain key/letter on your keyboard '
                                             'in every message you send, but still try to make sure everyone '
                                             'understands what you are trying to say. The last survivor standing wins '
                                             'and will be given a custom role',
                                 color=0x45ffff)
        overview.add_field(name='RULES',
                           value="-You can't the leave the game until you lose and the bot will remove your roles to "
                                 "get rid of the curse"
                                 "\n-Once you make a mistake, you will be instantly disqualified"
                                 "\n-This challenge will apply to every chat on this server, so be careful"
                                 "\n-you have to use a letter in every single sentence"
                                 "\n-Abusing rule loop hole is not allowed"
                                 "\n-Using emoji contain that key also not permitted"
                                 "\n-If you don't talk in general, you'll also lose (we check)",
                           inline=False)
        await message.reply(embed=overview)
        overview.add_field(name='QnA', value='', inline=False)
        overview.add_field(name='Q: What does "crsd ky" mean?',
                           value='A: It\'s "Cursed Key" but get rid of the vowels cause they are cursed.')
        overview.add_field(name='Q: What made you come up with this game?',
                           value='A: Isybel is upset she can\'t curse in my server, so she cursed me by removing my '
                                 'ability to use the letter "a" and I took it as a challenge xD (But I lost rip) ')
        overview.add_field(name='Q: What do I do if i got removed but dont think I should\'ve been?',
                           value='A: contact a moderator, and we\'ll look into your case and determine if you should '
                                 'still be in the game or not')
    elif command[1] == 'list':
        if len(blessed_keys) == 0:
            await message.reply('there are no blessed keys')
        else:
            await message.reply('blessed keys are: ' + str(blessed_keys))
    elif command[1] == 'join':
        if not blessed_keys_keys_running:
            if message.guild.get_role(player_role_id) in message.author.roles:
                await message.reply('You are already a part of this game!')
            else:
                await message.author.add_roles(message.guild.get_role(player_role_id))
                await message.reply('Joined the game!')
        else:
            await message.reply("Unable to join. a game is already running")
    elif command[1] == 'leave':
        await message.author.remove_roles(message.guild.get_role(player_role_id))
        await message.reply('You have been removed from the game')
    elif command[1] == 'set':
        chars = command[2].split(' ')
        keys = []
        for char in chars:
            if len(char) > 1:
                pass
            else:
                keys.append(char.lower())
                blessed_keys = keys
        await message.reply('Blessed Keys set: ' + str(blessed_keys))
    elif command[1] == 'start':
        if message.author.guild_permissions.manage_roles:
            cursed_keys_running = True
            if len(blessed_keys) == 0:
                await message.reply('Unable to start game! No Cursed Keys set!')
            else:
                await message.reply(f'<@&863630913686077450> The game is starting! blessed Keys are ' + str(
                        blessed_keys))
        else:
            await message.reply('Invalid permissions')
    elif command[1] == 'resetPlayers':
        if message.author.guild_permissions.manage_roles:
            for member in message.guild.get_role(player_role_id).members:
                await member.remove_roles(message.guild.get_role(player_role_id))
        await message.reply('Players reset')
    elif command[1] == 'stop':
        if message.author.guild_permissions.manage_roles:
            blessed_keys_running = False
            await message.reply('Game Stopped')
        else:
            await message.reply('Invalid Permissions')
    elif command[1] == 'numleft':
        await message.reply(str(len(message.guild.get_role(player_role_id).members)))


# Todo: look over and verify the purge code will work
async def purge(message):
    """
    method removes all members with the unverified role from Rikoland
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.14.4
    :param message: Message that called the bot
    :return: None
    """
    unverified_role_id = data[str(message.guild.id)]["roles"]['unverified']
    
    if message.author.guild_permissions.manage_roles:
        unverified_ppl = message.guild.get_role(unverified_role_id).members
        num_kicked = 0
        for member in unverified_ppl:
            try:
                await member.kick(reason='Server purge.')
                num_kicked += 1
            except discord.Forbidden:
                await message.channel.send('unable to kick <@' + str(member.id) + '>')
        await message.reply(str(len(unverified_ppl)) + ' members purged from Rikoland')
    else:
        await message.reply('Error 403: Forbidden\nInsufficient Permissions')


async def prune(message):
    """
    Removes inactive members from the server
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.14.4
    :param message:
    :return: NoneType
    """
    if message.author.guild is not None and message.author.guild_permissions.kick_members:
        # only run if in a guild and the user could do this manually.
        members = message.guild.members
        ignore_roles = [667970355733725184, 970723533846106165, 716173532245131265, 678102571063443499,
                        667246861328842774, 655755488100745247, 1006767850196840510, 911988983825842177,
                        932681590159601664, 936554410442620950, 903902681242931261, 612939346479153172,
                        915042582445322290, 612554353764597760]
        for member in members:
            for role in member.roles:
                if role.id in ignore_roles:
                    continue
                else:
                    member,
    else:
        await message.reply('Unable to comply. You either are attempting to use this in a DM, lack permission, '
                            'or both.')
        
        
async def join_pos(message):
    """
    Displays the number a user joined the server in.
    Last docstring edit: -Autumn V1.14.5
    Last function edit: -Autumn V1.16.3
    :param message: The message that called the command
    :return: NoneType
    """
    command = message.content.split(' ')
    if len(command) == 1:
        target = message.author.id
    else:
        try:
            target = int(command[1])
        except ValueError:
            await message.reply('Value Error: Please make sure the ID is a number')
            return -1

    pos = get_join_rank(target, message.guild)
    if pos == -1:
        await message.reply('Member <@%d> is not in the guild' % (target,))
    else:
        name = message.guild.get_member(target).name
        await message.reply('Member %s joined in position %d' % (name, pos))


def get_join_rank(target_id, target_guild):  # Call it with the ID of the user and the guild
    """
    Returns the rank at which a user joined the server.
    :param target_id:
    :param target_guild:
    :return:
    """
    members = target_guild.members

    def sortby(a):
        return a.joined_at.timestamp()

    members.sort(key=sortby)

    i = 0
    for member in members:
        i += 1
        if member.id == target_id:
            return i
    return -1


def get_member_position(position, target_guild):
    """
    Unknown function.
    Last docstring edit: -Autumn V1.16.3
    Last function edit: Unknown
    :param position:
    :param target_guild: Guild the member is in
    :return:
    """
    # TODO: Analyze function and correct the docstring
    members = target_guild.members

    def sort_by(a):
        return a.joined_at.timestamp()

    members.sort(key=sort_by)

    return members[position-1]


async def member_num(message):
    """
    I have no idea what this is. I need to make more detailed analysis later
    :param message:
    :return:
    """
    # TODO: Analyze function and correct the docstring
    command = message.content.split(' ')
    if len(command) == 1:
        await message.reply('Missing Argument: Member number')
        return
    else:
        try:
            position = int(command[1])
        except ValueError:
            await message.reply('Value Error: Please make sure the positon is a number')
            return

    pos = get_member_position(position, message.guild)
    if pos == -1:
        await message.reply('There is no member in position %d' % position)
    else:
        name = pos.name
        await message.reply('Member in position %d has the ID %d' % (position, name))


async def artfight(message):
    await Artfight.artfight(message, client)


async def huh(message):
    """
    Easter egg
    Last docstring edit: -Autumn V1.14.4
    Last method edit: Unknown
    :param message:
    :return: None
    """
    await message.reply("We've been trying to reach you about your car's extended warranty")


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
            'setcode': setcode, 'modmail': modmail, 'quit': end, 'setref': set_ref, 'ref': ref, 'addref': add_ref,
            'crsdky': cursed_keys, 'crsdkey': cursed_keys, 'crsedky': cursed_keys, 'cursedkey': cursed_keys,
            'cursdky': cursed_keys, 'cursdkey': cursed_keys, 'cursedky': cursed_keys, 'oc': oc, 'purge': purge,
            'join_pos': join_pos, 'huh': huh, 'kick': kick, 'blessedkey': blessed_keys, 'ban': ban, 'artfight': artfight,
            'random_ref': random_ref, 'randomref': random_ref, 'rr': random_ref, 'setup': setup, 'uptime': uptime}

scan_ignore = [688611557508513854]


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
    global cursed_keys_running
    global blessed_keys_running

    if message.author.bot:
        return
    
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        if not message.author.guild_permissions.mention_everyone:
            await AntiScam.scan_message(message)
    content = message.content.lower()

    if message.guild is None or content.find(AntiScam.code) != -1 or \
            message.author.guild_permissions.administrator or message.channel.id in scan_ignore:
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
        if cursed_keys_running and message.guild is not None:
            # TODO: Make this a separate function.
            # Check if the message author has the game role
            if message.guild.get_role(player_role_id) in message.author.roles:
                # If the message author has the role, scan their message for any cursed keys
                for key in crsd_keys:
                    if key in message.content.lower():
                        await message.author.remove_roles(message.guild.get_role(player_role_id))
                        await message.reply('You have been cursed for using the key: ' + key)
    
                        if len(message.guild.get_role(player_role_id).members) == 1:
                            # This code detects if there is a winner
                            cursed_keys_running = False
                            await message.channel.send('<@!' + str(message.guild.get_role(player_role_id).members[0].id) +
                                                       '> wins the game!')
                        break
        if blessed_keys_running and message.guild is not None:
            # TODO: Make this a separate function.
            # Check if the message author has the game role
            if message.guild.get_role(player_role_id) in message.author.roles:
                # If the message author has the role, scan their message for any cursed keys
                for key in blessed_keys:
                    if key not in message.content.lower():
                        await message.author.remove_roles(message.guild.get_role(player_role_id))
                        await message.reply('You have been cursed for not using the key: ' + key)
                
                        if len(message.guild.get_role(player_role_id).members) == 1:
                            # This code detects if there is a winner
                            cursed_keys_running = False
                            await message.channel.send(
                                '<@!' + str(message.guild.get_role(player_role_id).members[0].id) +
                                '> wins the game!')
                        break
    except IndexError:
        pass


def run_sunreek():
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
        inp = int(input('input token num\n1. SunReek\n2. Testing Environment\n'))
    
    if inp == 1:
        # Main bot client. Do not use for tests

        client.run(os.environ.get('SUNREEK_TOKEN'))     # must say client.run(os.environ.get('SUNREEK_TOKEN'))

    elif inp == 2:
        # Test Bot client. Allows for tests to be run in a secure environment.
        prefix = '>'

        client.run(os.environ.get('TESTBOT_TOKEN'))     # must say client.run(os.environ.get('TESTBOT_TOKEN'))


if __name__ == '__main__':
    run_sunreek()
