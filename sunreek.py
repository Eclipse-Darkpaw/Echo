import time
import discord
import os
import sys
from dotenv import load_dotenv
from leaderboard import Leaderboard
from profile import display_profile, set_bio
from fileManagement import joinleave_path, profile_path
from refManagement import ref, set_ref, add_ref
from main import read_line

load_dotenv()
start_time = time.time()
# todo: add uptime feature
# todo: add a master prefix only applicable to you as a back door

prefix = '}'
cmdlog = 'command.log'
version_num = '1.8.7'

eclipse_id = 440232487738671124

intents = discord.Intents.default()
intents.members = True

game = discord.Game(prefix + "help for commands")
client = discord.Client(intents=intents)

guild = None
application_channel = 819223217281302598   # channel where finished applications go
unverified = 612958044132737025
verified_role = 811522721824374834         # role to assign members who verify successfully
questioning_role = 819238442931716137      # Role to assign when users
mail_inbox = 840753555609878528            # modmail inbox channel

counter = 0
questions = ['Password?', 'What is your name?', 'How old are you?', 'Where did you get the link from? Please be specific. If it was a user, please use the full name and numbers(e.g. Echo#0109)', 'Why do you want to join?']


class Application:
    def __init__(self, applicant, channel, guild):
        global counter
        counter += 1
        self.applicant = applicant
        self.channel = channel
        self.guild = guild
        self.count = counter
        self.responses = []

    async def question(self):
        global questions
        global client
        dm = await self.applicant.create_dm()
        for question in questions:
            question = '<@!' + str(self.applicant.id) + '> ' + question
            response = await read_line(client, dm, question, self.applicant, delete_prompt=False, delete_response=False)
            self.responses.append(response.content)
        await dm.send('Please wait while your application is reviewed')

    def gen_embed(self):
        global questions

        embed = discord.Embed(title='Application #' + str(self.count))
        embed.set_author(name=self.applicant.name, icon_url=self.applicant.avatar_url)
        for i in range(len(questions)):
            embed.add_field(name=questions[i], value=self.responses[i])
        embed.add_field(name='User ID', value=str(self.applicant.id), inline=False)

        return embed

    def __str__(self):
        return 'Application for ' + str(self.applicant) + '\nWhere did you get the link from?'


async def verify(message):
    guild = message.guild

    if verified_role in message.guild.get_member(message.author.id).roles:
        await message.channel.send('You are already verified')
        return
    try:
        applicant = guild.get_member(message.author.id)
        application = Application(applicant, message.channel, message.guild)
        channel = guild.get_channel(application_channel)
    except discord.errors.Forbidden:
        message.reply('I cannot send you a message. Change your privacy settings in User Settings->Privacy & Safety')
        return

    await application.question()

    applied = await channel.send(embed=application.gen_embed())
    emojis = ['✅', '❓', '🚫', '❗']
    for emoji in emojis:
        await applied.add_reaction(emoji)

    def check(reaction, user):
        return user != client.user and user.guild_permissions.manage_roles and str(reaction.emoji) in emojis and reaction.message == applied

    while True:
        reaction, user = await client.wait_for('reaction_add', check=check)
        # TODO: allow multiple mods to react at once
        if str(reaction.emoji) == '✅':
            await application.applicant.add_roles(guild.get_role(verified_role))
            await message.author.send('You have been approved.')
            await application.applicant.remove_roles(guild.get_role(questioning_role))
            await application.applicant.remove_roles(guild.get_role(unverified))
            await channel.send('<@!'+str(message.author.id)+'> approved')
            break
        elif str(reaction.emoji) == '❓':
            await application.applicant.add_roles(guild.get_role(questioning_role))
            await channel.send('<@!'+str(message.author.id)+'>  is being questioned')
            await message.author.send('You have been pulled into questioning.')
        elif str(reaction.emoji) == '🚫':
            reason = await read_line(client, guild.get_channel(application_channel), 'Why was this user denied?', user,
                                     delete_prompt=False, delete_response=False)
            await message.author.send('Your application denied for:\n> ' + reason.content)
            await channel.send('<@!'+str(message.author.id)+'> was denied for:\n> '+reason.content)
            break
        elif str(reaction.emoji) == '❗':
            reason = await read_line(client, guild.get_channel(application_channel), 'Why was this user banned?', user,
                                     delete_prompt=False, delete_response=False)
            reason = reason.content
            if reason == 'cancel':
                await channel.send('Ban cancelled')

            else:
                try:
                    await message.guild.ban(user=application.applicant,reason=reason)
                    await channel.send('<@{}> banned for\n> {}'.format(message.author.id, reason))
                    break
                except discord.HTTPException:
                    await channel.send('Ban failed. Please try again, by reacting to the message again.')
                except discord.Forbidden:
                    await channel.send('Error 403: Forbidden. Insufficient permissions.')


