import time
import discord
import os
import sys


from profile import display_profile, set_bio
from refManagement import ref, set_ref, add_ref, oc
from fileManagement import warn_log_path
from main import read_line, get_user_id


blacklist = ['@everyone', 'https://', 'gift', 'nitro', 'steam', '@here', 'free', 'who is first? :)', "who's first? :)"]
code = 'plsdontban'


start_time = time.time()
# TODO: Add uptime feature.

prefix = '>'
version_num = '1.1.0'

eclipse_id = 440232487738671124

intents = discord.Intents.default()
intents.members = True

game = discord.Game(prefix + "help for commands")
client = discord.Client(intents=intents)

guild = None

suspended_1_id = 955229885163532319
suspended_2_id = 955230786993414156

mail_inbox = 955207611379245066             # modmail inbox channel
log_channel = 955224780318081095            # channel all bot logs get sent
warn_log_id = 955563724511518790


async def ping(message):
    """
    Displays the time it takes for the bot to send a message upon a message being received.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.16.2
    :param message: Message calling the bot
    :return: None
    """
    start = time.time()
    x = await message.channel.send('Pong!')
    ping_time = time.time() - start
    edit = x.content + ' ' + str(int(ping_time * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message):
    """
    Displays the version of the bot being used
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.14.4
    :param message: Message calling the bot
    :return: None
    """
    await message.channel.send('I am currently running version ' + version_num)


async def end(message):
    """
    Quits the bot. Sends a message and updates the game status to alert users the bot is quiting.

    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.14.4
    :param message: Message calling the bot
    :return: None
    """
    global game
    if message.author.id == eclipse_id or message.author.guild_permissions.administrator:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        await client.close()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def warn(message):
    """
    Warns a user for a specified rule with a custom reason.
    format: >warn <user> <rule> <reason>
    :param message:
    :return:
    """
    command = message.content[1:].split(' ', 3)
    if len(command) <= 2:
        embed = discord.Embed(title='Warn Command usage')
        embed.add_field(name='>warn [user] [rule number]', value='gives a user a warn')
        embed.add_field(name='>warn [user] [rule number] [reason]', value='Warns a user with the reason provided')
        await message.channel.send(embed=embed)
        return

    target_id = get_user_id(message, 1)
    rule_num = command[2]
    try:
        reason = command[3]
    except IndexError:
        reason = 'No reason provided'

    try:
        os.scandir(warn_log_path(target_id))
    except FileNotFoundError:
        os.mkdir(warn_log_path(target_id))

    os.chdir(warn_log_path(target_id))

    files = os.listdir()
    warn_num = len(files) + 1

    warn_time = time.strftime("%d/%m/%y %H:%M", time.gmtime())

    try:
        lines = [command[2], command[3], str(message.author.id), warn_time]
    except IndexError:
        await message.reply('Improper formatting. Warns need `>warn <target> <rule_num> <reason>')
        return

    with open(warn_log_path(target_id)+'\\'+str(warn_num)+'.warn', 'w') as warn_file:
        for line in lines:
            warn_file.writelines(line + '\n')
    await message.guild.get_channel(warn_log_id).send('<@'+str(target_id)+'> Warned for '+rule_num+'\nReason: '+reason)
    await message.channel.send('<@'+str(target_id)+'> You have been warned under rule '+rule_num+' for '+reason)


async def list_warnings(message):
    """
    format: >listwarnings <user/user_id/username/display_name>
    aliases: listwarns, listwarning, lw
    :param message:
    :return:
    """
    target_id = get_user_id(message, 1)
    warn_folder_path = warn_log_path(target_id)

    display_name = message.guild.get_member(target_id).display_name
    list_embed = discord.Embed(title=display_name+"'s Warnings")

    try:
        os.chdir(warn_log_path(target_id))
    except FileNotFoundError:
        os.mkdir(warn_log_path(target_id))

    i = 1
    with os.scandir(warn_folder_path) as files:
        for warn_path in files:
            with open(warn_path) as warn:
                lines = warn.readlines()
                list_embed.add_field(name='Warn #'+str(i),
                                     value='Rule number: ' + lines[0] +
                                           '\nReason: ' + lines[1] +
                                           '\nResponsible moderator: ' + lines[2] +
                                           '\nDate: ' + lines[3],
                                     inline=False)
                i += 1
    await message.channel.send(embed=list_embed)


async def modmail(message):
    """
    Sends a message to the moderators. Alerts the user if an error occurs during the process
    Last docstring edit: -Autumn V1.14.4
    Last method edit: Unknown
    :param message: Message that called the bot
    :return: None
    """
    sender = message.author
    await message.delete()

    dm = await sender.create_dm()
    try:
        subject = await read_line(client, dm, 'Subject Line:', sender, delete_prompt=False, delete_response=False)
        subject = 'Modmail | ' + subject.content
        body = await read_line(client, dm, 'Body:', sender, delete_prompt=False, delete_response=False)
        await dm.send('Your message has been sent')
    except discord.Forbidden:
        await message.reply('Unable to DM. Check your privacy settings')
        return

    mail = discord.Embed(title=subject, color=0xadd8ff)
    mail.set_author(name=sender.name, icon_url=sender.avatar_url)
    mail.add_field(name='Message', value=body.content)
    mail.add_field(name='User ID', value=str(message.author.id), inline=False)
    await message.guild.get_channel(mail_inbox).send(embed=mail)


async def kick(message):
    """
        Method designed to kick users from the server the command originated.
        >kick [user] [reason]
        Last docstring edit: -Autumn V1.0.0
        Last method edit: -Autumn V1.0.0
        Method added: V1.0.0
        :param message:The message that called the command
        :return: None
        """
    if message.author.guild_permissions.kick_members:
        command = message.content[1:].split(' ', 2)
        if len(command) == 1:
            embed = discord.Embed(title='Kick Command usage')
            embed.add_field(name='>kick [user]', value='Kicks a user from the server')
            embed.add_field(name='>kick [user] [reason]', value='Kicks a user with the reason provided')
            await message.channel.send(embed=embed)
            return

        target = get_user_id(message)

        if len(command) > 2:
            reason = command[2]
        else:
            reason = 'No reason specified.'
        try:
            await message.guild.kick(message.guild.get_member(target), reason=reason)
            await message.channel.send('<@!' + target + '> was kicked.')
        except discord.Forbidden:
            await message.reply('__**Error 403: Forbidden**__\nPlease verify I have the proper permissions.')

    else:
        await message.reply('Unauthorized usage.')


async def ban(message):
    """
        Method designed to ban users from the server the command originated. Deletes User messages from the last 24
        hours
        >ban [user] [reason]
        Last docstring edit: -Autumn V1.16.0
        Last method edit: -Autumn V1.16.3
        Method added: -Autumn V1.16.0
        :param message:The message that called the command
        :return: None
        """
    if message.author.guild_permissions.ban_members:
        command = message.content[1:].split(' ', 2)
        if len(command) == 1:
            embed = discord.Embed(title='Ban Command usage', description='All bans have ` | GM` appended to '
                                                                         'them for documentation in the Server '
                                                                         'Protector database')
            embed.add_field(name='>ban [user]', value='Bans a user from the server')
            embed.add_field(name='>ban [user] [reason]', value='Bans a user with the reason provided')
            await message.channel.send(embed=embed)
            return

        target = get_user_id(message, 1)

        if len(command) > 2:
            reason = command[2]
        else:
            reason = 'No reason specified.'

        try:
            await message.guild.ban(message.guild.get_member(target),
                                    reason=reason + ' | GM',
                                    delete_message_days=1)
            await message.channel.send('<@!' + str(target) + '> was banned.')
        except discord.Forbidden:
            await message.reply('__**Error 403: Forbidden**__\nPlease verify I have the proper permissions.')

    else:
        await message.reply('Unauthorized usage.')


async def help_message(message):
    """
    Displays the Bot's help message. Square brackets are optional arguments, angle brackets are required.
    Last docstring edit: -Autumn V1.0.0
    Last method edit: -Autumn V1.0.0
    :param message:
    :return:
    """
    # TODO: USE A SWITCH HERE!!!
    command = message.content[1:].split(' ')
    if len(command) == 1:
        embed = discord.Embed(title="Gardenbot Command list",
                              description='Square brackets are optional arguments. Angle brackets are required '
                                          'arguments',
                              color=0x45FFFF)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)

        embed.add_field(name='`'+prefix+'help`',
                        value="That's this command!",
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
        embed.add_field(name='`'+prefix+'OC`',
                        value="Manages a users OCs",
                        inline=False)
        embed.add_field(name='`'+prefix+'quit`',
                        value='quits the bot.\n Mod only.',
                        inline=False)
        embed.add_field(name='`' + prefix + 'huh`',
                        value='???',
                        inline=False)
        await message.channel.send(embed=embed)
    elif command[1] == 'help':
        help_embed = discord.Embed(title="SunReek Command list", color=0x45FFFF)
        help_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        help_embed.add_field(name='`' + prefix + 'help [bot command]`', value="That's this command!", inline=False)
        await message.channel.send(embed=help_embed)
    elif command[1] == 'profile':
        profile_embed = discord.Embed(title='Profile Command list',
                                      description='Displays a users profile',
                                      color=0x45FFFF)

        profile_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)

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
    elif command[1] == 'ref':
        ref_embed = discord.Embed(title='`'+prefix+'ref` Command List',
                                  description='Displays a users primary ref.',
                                  color=0x45FFFF)
        ref_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
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
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
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


