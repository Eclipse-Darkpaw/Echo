import discord
import os
import sys
from dotenv import load_dotenv
load_dotenv()

prefix = '>'
cmdlog = 'messages.txt'

game = discord.Game(prefix + "help for commands")
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=game)

guild = None
application_channel = None
verified_role = None
questioning_role = None

async def displayMessage(channel, message):
    if not len(message) > 0:
        return
    return await channel.send(message)

async def readMessage(channel, client, prompt=None, delete_prompt=True,delete_response=True):
    show = await displayMessage(channel, prompt)
    message = await client.wait_for('message',timeout=120.0)
    if delete_response:
        await message.delete()
    if delete_prompt:
        await show.delete()
    return message

async def readLine(channel, client, prompt, target, delete_prompt=True,delete_response=True):
    show = await displayMessage(channel, prompt)

    def check(msg):
        return msg.author != client.user and (msg.author == target or msg.channel == channel)
    msg = await client.wait_for('message',check=check)

    if delete_response:
        await msg.delete()
    if delete_prompt:
        await show.delete()

    return msg

async def readUser(channel, client,key=None, prompt = None):
    await channel.send(prompt)
    while(True):
        msg = await client.wait_for('message',timeout=120.0)
        if msg and msg.content==key and msg.channel == channel:
            return msg.author

async def readInt(channel, client, prompt=None,target=None):
    num = 0
    parsed = False

    while not parsed:
        line = await readLine(channel, client, prompt,target)

        try:
            num = int(line)
            parsed = True
        except:
            await displayMessage(channel, "Thats not a valid number! Try again!")
            parsed = False
    return num

def log(message):
    global cmdlog
    to_log ='[' + str(message.created_at) + '] #' + str(message.channel.name) + ' in ' + str(message.guild.name) + ' \n@'+ str(message.author) + ' said ' + message.content + '\n'
    with open(cmdlog, 'w') as file:
        file.write(to_log)
        file.close()
    print(to_log)

async def help(message):
    global prefix
    """
    Effectively the docutmentation for all methods and functions
    :param message:
    :return:
    """
    command = message.content[len(prefix):].split()
    if len(command) == 1:
        await message.channel.send('`help {command}` - thats this command.\n'
                                   '`repeat [phrase]` - repeats the user input\n'
                                   '***__Moderator Commands__***'
                                   '`quit` - quits the bot\n'
                                   '`ban [member] - bans a member`')
    else:
        pass

counter = 0
questions = ['Where did you get the link from?','How old are you?']
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
        for question in questions:
            question = '<@!' + str(self.applicant.id)  + '> ' + question
            response = await readLine(await self.applicant.create_dm(),client,question,self.applicant,delete_prompt=False,delete_response=False)
            self.responses.append(response.content)

    def gen_embed(self):
        global application_channel
        global questions

        embed = discord.Embed(title='Application #'+str(self.count))
        embed.set_author(name=self.applicant.name,icon_url=self.applicant.avatar_url)
        for i in range(len(questions)):
            embed.add_field(name=questions[i],value=self.responses[i])
        embed.add_field(name='User ID',value=str(self.applicant.id),inline=False)

        return embed

    def __str__(self):
        return 'Application for ' + str(self.applicant) + '\nWhere did you get the link from?'

