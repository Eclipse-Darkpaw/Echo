import discord
import os
import sys
#from keep_alive import keep_alive

name = None
prefix = None
client = discord.Client()
Eclipse_Darkpaw_ID = int(os.getenv('ECLIPSE_DARKPAW_ID'))
cmdlog = 'messages.txt'

async def displayMessage(channel, message):
    if not len(message) > 0:
        return
    await channel.send(message)

async def readMessage(channel, client, prompt=None):
    await displayMessage(channel, prompt)
    return await client.wait_for('message',timeout=120.0)

async def readLine(channel, client, prompt=None, target=None):
    while(True):
        msg = readMessage(channel, client, prompt)
        if msg.author == client.user or (target != None and msg.author != target.user()):
            continue
        elif msg.channel == channel:
            return msg.content

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
    file = open(cmdlog, 'a')
    file.write('[' + str(message.created_at) + '] #' 
    + str(message.channel.name) + ' in ' 
    + str(message.guild.name) + ' \n@'
    + str(message.author) + ' said ' 
    + message.content + '\n')
    file.close()

def join(message):
    pass

async def help(self, message):
    """
    Effectively the docutmentation for all methods and functions
    :param message:
    :return:
    """
    command = message.content[len(self._prefix):].split()
    if len(command) == 1:
        await message.channel.send('`help {command}` - thats this command.\n'
                                   '`repeat [phrase]` - repeats the user input\n'
                                   '***__Moderator Commands__***'
                                   '`quit` - quits the bot\n'
                                   '`ban [member] - bans a member`')
    else:
        pass

'''
async def verify(self, message):
    application = []
    application.append(message.author)
    application.append(message.channel)
    application.append(message.guild)
    await message.delete()

    await message.channel.send('Where did you get the link from?')
    where = await readMessage(message.channel, client)
    application.append(where.content)
    ''
    Status code
    0 = awaiting approval
    1 = approved
    2 = denied
    3 = Secondary role/questioning
    ''
    status = 0
    application = application_channel.send()
    emojis = ['✅', '❓', '🚫', '❗']
    for emoji in emojis:
        await application.add_reaction(emoji)
    await client.wait_for('reaction')

    def check(reaction):
        return

    reaction = await client.wait_for('reaction_add')
    if str(reaction.emoji) == '✅':
        await application[0].add_roles(application[2].get_role(811522721824374834))
        await application[0].remove_roles(application[2].get_role(612958044132737025))
    elif str(reaction.emoji) == '❓':
        pass
    elif str(reaction.emoji) == '🚫':
        message.channel.send('')
    elif str(reaction.emoji) == '❗':
        pass
'''

#
async def quit(self, message):
    if message.author.guild_permissions.administrator:
        print('quitting program')
        await message.channel.send('Goodbye :wave:')
        sys.exit()
    else:
        await displayMessage(message.channel, 'You do not have permission to turn me off!')

async def warn(self, message):
    command = message.content[1:].lower().split(' ', 3)
    if message.author.guild_permissions.kick_members:
        target = message.mentions[0]
        if target == None:
            await message.channel.send('null target')
            return
        elif message.author == target:
            await message.channel.send('You cannot kick yourself')
            return

        await message.channel.send(target + ' was not warned. Unable to comply')

    else:
        await message.channel.send('You do not have the permissions to do that.')

async def kick(self, message):
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
        try:
            await target.kick(command[2])
            await message.channel.send(target + ' was kicked.\n Reason: ' + command[2])
        except IndexError:
            await target.kick()
            await message.channel.send(str(target) + ' was kicked.')
        else:
            await message.channel.send('An Error occured.')
    else:
        await message.channel.send('You do not have the permissions to do that.')

async def ban(self, message):
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
        try:
            await target.ban(command[2])
            await message.channel.send(target + ' was banned.\n Reason: ' + command[2])
        except:
            await target.ban()
            await message.channel.send(str(target) + ' was banned.')
    else:
        await message.channel.send('You do not have the permissions to do that.')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=game)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        return
    if message.content.startswith(prefix):
        command = message.content[1:].lower().split(' ', 1)
        log(message)
        if command[0] == 'help':
            await help(message)
        elif command[0] == 'test':
            await message.reply('I am online')
        elif command[0] == 'repeat':
            await message.channel.send(command[1])
        elif command[0] == 'quit':
            print('quit command recieved')
            await quit(message)
        elif command[0] == 'verify':
            verify(message)
        elif command[0] == 'warn':
            warn(message)
        elif command[0] == 'kick':
            await kick(message)
        elif command[0] == 'ban':
            await ban(message)
        elif command[0] == 'join':
            join(message)
        elif command[0] == 'prefix':
            prefix = command[1]
            file = open('main.py', 'r')
            lines = file.readlines()
            file.close()
            lines[5] = 'prefix = ' + prefix + '\n'
            file = open('main.py', 'w')
            file.writelines(lines)
            file.close()
        else:
            pass

@client.event
async def on_member_join(member):
    DM = member.create_DM()
    displayMessage(DM, 'Hello, and welcome to the server! Please read over the rules before verifying yourself!')

def export_to_file(name, prefix):
    """
    Exports the bot to a file that can it can be loaded from again

    :return:
    """
    file = open(name + '.bot', 'w')
    lines = [name, prefix]
    file.writelines(lines)
    file.close()

def import_from_file(file_name):
    bot = open(file_name, 'r')
    lines = bot.readlines()
    return lines[0], lines[1]


if __name__ == '__main__':
    print('Starting Bot')
    import_from_file('echo.bot')
    game = discord.Game(prefix + "help for commands")
    #keep_alive()
    client.run(os.getenv('TEST_TOKEN'))
