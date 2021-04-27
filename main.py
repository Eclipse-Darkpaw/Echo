import time
import discord
import os
import sys
from dotenv import load_dotenv
from leaderboard import Leaderboard

load_dotenv()

prefix = '>'
cmdlog = 'command.log'
version_num = '1.2.1'

eclipse_id = 440232487738671124

intents = discord.Intents.default()
intents.members = True

game = discord.Game(prefix + "help for commands")
client = discord.Client(intents=intents)

guild = None
application_channel = 813991832593367051
unverified = 813996107126276127
verified_role = 758487413257011271
questioning_role = 813798884173414451
suspended_role = 773401156935352390
warn_roles = [758497391955017728, 758497457444356147, 819264514334654465, 819264556265898044, 819264588339478540]

warn_log_channel = 771519147808653322
join_leave_log = 813794437347147856
cases = 0
mail_inbox = 828862015056379915
rules = None
num_rules = 0
rule_lst = []

ignore = []

most_active = Leaderboard()


async def display_message(channel, message):
    if not len(message) > 0:
        return
    return await channel.send(message)


async def read_message(channel, prompt=None, delete_prompt=True, delete_response=True):
    show = await display_message(channel, prompt)
    message = await client.wait_for('message', timeout=120.0)
    if delete_response:
        await message.delete()
    if delete_prompt:
        await show.delete()
    return message


async def read_line(channel, prompt, target, delete_prompt=True, delete_response=True):
    show = await display_message(channel, prompt)

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


async def read_user(channel, key=None, prompt=None):
    await channel.send(prompt)
    while True:
        msg = await client.wait_for('message', timeout=120.0)
        if msg and msg.content == key and msg.channel == channel:
            return msg.author


async def read_int(channel, prompt=None, target=None):
    num = 0
    parsed = False

    while not parsed:
        line = await read_line(channel, prompt, target)

        try:
            num = int(line)
            parsed = True
        except:
            await channel.send("That's not a valid number! Try again!")
            parsed = False
    return num


def log(message):
    to_log = '[' + str(message.created_at) + 'Z] ' + str(message.guild) + \
             '\n' + message.content + '\n' + \
             'channel ID:' + str(message.channel.id) + ' Author ID:' + str(message.author.id) + '\n\n'
    file = open(cmdlog, 'a')
    file.write(to_log)
    file.close()


counter = 0
questions = ['What is your name?', 'How old are you?', 'Where did you get the link from?', 'Why do you want to join?']


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
        await display_message(dm, 'Please wait while your application is reviewed')

    def gen_embed(self):
        global application_channel
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

    await application.question()

    applied = await guild.get_channel(application_channel).send(embed=application.gen_embed())
    emojis = ['✅', '❓', '🚫', '❗']
    for emoji in emojis:
        await applied.add_reaction(emoji)

    def check(reaction, user):
        return user != client.user and user.guild_permissions.manage_roles and str(reaction.emoji) in emojis

    reaction, user = await client.wait_for('reaction_add', check=check)

    if str(reaction.emoji) == '✅':
        await application.applicant.add_roles(guild.get_role(verified_role))
        await message.author.send('You have been approved.')
        await application.applicant.remove_roles(guild.get_role(questioning_role))
        await application.applicant.remove_roles(guild.get_role(unverified))
    elif str(reaction.emoji) == '❓':
        await application.applicant.add_roles(guild.get_role(questioning_role))
        await message.author.send('You have been pulled into questioning.')
    elif str(reaction.emoji) == '🚫':
        reason = await read_line(guild.get_channel(application_channel), 'Why was this user denied?', user, delete_prompt=False, delete_response=False)
        await message.author.send('Your application denied for:\n> ' + reason.content)
    elif str(reaction.emoji) == '❗':
        await application.applicant.add_roles(guild.get_role(suspended_role))
        await guild.get_channel(application_channel).send('Member Suspended')


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
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        print('quitting program')
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def restart(message):
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        os.execv(__file__, sys.argv)
    else:
        await message.channel.send('You do not have permission to turn me off!')


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
        # if message.author == target:
        # await message.channel.send('You cannot kick yourself')
        # return
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
    embed = discord.Embed(title="Echo Command list", color=0x45FFFF)
    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embed.add_field(name='`>help`', value="That's this command!", inline=False)
    embed.add_field(name='`>verify`', value='Verifies an un verified member.', inline=False)
    embed.add_field(name='`>modmail`', value='Sends a private message to the moderators.', inline=False)
    embed.add_field(name='`>test`', value='Tests if the bot is online', inline=False)
    embed.add_field(name='`>version_num`', value='What version_num Echo is currently on')
    embed.add_field(name='Moderator Commands', value='Commands that only mods can use', inline=False)
    embed.add_field(name='`>warn <MemberTagged> <rule#> [reason]`', value='Warns a member for a rule and logs it',
                    inline=False)
    embed.add_field(name='`>kick <MemberTagged> <rule#> [reason]`', value='Kicks a member for a rule and logs it',
                    inline=False)
    embed.add_field(name='`>ban <MemberTagged> <rule#> [reason]`', value='Bans a member for a rule and logs it.',
                    inline=False)
    embed.add_field(name='`>quit`', value='quits the bot', inline=False)
    await message.channel.send(embed=embed)


