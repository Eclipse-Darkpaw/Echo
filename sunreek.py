import time
import discord
import os
import sys

from profile import display_profile, set_bio
from refManagement import ref, set_ref, add_ref, oc
from main import read_line, get_user_id


start_time = time.time()
# TODO: Add uptime feature.

prefix = '}'
version_num = '2.0.0'

eclipse_id = 440232487738671124

intents = discord.Intents.default()
intents.members = True

game = discord.Game(prefix + "help for commands")
client = discord.Client(intents=intents)

guild = None

unverified_role_id = 612958044132737025     # Role assigned to unverified users. is removed on verification
verified_role_id = 811522721824374834       # role to assign members who verify successfully
questioning_role_id = 819238442931716137    # Role to assign when users

application_channel = 819223217281302598    # channel where finished applications go
mail_inbox = 840753555609878528             # modmail inbox channel
log_channel = 933456094016208916            # channel all bot logs get sent

testing_channel = 952750855285784586

counter = 0
active_forms = 0
incomplete_forms = 0
submitted_forms = 0
application_questions = ['Server Password?\n**NOT YOUR DISCORD PASSWORD**\n(you have 3 attempts to fill the form)',
                         'What is your nickname?',
                         'How old are you?',
                         'Where did you get the link from? Please be specific. If it was a user, please use the full '
                         'name and numbers(e.g. Echo#0109)',
                         'Why do you want to join?']

blacklist = ['@everyone', 'https://', 'gift', 'nitro', 'steam', '@here', 'free', 'who is first? :)', "who's first? :)"]
code = 'plsdontban'

artfight_enabled = False

testing_client = False


class Application:
    def __init__(self, applicant, channel, applicant_guild):
        global counter
        global active_forms
        global incomplete_forms
        counter += 1
        active_forms += 1
        incomplete_forms += 1
        self.applicant = applicant
        self.channel = channel
        self.guild = applicant_guild
        self.count = counter
        self.responses = []

    async def question(self):
        global application_questions
        global client
        dm = await self.applicant.create_dm()
        for question in application_questions:
            response = await read_line(client, dm, question, self.applicant, delete_prompt=False, delete_response=False)
            if question == application_questions[0]:
                guesses = 2
                for guess in range(guesses):
                    if response.content == 'Ooo festive, joining Riko server les go':
                        break
                    question = 'Incorrect password ' + str(guesses) + ' attempts remaining'
                    guesses -= 1
                    response = await read_line(client, dm, question, self.applicant, delete_prompt=False,
                                                   delete_response=False)
                    if guesses <= 0:
                        await dm.send('No guesses remain.')
                        return -1
                    else:
                        continue
            self.responses.append(response.content)
        await dm.send('Please wait while your application is reviewed. I will need to DM you when your application is '
                      'fully processed.')
        return 1

    def gen_embed(self):
        global application_questions

        embed = discord.Embed(title='Application #' + str(self.count))
        embed.set_author(name=self.applicant.name, icon_url=self.applicant.avatar_url)

        for i in range(len(application_questions)):
            embed.add_field(name=application_questions[i], value=self.responses[i])

        embed.add_field(name='User ID', value=str(self.applicant.id), inline=False)

        return embed

    def __str__(self):
        return 'Application for ' + str(self.applicant) + '\nWhere did you get the link from?'


class Message:
    def __init__(self, content, channel):
        self.content = content
        self.channel = channel

    def reply(self, content):
        await self.channel.send(content)


