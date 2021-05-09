import time
import discord
import os
import sys
from dotenv import load_dotenv
from leaderboard import Leaderboard
from profile import display_profile, set_bio
from fileManagement import ref_path, joinleave_path, profile_path
'''TODO:
* move member_leave.log to a separate file
* move command.log to a separate file
* update to not use .env file
* move leaderboard out of project files'''
load_dotenv()

prefix = '}'
cmdlog = 'command.log'
version_num = '1.4.4'

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
suspended_role =  None       # role to suspend users
'''
warn_roles = [758497391955017728, 758497457444356147, 819264514334654465, 819264556265898044, 819264588339478540]
warn_log_channel = 771519147808653322      # channel to log warns
join_leave_log = 813794437347147856        # channel to log member join and leave
'''
mail_inbox = 840753555609878528            # modmail inbox
# ignore = []

# most_active = Leaderboard()  # Deactivated for Riko's server


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
    to_log = '[' + str(message.created_at) + 'Z] ' + str(message.guild) + \
             '\n' + message.content + '\n' + \
             'channel ID:' + str(message.channel.id) + ' Author ID:' + str(message.author.id) + '\n\n'
    with open(cmdlog, 'a') as file:
        file.write(to_log)

'''
async def save(message):
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        msg = await message.channel.send('Saving')
        most_active.save_leaderboard(message)
        await msg.edit(content='Saved!')


async def load(message, guild=message.guild):
    if message.author.id == eclipse_id or message.author.guild_permissions.administrator:
        msg = await message.channel.send('Loading')
        most_active.load_leaderboard(message)
        await msg.edit(content='Done')
'''

counter = 0
questions = ['Password?','What is your name?', 'How old are you?', 'Where did you get the link from? Please be specific. If it was a user, please use the full name and numbers(e.g. Echo#0109)', 'Why do you want to join?']


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
            response = await read_line(dm, question, self.applicant, delete_prompt=False, delete_response=False)
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
    log(message)
    if verified_role in guild.get_member(message.author.id).roles:
        await message.channel.send('You are already verified')
        return
    applicant = guild.get_member(message.author.id)
    application = Application(applicant, message.channel, message.guild)
    channel = guild.get_channel(application_channel)

    await application.question()

    applied = await channel.send(embed=application.gen_embed())
    emojis = ['✅', '❓', '🚫']
    for emoji in emojis:
        await applied.add_reaction(emoji)

    def check(reaction, user):
        return user != client.user and user.guild_permissions.manage_roles and str(reaction.emoji) in emojis

    while True:
        reaction, user = await client.wait_for('reaction_add', check=check)

        if str(reaction.emoji) == '✅':
            await application.applicant.add_roles(guild.get_role(verified_role))
            await message.author.send('You have been approved.')
            await application.applicant.remove_roles(guild.get_role(questioning_role))
            await application.applicant.remove_roles(guild.get_role(unverified))
            await channel.send('Member approved')
            break
        elif str(reaction.emoji) == '❓':
            await application.applicant.add_roles(guild.get_role(questioning_role))
            await channel.send('Member is being questioned')
            await message.author.send('You have been pulled into questioning.')
        elif str(reaction.emoji) == '🚫':
            reason = await read_line(guild.get_channel(application_channel), 'Why was this user denied?', user, delete_prompt=False, delete_response=False)
            await message.author.send('Your application denied for:\n> ' + reason.content)
            await channel.send('Member was denied for:\n> '+reason.content)
            break


async def ping(message):
    log(message)
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message):
    log(message)
    await message.channel.send('I am currently running Echo ' + version_num)


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