async def profile(message):
    """
    Handles all profile changes and calls the desired methods.
    Last docstring edit: -Autumn V1.14.5
    Last method edit: Unknown
    :param message:
    :return:
    """
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


async def huh(message):
    """
    Easter egg
    Last docstring edit: -Autumn V1.14.4
    Last method edit: Unknown
    :param message:
    :return: None
    """
    await message.reply("We've been trying to reach you about your car's extended warranty")


async def scan_message(message):
    """
    The primary anti-scam method. This method is given a message, counts the number of flags in a given message, then
    does nothing if no flags, flags the message as a possible scam if 1-3, or flags and deletes the message at 3+ flags.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.14.5
    :param message: the message sent
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
        if flags >= 3:
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
    Method called when the bot boots and is fully online
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.16.3
    :return: None
    """
    global guild

    print('We have logged in as {0.user}'.format(client))

    guild = client.get_guild(955148737427157062)
    await client.change_presence(activity=game)
    await guild.get_member(eclipse_id).send('Running, and active')
    # artfight_load()


switcher = {'help': help_message, 'ping': ping, 'version_num': version, 'modmail': modmail, 'quit': end, 'oc': oc,
            'profile': profile,  'setref': set_ref, 'ref': ref, 'addref': add_ref, 'huh': huh, 'kick': kick, 'ban': ban,
            'warn': warn, 'listwarnings':list_warnings, 'listwarns': list_warnings, 'lw': list_warnings}