async def verify(message):
    """
    The method that primarily handles member verification. All members must verify from this method. Sends DM to user,
    asks user questions, then sends answers to the moderators in a designated chat
    Last docstring edit: -Autumn V1.14.5
    Last method edit: -Autumn V1.16.3
    :param message: Discord message calling the method
    :return: NoneType
    """
    global active_forms
    global incomplete_forms
    global submitted_forms
    msg_guild = message.guild

    if verified_role_id in message.guild.get_member(message.author.id).roles:
        await message.channel.send('You are already verified')
        return

    applicant = message.author
    application = Application(applicant, message.channel, message.guild)

    if not testing_client:
        channel = msg_guild.get_channel(application_channel)
    else:
        channel = message.channel

    try:
        questioning_error_code = await application.question()
    except discord.errors.Forbidden:
        await message.channel.send('<@!'+str(message.author.id)+'> I cannot send you a message. Change your privacy '
                                                                'settings in User Settings->Privacy & Safety')
        active_forms -= 1
        incomplete_forms -= 1
        return

    if questioning_error_code == -1:
        try:
            await channel.send('<@!'+str(message.author.id)+'> kicked for excessive password guesses.')
            await message.guild.kick(message.author, reason='Too many failed password attempts')
        except discord.Forbidden:
            await message.channel.send("Unable to complete task. Please verify my permissions are correct\n```Error 403"
                                       "\nsunkreek.py Line 160:13\n"
                                       "await message.guild.kick(message.author, reason='Too many failed password "
                                       "attempts')```")

    applied = await channel.send(embed=application.gen_embed())
    emojis = ['✅', '❓', '🚫', '❗']
    for emoji in emojis:
        await applied.add_reaction(emoji)

    def check(reaction, user):
        """
        Checks for reactions on a message.
        :param reaction:
        :param user:
        :return: boolean
        """
        return user != client.user and user.guild_permissions.manage_roles and str(reaction.emoji) in emojis and\
               reaction.message == applied

    incomplete_forms -= 1
    submitted_forms += 1
    while True:
        reaction, user = await client.wait_for('reaction_add', check=check)
        if str(reaction.emoji) == '✅':
            await application.applicant.add_roles(msg_guild.get_role(verified_role_id))

            try:
                await message.author.send('You have been approved.')
            except discord.Forbidden:
                await channel.send('Unable to DM <@!'+str(message.author.id)+'>')

            await application.applicant.remove_roles(msg_guild.get_role(questioning_role_id))
            await application.applicant.remove_roles(msg_guild.get_role(unverified_role_id))
            await channel.send('<@!'+str(message.author.id)+'> approved')

            active_forms -= 1
            submitted_forms -= 1

            await applied.add_reaction('🆗')
            break
        elif str(reaction.emoji) == '❓':
            await application.applicant.add_roles(msg_guild.get_role(questioning_role_id))
            await channel.send('<@!'+str(message.author.id)+'>  is being questioned')
            await message.author.send('You have been pulled into questioning.')
        elif str(reaction.emoji) == '🚫':
            reason = await read_line(client, msg_guild.get_channel(application_channel),
                                     'Why was <@!' + str(message.author.id) + '> denied?', user,
                                     delete_prompt=False, delete_response=False)

            if reason == 'cancel':
                await channel.send('Action cancelled')
                continue
            else:
                await message.author.send('Your application denied for:\n> ' + reason.content)
                await channel.send('<@!'+str(message.author.id)+'> was denied for:\n> '+reason.content)
                active_forms -= 1
                submitted_forms -= 1
                await applied.add_reaction('🆗')
                break
        elif str(reaction.emoji) == '❗':
            reason = await read_line(client, msg_guild.get_channel(application_channel), 'Why was <@!' +
                                     str(message.author.id) + '> banned? write `cancel` to cancel.', user,
                                     delete_prompt=False, delete_response=False)
            reason = reason.content
            if reason == 'cancel':
                await channel.send('Ban cancelled')

            else:
                try:
                    await message.guild.ban(user=application.applicant, reason=reason)
                    await channel.send('<@{}> banned for\n> {}'.format(message.author.id, reason))
                    active_forms -= 1
                    submitted_forms -= 1
                    await applied.add_reaction('🆗')
                    break
                except discord.Forbidden:
                    await channel.send('Error 403: Forbidden. Insufficient permissions.')
                except discord.HTTPException:
                    await channel.send('Ban failed. Please try again, by reacting to the message again.')


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
        await save(message)
        await client.close()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def restart(message):
    """
    Restarts the bot. Rarely called.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.16.3
    :param message:
    :return: None
    """
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        os.execl(sys.executable, __file__, 'main.py')
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def save(message):
    """
    Saves necessary bot data to the necessary files
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.16.3
    :param message:
    :return:
    """
    # artfight_save()
    await message.reply('Data saved')


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
        message.reply('Unable to DM. Check your privacy settings')
        return

    mail = discord.Embed(title=subject, color=0xadd8ff)
    mail.set_author(name=sender.name, icon_url=sender.avatar_url)
    mail.add_field(name='Message', value=body.content)
    await message.guild.get_channel(mail_inbox).send(embed=mail)


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
    if message.author.guild_permissions.kick_members:
        command = message.content[1:].split(' ', 2)
        if len(command) == 1:
            embed = discord.Embed(title='Kick Command usage')
            embed.add_field(name='}kick [user]', value='Kicks a user from the server')
            embed.add_field(name='}kick [user] [reason]', value='Kicks a user with the reason provided')
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
            embed = discord.Embed(title='Ban Command usage', description='All bans have the ` | Rikoland` appended to '
                                                                         'the reason for documentation in the Server '
                                                                         'Protector database')
            embed.add_field(name='}ban [user]', value='Bans a user from the server')
            embed.add_field(name='}ban [user] [reason]', value='Bans a user with the reason provided')
            await message.channel.send(embed=embed)
            return

        target = get_user_id(message, 1)

        if len(command) > 2:
            reason = command[2]
        else:
            reason = 'No reason specified.'

        try:
            await message.guild.ban(message.guild.get_member(target),
                                    reason=reason + ' | Rikoland',
                                    delete_message_days=1)
            await message.channel.send('<@!' + str(target) + '> was banned.')
        except discord.Forbidden:
            await message.reply('__**Error 403: Forbidden**__\nPlease verify I have the proper permissions.')

    else:
        await message.reply('Unauthorized usage.')


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
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)

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
    elif command[1] == 'crsdky':
        crsdky_embed = discord.Embed(title="`}crsdky Command list", color=0x45FFFF)
        crsdky_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)

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
    elif command[1] == 'artfight':
        artfight_embed = discord.Embed(title='`'+prefix+'artfight` Command List',
                                       description='This is the commands for the annual Art Fight',
                                       color=0x45FFFF)
        artfight_embed.add_field(name='join',
                                 value='this command is disabled',
                                 inline=False)
        artfight_embed.add_field(name='scores',
                                 value='shows the team scores',
                                 inline=False)
        artfight_embed.add_field(name='submit',
                                 value='This is how you submit art. See <#787316128614973491> for scoring.',
                                 inline=False)
        artfight_embed.add_field(name='save',
                                 value='Saves the data to a file to be loaded from later. this is automatically done '
                                       'after every submission',
                                 inline=False)
        artfight_embed.add_field(name='load',
                                 value='loads saved score values',
                                 inline=False)
        artfight_embed.add_field(name='remove [coal/reindeer] [score to remove]',
                                 value='Takes score away from a team (coal/reindeer). Use negative numbers to add '
                                       'score.\nMod only.',
                                 inline=False)
        await message.channel.send(embed=artfight_embed)


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