# May remove depending on needs
''' Removed for Riko's Server
async def suspend(message):
    command = message.content[1:].lower().split(' ', 2)
    if message.author.guild_permissions.ban_members or message.author.guild_permissions.administrator:
        target = message.mentions[0]
        print(target)
        if target == None:
            await message.channel.send('null target')
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
        embed = discord.Embed(title='Warn & Kick | Case #' + str(cases))
        embed.set_author(name=target.name, icon_url=target.avatar_url)
        embed.add_field(name='Rule broken', value=str(command[2]))
        embed.add_field(name='Comments', value=str(command[3]))
        embed.add_field(name='User ID', value=str(target.id), inline=False)
        await warn_log_channel.send(embed=embed)
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
            await message.channel.send('null target')
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
        embed = discord.Embed(title='Banned | Case #' + str(cases))
        embed.set_author(name=target.name, icon_url=target.avatar_url)
        embed.add_field(name='Rule broken', value=str(command[2]))
        embed.add_field(name='Comments', value=str(command[3]))
        embed.add_field(name='User ID', value=str(target.id), inline=False)
        await warn_log_channel.send(embed=embed)
        reason = str(target) + ' banned for ' + command[3]
        await message.channel.send(reason)
        await message.channel.send(target + ' was banned.\n Reason: ' + command[2])
    else:
        await message.channel.send('You do not have the permissions to do that.')


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
    subject = await read_line(dm, 'Subject Line:', sender, delete_prompt=False, delete_response=False)
    subject = 'Modmail | ' + subject.content
    body = await read_line(dm, 'Body:', sender, delete_prompt=False, delete_response=False)
    await dm.send('Your message has been sent')

    mail = discord.Embed(title=subject, color=0xadd8ff)
    mail.set_author(name=sender.name, icon_url=sender.avatar_url)
    mail.add_field(name='Message', value=body.content)
    await mail_inbox.send(embed=mail)


async def help(message):
    embed = discord.Embed(title="SunReek Command list", color=0x45FFFF)
    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embed.add_field(name='`>help`', value="That's this command!", inline=False)
    embed.add_field(name='`>verify`', value='Verifies an un verified member.', inline=False)
    embed.add_field(name='`>modmail`', value='Sends a private message to the moderators.', inline=False)
    embed.add_field(name='`>test`', value='Tests if the bot is online', inline=False)
    embed.add_field(name='`>version_num`', value='What version the bot is currently on')
    embed.add_field(name='`>profile [member tag/member id]/[edit]`', value="Gets a tagged user's profile or your profile")
    embed.add_field(name='`>edit`', value='Saves all important files')
    embed.add_field(name='`>ref [member tag/member id]`', value="gets a user's ref sheet")
    embed.add_field(name='`>set_ref`', value="Sets a user's ref")

    embed.add_field(name='Moderator Commands', value='Commands that only mods can use', inline=False)
    embed.add_field(name='`>quit`', value='quits the bot', inline=False)
    await message.channel.send(embed=embed)

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
    command = message.content[1:].split(' ', 2)
    if len(command) == 1:
        await display_profile(message)
    elif command[1] == 'edit':
        set_bio(str(message.author.id), command[2])
        await message.channel.send('Bio set')
    else:
        if len(command[1]) <= 18:
            target = message.guild.get_member(int(command[1]))
        else:
            target = message.mentions[0]
        await display_profile(message, target)


async def set_ref(message):
    try:
        ref_sheet = message.attachments[0]
        path = ref_path(message.author.id)
        await ref_sheet.save(fp=path)
        file = await ref_sheet.to_file()
        await message.channel.send(content='Ref set!')
    except IndexError:
        await message.channel.send('No ref_sheet attached!')


async def ref(message):
    command = message.content.split()
    try:
        if len(command) == 1:
            target = message.author.id
        elif len(command[1]) == 18:
            target = int(command[1])
        elif len(command[1]) == 21:
            target = int(command[2:-2])
        elif len(command[1]) == 22:
            target = int(command[3:-2])
        else:
            await message.channel.send('Not a valid user!')
            return
    except ValueError:
        await message.channel.send('Invalid user')
        return
    try:
        ref_sheet = open(ref_path(target), 'rb')
        file = discord.File(ref_sheet)
        await message.channel.send(file=file)
    except FileNotFoundError:
        await message.channel.send('User has not set their ref.')


@client.event
async def on_ready():
    global guild

    print('We have logged in as {0.user}'.format(client))

    guild = client.get_guild(612550152514961408)
    await client.change_presence(activity=game)
    await guild.get_member(eclipse_id).send('Running, and active')


switcher = {'help': help, 'ping': ping, 'version_num': version, 'verify': verify, 'modmail': modmail,
            'quit': quit, 'profile': profile, 'restart': restart, 'setref': set_ref, 'ref': ref}


@client.event
async def on_message(message):
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
    # most_active.score(message)
    # todo: add a warn check feature to see when a warn can be removed

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