async def ping(message):
    # log(message)
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message):
    # log(message)
    await message.channel.send('I am currently running version ' + version_num)


async def quit(message):
    global game
    # log(message)
    # await save(message)
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def restart(message):
    # log(message)
    # await save(message)
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        os.execl(sys.executable,__file__,'main.py')
    else:
        await message.channel.send('You do not have permission to turn me off!')

# May remove depending on needs
'''
async def suspend(message):
    command = message.content[1:].lower().split(' ', 2)
    if message.author.guild_permissions.ban_members or message.author.guild_permissions.administrator:
        target = message.mentions[0]
        print(target)
        if target == None:
            await message.channel.send('No target')
            return
        if message.author == target:
            await message.channel.send('You cannot suspend yourself')
            return
        elif client.user == target:
            await message.channel.send('You cannot suspend me!')
            return
        if len(command) == 2:
            command.append('No reason given.')

        await target.add_roles(message.guild.get_role(suspended_role))
        await message.channel.send(target + ' was suspended.\n Reason: ' + command[2])
        await target.add_roles()
        embed = discord.Embed(title='Suspension | Case #' + str(cases))
        embed.set_author(name=target.name, icon_url=target.avatar_url)
        embed.add_field(name='Rule broken', value=str(command[2]))
        embed.add_field(name='Comments', value=str(command[3]))
        embed.add_field(name='User ID', value=str(target.id), inline=False)
        await warn_log_channel.send(embed=embed)
        reason = str(target) + ' suspended for ' + command[3]
        await message.channel.send(reason)
    else:
        await message.channel.send('You do not have the permissions to do that.')
    pass
'''


async def kick(message):
    command = message.content[1:].lower().split(' ', 2)
    if message.author.guild_permissions.kick_members:
        target = message.mentions[0]
        print(target)
        if target == None:
            await message.channel.send('null target')
            return
        if message.author == target:
            await message.channel.send('You cannot kick yourself')
            return
        elif client.user == target:
            await message.channel.send('You cannot kick me like this!')
            return
        if len(command) == 2:
            command.append('No reason given')
            await target.kick(command[2])
        embed = discord.Embed(title='Kick')
        embed.set_author(name=target.name, icon_url=target.avatar_url)
        embed.add_field(name='Rule broken', value=str(command[2]))
        embed.add_field( name='Comments', value=str(command[3]))
        embed.add_field(name='User ID', value=str(target.id), inline=False)
        await message.guild.get_channel(819234197063467058).send(embed=embed)
        reason = str(target) + ' kicked for ' + command[3]
        await message.channel.send(reason)
    else:
        await message.channel.send('You do not have the permissions to do that.')