cursed_keys_running = False
crsd_keys = []
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


async def purge(message):
    """
    method removes all members with the unverified role from Rikoland
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.14.4
    :param message: Message that called the bot
    :return: None
    """
    if message.author.guild_permissions.manage_roles:
        unverified_ppl = message.guild.get_role(unverified_role_id).members
        num_kicked = 0
        for member in unverified_ppl:
            try:
                await member.kick(reason='Server purge.')
                num_kicked += 1
            except discord.Forbidden:
                await message.channel.send('unable to ban <@' + str(member.id) + '>')
        await message.reply(str(len(unverified_ppl)) + ' members purged from Rikoland')
    else:
        await message.reply('Error 403: Forbidden\nInsufficient Permissions')


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
        await message.reply('Member in postion %d has the ID %d' % (position, name))


artfight_team1 = 000000000000000000    # team 1 id
artfight_team2 = 000000000000000000    # team 2 id

artfight_team1_score = 0
artfight_team2_score = 0

artfight_channel = 918673017549238283


'''async def artfight_submit(message, team_num):
    global artfight_team1_score
    global artfight_team2_score

    dm = await message.author.create_dm()

    artfight_questions = ['What type of submission is this?\n1:Black&White Sketch\n2:Color Sketch'
                          '\n3:Black&White Lineart\n4:Flat colored\nPlease reply with the corrosponding number',
                          'Please reply with the number of OCs/characters in your submission',
                          'Is this shaded? Respond "Y" if yes, anything else for no',
                          'Is there a background? Respond "Y" if yes, anything else for no',
                          'What is the title of this piece?']
    responses = []
    try:
        image = await read_line(client, dm, 'What image are you submitting? Only submit one image.', message.author,
                                delete_prompt=False, delete_response=False)
        link = image.attachments[0].url

        for question in artfight_questions:
            question = '<@!' + str(message.author.id) + '> ' + question
            response = await read_line(client, dm, question, message.author, delete_prompt=False, delete_response=False)
            responses.append(response)
    except discord.Forbidden:
        message.reply('Unable to DM You, please change your privacy settings.')
        return -1

    if int(responses[0].content) == 1:
        base = 5
    elif int(responses[0].content) == 2:
        base = 10
    elif int(responses[0].content) == 3:
        base = 20
    elif int(responses[0].content) == 4:
        base = 30
    else:
        await dm.send('Unable to score your submission')
        return -2

    num_chars = int(responses[1].content)

    if responses[2].content.lower() == 'y':
        shaded = 10
    else:
        shaded = 0

    if responses[3].content.lower() == 'y':
        bg = 20
    else:
        bg = 0

    if num_chars > 5:
        num_chars = 5

    score = (base + shaded) * num_chars + bg

    embed = discord.Embed(title=responses[4].content, description='A Submission from <@'+str(message.author.id)+'>')
    embed.add_field(name='Score', value=str(score)+' ornaments')
    embed.set_image(url=link)
    embed.color = message.author.color

    await dm.send(embed=embed)
    response = await read_line(client, dm, 'Do you want to submit this? "Y" for yes.', message.author,
                               delete_prompt=False, delete_response=False)

    if response.content.lower() == 'y':

        if team_num == 1:
            artfight_team1_score += score
            pass
        elif team_num == 2:
            artfight_team2_score += score
            pass
        await dm.send('Submission sent!')
        return embed
    else:
        await dm.send('Submission cancelled. please redo')
        return -2


def artfight_save():
    with open(artfight_scores(), 'w') as file:
        lines = [artfight_team1_score, artfight_team2_score]

        for line in lines:
            file.write(str(line) + '\n')


def artfight_load():
    global artfight_team1_score
    global artfight_team2_score

    with open(artfight_scores(), 'r') as file:
        lines = file.readlines()

    try:
        artfight_team1_score = int(lines[0].split('\n')[0])
        artfight_team2_score = int(lines[1])
    except NameError:
        return -1
    return 1


async def artfight(message):
    global artfight_team1_score
    global artfight_team2_score

    if not artfight_enabled:
        message.reply('This command is currently disabled')
        return
    command = message.content[1:].split(' ', 3)

    if len(command) == 1:
        await help_message(Message('}help artfight', message.channel))
    elif command[1] == 'join':
        await message.reply('This command is not functional')
        return
    elif command[1] == 'scores' and message.author.guild_permissions.manage_roles:
        score_embed = discord.Embed(title='Team scores')
        score_embed.add_field(name='Coal Factories Score', value=str(artfight_team1_score))
        score_embed.add_field(name='Black Nosed Rendeers Score', value=str(artfight_team2_score))
        await message.reply(embed=score_embed)
        artfight_save()
        return
    elif command[1] == 'submit':
        roles = message.author.roles
        role_ids = []

        for role in roles:
            role_ids.append(role.id)

        if message.channel.id == artfight_channel:
            if artfight_team1 in role_ids:
                embed = await artfight_submit(message, 1)

                if embed == -1:
                    await message.reply('Error: Please retry your submission')
                    return
            elif artfight_team2 in role_ids:
                embed = await artfight_submit(message, 2)

                if embed == -1:
                    await message.reply('Error: Please retry your submission')
                    return
            else:
                await message.reply('You are not on an artfight team!')
                return
            await message.reply(embed=embed)
        else:
            await message.reply('You can only use this in <#' + str(artfight_channel) + '>!')
    elif command[1] == 'load' and message.author.guild_permissions.manage_roles:
        error = artfight_load()
        if error == 1:
            await message.reply('Data loaded from memory!')
    elif command[1] == 'save':
        artfight_save()
    elif command[1] == 'remove' and message.author.guild_permissions.manage_roles:
        if command[2] == 'coal':
            artfight_team1_score -= int(command[3])
            await message.reply(command[3]+' ornaments removed from coal')
        elif command[2] == 'reindeer':
            artfight_team2_score -= int(command[3])
            await message.reply(command[3]+' ornaments removed from Reindeer')'''


