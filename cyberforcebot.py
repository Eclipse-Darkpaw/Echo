"""
Import statements are crucial statements that allow the bot to run code you didn't create yourself
- The discord module includes all the code that allows the bot to connect to the Discord API
- The sys module allows you to run system commands
- The time module allows you to time how long some task takes
"""
import discord
import sys
import time
import os

# The version number isn't a necessary feature, but it is useful to confirm the bot is running the
# most recent version of the code
version_num = '1.0.1'

# This is the bot prefix. This tells the bot what to look for at the start of a message.
prefix = '>'

# This is the bot Token. It's like the bot's password. DO NOT SHARE THE TOKEN WITH ANYONE.
token = os.getenv('CYBERFORCE_BOT_TOKEN')

# This sets the bot's Activity status. It allows the bot to go into more detail about its current
# status
game = discord.Game('Scanning for pings')

# The client is the bot's discord account. It allows the bot to connect to discord and run commands
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


client = discord.Client(intents=intents)


async def ping(message):
    """
    Returns how long it takes the bot to edit a message, as well as demonstrates the bot can send
    and receive messages
    Last docstring edit: -Autumn V1.0.1
    Last method edit: -Autumn V1.0.0
    :param message: message that called the quit command
    :return: None
    """
    start = time.time()
    x = await message.channel.send('Pong!')
    edit_time = time.time() - start
    edit = x.content + ' ' + str(int(edit_time * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message):
    """
    Returns the current version of the bot. Useful for testing the bot can send and receive messages
    Last docstring edit: -Autumn V1.0.1
    Last method edit: -Autumn V1.0.0
    :param message: message that called the command
    :return: None
    """
    await message.channel.send('I am currently running version ' + version_num)


async def end(message):
    """
    Quits the bot, and closes the program. Replies and updates the game status to alert users to it
    quitting.
    Last docstring edit: -Autumn V1.0.1
    Last method edit: -Autumn V1.0.0
    :param message: message that called the quit command
    :return: None
    """
    global game
    # The global key word tells python to look for the variable outside the function named game
    if message.author.guild_permissions.administrator:  # makes sure the bot is being
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def mama(message):
    await message.channel.send('Drink some water, have a snack, take your meds, and remember Mama Bruise loves you!')


async def microwave(message):
    await message.channel.send('You put Gemini in the microwave for 2 minutes. She comes out nice and warm when you '
                               'hug her')
    await message.channel.send('https://i.imgur.com/eOPKEV4.gif')


async def hug(message):
    await message.channel.send('You give Gemini a hug. You can smell a faint citrus scent when you do.')
# ADD NEW METHODS HERE!


@client.event
async def on_ready():
    """
    Confirms the bot is online, and has started. It prints a message to the command line, and
    changes the bot's Activity status.
    Last docstring edit: -Autumn V1.0.0
    Last method edit: -Autumn V1.0.0
    :return: None
    """
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=game)


'''
The switcher allows you to call a command with out using a large series of if/else statements. Its much easier to
work with when dealing with Strings, like in discord bots, and allows the functions to be called in a much more
efficient way. However, this requires each function to have the same parameters. If you want each function to have
different parameters, you need to handle it in the function.
'''
switcher = {'ping': ping, 'version': version, 'quit': end, 'microwave': microwave, 'hug': hug}
mama_switch = {'mama': mama}


@client.event
async def on_message(message):
    """
    When a message happens, it scans the first character for the bot prefix. If the first character
    is the bot prefix, the bot will attempt to run the command. If the command is in the switcher,
    the command will run and the bot should return an output, and respond in the same channel.
    Last docstring edit: -Autumn V1.0.0
    Last method edit: -Autumn V1.0.0
    :param message: the message that was just sent
    :return: None
    """
    if message.content.startswith(prefix):
        command = message.content[1:].lower().split(' ', 1)
        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            pass
    if message.content.startswith(';'):
        command = message.content[1:].lower().split(' ', 1)
        try:
            method = mama_switch[command[0]]
            await method(message)
        except KeyError:
            pass
        

'''This is what begins the entire bot, and tells the bot to run
THIS LINE MUST BE AT THE END OF THE SCRIPT.
IF THIS LINE IS NOT LAST, ANYTHING AFTER IT WILL NOT LOAD.'''
client.run(token)
