import discord
import os
import sys
#from keep_alive import keep_alive

prefix = '>'
client = discord.Client()
Eclipse_Darkpaw_ID = int(os.getenv('ECLIPSE_DARKPAW_ID'))
cmdlog = 'messages.txt'
game = discord.Game(prefix + "help for commands")

application_channel = None
new_member_channel = None

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
        async def check(m):
            msg = await client.wait_for('message',timeout=120.0)
        if msg.content==key and msg.channel == channel:
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


print('Starting Bot')
#keep_alive()
client.run(os.getenv('TEST_TOKEN'))