async def numforms(message):
    """
    Displays the number of verification forms.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: Unknown
    :param message:
    :return:
    """
    await message.reply(str(active_forms) + ' active forms \n' +
                        str(incomplete_forms) + ' incomplete \n' +
                        str(submitted_forms) + ' forms Submitted')


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

    guild = client.get_guild(840181552016261170)
    await client.change_presence(activity=game)
    await guild.get_member(eclipse_id).send('Running, and active')
    # artfight_load()


switcher = {'help': help_message, 'ping': ping, 'version_num': version, 'verify': verify, 'modmail': modmail,
            'quit': end, 'profile': profile, 'restart': restart, 'setref': set_ref, 'ref': ref, 'addref': add_ref,
            'crsdky': cursed_keys, 'oc': oc, 'purge': purge, 'join_pos': join_pos, 'activeforms': numforms,
            'save': save, 'huh': huh, 'kick': kick, 'ban': ban}


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
        await scan_message(message)

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
    elif cursed_keys_running and message.guild is not None:
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
    global testing_client

    inp = int(input('input token num\n1. SunReek\n2. Testing Environment\n'))

    if inp == 1:
        # Main bot client. Do not use for tests

        client.run(os.environ.get('SUNREEK_TOKEN')) # must say client.run(os.environ.get('SUNREEK_TOKEN'))

    elif inp == 2:
        # Test Bot client. Allows for tests to be run in a secure environment.
        prefix = '>'
        testing_client = True

        client.run(os.environ.get('TESTBOT_TOKEN')) # must say client.run(os.environ.get('TESTBOT_TOKEN'))


if __name__ == '__main__':
    run_sunreek()