async def ban(message):
    command = message.content[1:].lower().split(' ', 2)
    if message.author.guild_permissions.ban_members:
        target = message.mentions[0]
        print(target)
        if target == None:
            await message.channel.send('No target')
            return
        if message.author == target:
            await message.channel.send('You cannot ban yourself')
            return
        elif client.user == target:
            await message.channel.send('You cannot ban me like this!')
            return
        if len(command) == 2:
            command.append('No reason given.')
        await target.ban(command[2])
        embed = discord.Embed(title='Banned')
        embed.set_author(name=target.name, icon_url=target.avatar_url)
        embed.add_field(name='Rule broken', value=str(command[2]))
        embed.add_field(name='Comments', value=str(command[3]))
        embed.add_field(name='User ID', value=str(target.id), inline=False)
        await message.guild.get_channel(819234197063467058).send(embed=embed)
        reason = str(target) + ' banned for ' + command[3]
        await message.channel.send(reason)
        await message.channel.send(target + ' was banned.\n Reason: ' + command[2])
    else:
        await message.channel.send('You do not have the permissions to do that.')

'''
async def warn(message):
    global cases

    try:
        command = message.content[1:].lower().split(' ', 3)
    except:
        await message.channel.send('Improper formatting. Use `>warn <Member/ID> <rule> [reason]`')
        return

    # warn <member> <rule> reason
    # take id too
    perms = message.author.guild_permissions
    if perms.kick_members and perms.manage_roles and perms.ban_members:
        target = message.mentions[0]
        if target is None:
            await message.channel.send('null target')
            return
        elif message.author == target:
            await message.channel.send('You cannot warn yourself')
            return
        cases += 1

        if not command[3]:
            command[3] = 'No reason given'
        for role in warn_roles:
            if role not in target.roles:
                await target.add_roles(role)
                if role == warn_roles[2]:
                    await suspend(message)
                    return
                elif role == warn_roles[3]:
                    await kick(message)
                    return
                elif role == warn_roles[4]:
                    await ban(message)
                    return
                else:
                    embed = discord.Embed(title='Warn | Case #' + str(cases))
                    embed.set_author(name=target.name, icon_url=target.avatar_url)
                    embed.add_field(name='Rule broken', value=str(command[2]))
                    embed.add_field(name='Comments', value=str(command[3]))
                    embed.add_field(name='User ID', value=str(target.id), inline=False)
                    await warn_log_channel.send(embed=embed)
                    reason = str(target) + ' warn for ' + command[3]
                    await message.channel.send(reason)
                    return
    else:
        await message.channel.send('You do not have the permissions to do that.')


async def mute(message):
    target = get_user_id(message)
    await message.guild.get_member(target).add_roles(message.guild.get_role(813806878403461181))
    await message.channel.send(content='<@!'+target+'> was muted.' '',file=open('resources\\mute.jpg','rb')'')
'''


async def modmail(message):
    sender = message.author
    dm = await sender.create_dm()
    subject = await read_line(client, dm, 'Subject Line:', sender, delete_prompt=False, delete_response=False)
    subject = 'Modmail | ' + subject.content
    body = await read_line(client, dm, 'Body:', sender, delete_prompt=False, delete_response=False)
    await dm.send('Your message has been sent')

    mail = discord.Embed(title=subject, color=0xadd8ff)
    mail.set_author(name=sender.name, icon_url=sender.avatar_url)
    mail.add_field(name='Message', value=body.content)
    await guild.get_channel(mail_inbox).send(embed=mail)