# TODO: make a separate rule class
async def rule(message):
    pass


async def rule_new(rule):
    global num_rules

    num_rules += 1
    rule = str(num_rules) + '. ' + rule
    id = await rules.send(rule).id
    rule_lst.append(id)


async def rule_edit(rule, new_wording):
    message = rules.get_message(rule_lst[rule - 1])
    number = message.content.split('. ', 1)[0]
    await message.edit(number + '. ' + new_wording)


async def rule_delete(rule):
    global num_rules

    num_rules -= 1
    await rules.get_message(rule_lst[rule - 1]).delete()
    for i in range(rule, len(rule_lst)):
        message = rules.get_message(rule_lst[i - 1])
        number = message.content.split('. ', 1)
        await message.edit(str(int(number[0]) - 1) + '. ' + number[1])


async def leaderboard(message):
    command = message.content[1:].split(' ', 2)
    if not message.author.guild_permissions.administrator:
        await message.channel.send('Insufficient permissions.')
    elif command[1] == 'show':
        await most_active.show_leaderboard(message)
    elif command[1] == 'reset':
        await most_active.reset_leaderboard(message)

profiles = []
async def display_profile(member, channel, profile):

    embed = discord.Embed(title=member)
    embed.set_author(name=member.name, icon_url=member.avatar_url)

    embed.add_field(name='Bio', value=profile.bio, inline=False)
    embed.add_field(name='Join Date', value=member.joined_at)

    await channel.send(embed=embed)


async def edit_profile(member, new_bio):
    if len(new_bio) > 1024:
        raise RuntimeError('Field value exceeds maximum len')

    file_name = str(member.id) + '/.profile'
    with open(file_name) as file:
        lines = file.readLines()


async def profile(message):
    command = message.content[1:].split(' ', 2)
    if len(command) == 1:
        await display_profile(message.author, message.channel)
    elif command[1] == 'edit':
        edit_profile(message.author)


@client.event
async def on_connect():
    print('Connected to Discord!')


@client.event
async def on_disconnect():
    print('Disconnected from Discord')


@client.event
async def on_ready():
    global guild
    print('We have logged in as {0.user}'.format(client))

    guild = client.get_guild(758472902197772318)
    await client.change_presence(activity=game)

    await guild.get_member(eclipse_id).send('Running, and active')
    print('All ready to run!')


switcher = {'help': help, 'ping': ping, 'version_num': version_num, 'verify': verify, 'modmail': modmail, 'warn': warn,
            'kick': kick, 'ban': ban, 'quit': quit, 'leaderboard': leaderboard, 'profile': profile, 'restart': restart}


@client.event
async def on_message(message):
    global application_channel
    global verified_role
    global questioning_role
    global most_active

    if message.author.bot:
        return
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        return
    if len(message.content) < 3 or message.content[1] == ' ':
        return
    if message.content.startswith(prefix):
        command = message.content[1:].split(' ', 1)

        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            await message.channel.send("That's not a valid command")
        if command[0] == 'print':
            print('/n/n/n/n'+message.content)
        '''
        elif command[0] == 'rule':
            command = message.content.split(' ',2)
            if command[1] == 'new':
                await rule_new(command[2])
            elif command[1] == 'edit':
                rule = command[2].split(' ',1)
                await rule_edit(rule[0], rule[1])
            elif command[1] == 'delete':
                await rule_delete(int(command[2]))
        elif command[0] == 'print':
            print(message.content)
        '''

    #leaderboard.score(message)


@client.event
async def on_member_join(member):
    file = open('join-leave.log', 'a')
    file.write('->' + str(member.name))
    await member.send('Hello, and welcome to the server! Please read over the rules before verifying yourself!')
    embed = discord.Embed(title='Member Join')
    embed.set_author(name=member.name, icon_url=member.avatar_url)
    age = str(member.created_at)
    embed.set_footer(text=str(member.id))
    await join_leave_log.send(embed=embed)


@client.event
async def on_member_remove(member):
    filename = member.id + '/.profile'
    with open(filename) as file:
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


token = os.getenv('TOKEN')
client.run(token)