async def verify(message):
    application = Application(message.author, message.channel, message.guild)
    await message.delete()

    await application.question()

    applied = await application_channel.send(embed=application.gen_embed())
    emojis = ['✅', '❓', '🚫', '❗']
    for emoji in emojis:
        await applied.add_reaction(emoji)

    print('check')
    def check(reaction, user):
        return user != client.user and user.guild_permissions.manage_roles and str(reaction.emoji) in emojis

    print('Waiting for user reaction')
    reaction, user = await client.wait_for('reaction_add',check=check)
    print('user reacted ' + str(user) + str(reaction.emoji))

    if str(reaction.emoji) == '✅':
        await application.applicant.add_roles(message.guild.get_role(int(os.getenv('VERIFIED_ROLE_ID'))))
        await message.author.send('You have been approved.')
    elif str(reaction.emoji) == '❓':
        await application.applicant.add_roles(message.guild.get_role(int(os.getenv('QUESTIONING_ROLE_ID'))))
        await message.author.send('You have been pulled into questioning.')
    elif str(reaction.emoji) == '🚫':
        reason = await readLine(application_channel,client,'Why was this user denied?', user)
        await message.author.send('Your application denied for:' + reason.content)
    elif str(reaction.emoji) == '❗':
        await application.applicant.add_roles(message.guild.get_role(int(os.getenv('SUSPENDED_ID'))))

async def quit(message):
    global game
    if message.author.guild_permissions.administrator:
        print('quitting program')
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await displayMessage(message.channel, 'You do not have permission to turn me off!')

async def warn(message):
    command = message.content[1:].lower().split(' ', 3)
    # take id too
    if message.author.guild_permissions.kick_members:
        target = message.mentions[0]
        if target == None:
            await message.channel.send('null target')
            return
        elif message.author == target:
            await message.channel.send('You cannot warn yourself')
            return

        await message.channel.send(target + ' was not warned. Unable to comply')

    else:
        await message.channel.send('You do not have the permissions to do that.')

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
        await message.channel.send(target + ' was kicked.\n Reason: ' + command[2])
    else:
        await message.channel.send('You do not have the permissions to do that.')

async def ban(message):
    command = message.content[1:].lower().split(' ', 2)
    if message.author.guild_permissions.ban_members or message.author.guild_permissions.administrator:
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

        await target.ban()
        await message.channel.send(target + ' was banned.\n Reason: ' + command[2])
    else:
        await message.channel.send('You do not have the permissions to do that.')

@client.event
async def on_ready():
    global guild
    global application_channel
    global verified_role
    global questioning_role

    print('We have logged in as {0.user}'.format(client))

    guild = client.get_guild(int(os.getenv('GUILD')))
    application_channel = guild.get_channel(int(os.getenv('APPLICATION_CHANNEL_ID')))
    verified_role = guild.get_role(int(os.getenv('VERIFIED_ROLE_ID')))
    questioning_role = guild.get_role(int(os.getenv('QUESTIONING_ROLE_ID')))
    await client.change_presence(activity=game)


@client.event
async def on_message(message):
    global prefix
    global application_channel
    global verified_role
    global questioning_role
    if message.author == client.user:
        return
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        return
    if message.content.startswith(prefix):
        command = message.content[1:].split(' ', 1)
        log(message)
        if command[0] == 'help':
            await message.channel.send('To be worked on')
        elif command[0] == 'test':
            await message.reply('I am online')
        elif command[0] == 'version':
            await message.reply('I am currently running Echo 0.1.1')
        elif command[0] == 'repeat':
            await message.channel.send(command[1])
        elif command[0] == 'quit':
            print('quit command recieved')
            await quit(message)
        elif command[0] == 'verify':
            await verify(message)
        elif command[0] == 'warn':
            await warn(message)
        elif command[0] == 'kick':
            await kick(message)
        elif command[0] == 'ban':
            await ban(message)
        elif command[0] == 'prefix':
            prefix = command[1]
            file = open('main.py', 'r')
            lines = file.readlines()
            file.close()
            lines[4] = 'prefix = ' + prefix + '\n'
            file = open('main.py', 'w')
            file.writelines(lines)
            file.close()
        elif command[0] == 'set':
            application_channel = message.channel
        else:
            pass

@client.event
async def on_member_join(member):
    DM = member.create_DM()
    displayMessage(DM, 'Hello, and welcome to the server! Please read over the rules before verifying yourself!')


print('Starting Bot')
client.run(os.getenv('TEST_TOKEN'))