async def help(message):
    # square brackets are optional arguments, angle brackets are required
    command = message.content[1:].split(' ')
    if len(command) == 1:
        embed = discord.Embed(title="SunReek Command list", description='Square brackets are optional arguments. Angle brackets are required arguments', color=0x45FFFF)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        embed.add_field(name='`'+prefix+'help`', value="That's this command!", inline=False)
        embed.add_field(name='`'+prefix+'verify`', value='Verifies an un verified member.', inline=False)
        embed.add_field(name='`'+prefix+'modmail`', value='Sends a private message to the moderators.', inline=False)
        embed.add_field(name='`'+prefix+'version_num`', value='What version the bot is currently on', inline=False)
        embed.add_field(name='`'+prefix+'profile [member tag/member id]/[edit]`', value="Gets a tagged user's profile or your profile", inline=False)
        embed.add_field(name='`'+prefix+'ref [member tag/member id]`', value="gets a user's ref sheet", inline=False)
        embed.add_field(name='`'+prefix+'setref <attachment>`', value="Sets a user's ref. Overwrites all current ref data", inline=False)
        embed.add_field(name='`'+prefix+'addref <attachment>`', value="Adds another ref to your file.", inline=False)
        embed.add_field(name='`'+prefix+'crsdky [arguments]`', value='commands for the CursedKeys game. will show the list of cursed keys if argument is left off', inline=False)
        embed.add_field(name='Moderator Commands', value='Commands that only mods can use', inline=False)
        embed.add_field(name='`'+prefix+'quit`', value='quits the bot', inline=False)
        await message.channel.send(embed=embed)
    elif command[1] == 'help':
        help_embed = discord.Embed(title="SunReek Command list", color=0x45FFFF)
        help_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        help_embed.add_field(name='`' + prefix + 'help [bot command]`', value="That's this command!", inline=False)
        await message.channel.send(embed=help_embed)
    elif command[1] == 'profile':
        profile_embed = discord.Embed(title='Profile Command list',description='Displays a users profile', color=0x45FFFF,)
        profile_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        profile_embed.add_field(name='No argument', value='Displays your profile', inline=False)
        profile_embed.add_field(name='`User ID/Tagged User/Nickname`', value='Searches for a user\'s profile. Tagging the desired user, or using their member ID yeilds the most accurate results.', inline=False)
        profile_embed.add_field(name='`edit <string>`', value='Changes your profile to say what you want. Only emotes from this server can be used.', inline=False)
        await message.channel.send(embed=profile_embed)
    elif command[1] == 'crsdky':
        crsdky_embed = discord.Embed(title="`}crsdky Command list", color=0x45FFFF)
        crsdky_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        crsdky_embed.add_field(name='Notes', value='Used by going `}crsdky [argument]`, ', inline=False)
        crsdky_embed.add_field(name='`join`', value='Joins the game of crsdky. Users cannot join after the game starts.', inline=False)
        crsdky_embed.add_field(name='`leave`', value='leaves the game of crsdky', inline=False)
        crsdky_embed.add_field(name='`numleft`', value='Shows the number of players left.', inline=False)
        await message.channel.send(embed=crsdky_embed)
        if message.author.guild_permissions.manage_roles:
            mod_crsdky_embed = discord.Embed(title='`}crsdky` Mod Commands',color=message.author.color)
            mod_crsdky_embed.add_field(name='Notes', value='All these commands require the user to have moderator permissions.', inline=False)
            mod_crsdky_embed.add_field(name='`set <char list>`', value='Sets the cursed keys. Takes lowercase letters and symbols.', inline=False)
            mod_crsdky_embed.add_field(name='`start`', value='Starts the round, and prevents new players from joining', inline=False)
            mod_crsdky_embed.add_field(name='`stop`', value='Pauses the round until the `start` command is recieved', inline=False)
            mod_crsdky_embed.add_field(name='`resetPlayer`', value='Removes all players from the game', inline=False)
            await message.channel.send(embed=mod_crsdky_embed)
    elif command[1] == 'ref':
        ref_embed = discord.Embed(title='`'+prefix+'ref` Command List', description='Displays a users primary ref.', color=0x45FFFF)
        ref_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        ref_embed.add_field(name='No argument', value='Displays your ref', inline=False)
        ref_embed.add_field(name='`User ID/Tagged User/Nickname`', value='Searches for a user\'s profile. Tagging the desired user, or using their member ID yeilds the most accurate results.', inline=False)
        ref_embed.add_field(name='`set <string/ref>`', value='Changes your ref to say what you want. Only emotes from this server can be used.', inline=False)
        await message.channel.send(embed=profile_embed)