@client.event
async def on_message(message):
    """
    The primary method called. This method determines what was called, and calls the appropriate message, as well as
    handling all message scanning. This is called every time a message the bot can see is sent.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.14.4
    :param message:
    :return: None
    """
    global cursed_keys_running
    global application_channel
    global verified_role_id
    global questioning_role_id

    if message.author.bot:
        return
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        if not message.author.guild_permissions.mention_everyone:
            await scan_message(message)
    content = message.content.lower()

    if message.guild != guild or message.guild is None or content.find(code) != -1 or \
            message.author.guild_permissions.administrator:
        pass
    else:
        # await scan_message(message)
        pass

    if message.content.startswith(prefix):

        # split the message to determine what command is being called
        command = message.content[1:].lower().split(' ', 1)

        # search the switcher for the command called. If the command is not found, do nothing
        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            pass
        if command[0] == 'print':
            # Used to transfer data from Discord directly to the command line. Very simple shortcut
            print(message.content)


def run_gardenbot():
    """
    Function allows the host to pick whether to run the live bot, or run the test bot in a closed environment, without
    switching programs. This allows the live code to run parallel to the testing code and prevent constant restarts to
    test new features.
    Last docstring edit: -Autumn V1.0.0
    Last function edit: Unknown
    :return: None
    """
    global prefix
    global testing_client

    inp = int(input('input token num\n1. gardenbot\n2. Testing Environment\n'))

    if inp == 1:
        # Main bot client. Do not use for tests
        client.run(os.environ.get('GARDENBOT_TOKEN'))
    elif inp == 2:
        # Test Bot client. Allows for tests to be run in a secure environment.
        testing_client = True
        client.run(os.environ.get('TESTBOT_TOKEN'))


if __name__ == '__main__':
    run_gardenbot()