'''# TODO: Implement a switch case
async def leaderboard(message):
    command = message.content[1:].split(' ', 2)
    if not message.author.guild_permissions.administrator:
        await message.channel.send('Insufficient permissions.')
    elif len(command) == 1 or command[1] == 'show':
        await most_active.show_leaderboard(message)
    elif command[1] == 'reset':
        await most_active.reset_leaderboard(message)
    elif command[1] == 'save':
        most_active.save_leaderboard(message)
    elif command[1] == 'load':
        most_active.load_leaderboard(message)
    elif command[1] == 'award':
        await most_active.award_leaderboard(message)
'''


async def profile(message):
    command = message.content.split(' ', 2)
    if len(command) == 1:
        await display_profile(message)
    elif command[1] == 'edit':
        try:
            set_bio(str(message.author.id), command[2])
            await message.channel.send('Bio set')
        except Exception:
            await message.channel.send('Error. Bio not set, please use ASCII characters and custom emotes.')
    else:
        await display_profile(message)

cursed_keys_running = False
crsd_keys = []
player_role_id = 863630913686077450


async def cursed_keys(message):
    global cursed_keys_running
    global player_num
    global crsd_keys

    command = message.content[1:].split(' ', 2)
    if len(command) == 1:
        if len(crsd_keys) == 0:
            await message.reply('there are no cursed keys')
        else:
            await message.reply('cursed keys are: '+str(crsd_keys))
    elif command[1] == 'join':
        # either by command or by some other mechanism
        if not cursed_keys_running:
            if message.guild.get_role(player_role_id) in message.author.roles:
                await message.reply('You are already a part of this game!')
            else:
                await message.author.add_roles (message.guild.get_role(player_role_id))
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
        await message.reply('Cursed Keys set: '+ str(crsd_keys))
    elif command[1] == 'start':
        if message.author.guild_permissions.manage_roles:
            cursed_keys_running = True
            if len(crsd_keys) == 0:
                await message.reply('Unable to start game! No Cursed Keys set!')
            else:
                await message.reply('<@&863630913686077450> The game is starting! Cursed Keys are ' + str(crsd_keys))
        else:
            await message.reply('Invalid permissions')
    elif command[1] == 'auto-enroll':
        if message.author.guild_permissions.manage_roles:
            if command[2] == all:
                for member in message.guild.members:
                    await member.add_roles(player_role_id)
            else:
                roles = message.role_mentions
                for role in roles:
                    for member in role.members:
                        await member.add_roles(player_role_id)
                await message.reply('members added')
        else:
            await message.reply('invalid permissions')
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


@client.event
async def on_ready():
    global guild

    print('We have logged in as {0.user}'.format(client))

    guild = client.get_guild(840181552016261170)
    await client.change_presence(activity=game)
    await guild.get_member(eclipse_id).send('Running, and active')


switcher = {'help': help, 'ping': ping, 'version_num': version, 'verify': verify, 'modmail': modmail,'quit': quit,
            'profile': profile, 'restart': restart, 'setref': set_ref, 'ref': ref, 'kick':kick, 'ban':ban,
            'addref': add_ref, 'crsdky': cursed_keys}


@client.event
async def on_message(message):
    global cursed_keys_running
    global application_channel
    global verified_role
    global questioning_role
    global most_active

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
    elif cursed_keys_running:
        if message.guild.get_role(player_role_id) in message.author.roles:
            for key in crsd_keys:
                if key in message.content.lower():
                    await message.author.remove_roles(message.guild.get_role(player_role_id))
                    await message.reply('You have been cursed for using the key: ' + key)
                    if len(message.guild.get_role(player_role_id).members) == 1:
                        cursed_keys_running = False
                        await message.channel.send('<@!' + str(message.guild.get_role(player_role_id).members[0].id) + '> wins the game!')
                    break



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

token = os.getenv('SUNREEK')
client.run(token)
'''RNG base on a string a human creates then converts each word into an int by using its position on the list of words.
add each int and mod '''