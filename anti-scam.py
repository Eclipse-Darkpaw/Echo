import os

import discord
import modules.AntiScam as AntiScam
import modules.General as General
import modules.ServerSettings as Settings
import modules.Verification as Verif
import sys
import time

from main import read_line
from refbot import profile
from refManagement import ref, set_ref, add_ref, oc, random_ref

version_num = '3.3.0'

prefix = '>'

eclipse_id = 440232487738671124

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

game = discord.Game(prefix + "help for commands")
client = discord.Client(intents=intents)


async def verify(message):
    """
    The method that primarily handles member verification. All members must verify from this method. Sends DM to user,
    asks user questions, then sends answers to the moderators in a designated chat
    Last docstring edit: -Autumn V2.1.0
    Last method edit: -Autumn V3.3.0
    :param message: Discord message calling the method
    :return: NoneType
    """
    await Verif.verify(message, client)


async def setup(message):
    """
    Sets up a server for the bot to run
    Last docstring edit: -Autumn V3.3.0
    Last method edit: -Autumn V3.3.0
    :param message: message that called the bot
    :return:
    """
    await Settings.setup(message, client)

async def ping(message):
    """
    Returns how long it takes the bot to send a message
    Last docstring edit: -Autumn V1.2.2
    Last method edit: -Autumn V3.3.0
    :param message: message that called the quit command
    :return: None
    """
    await General.ping(message)


async def version(message):
    """
    Returns the current version of the bot
    Last docstring edit: -Autumn V1.2.2
    Last method edit: -Autumn V3.3.0
    :param message: message that called the command
    :return: None
    """
    await General.version(message, version_num)


async def quit(message):
    """
    Quits the bot, and closes the program. Replys and updates the game status to alert users to it quitting.
    :param message: message that called the quit command
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :return: N/A. program closes
    """
    await General.quit(message, client)


@client.event
async def on_ready():
    """
    Confirms the bot is online, and has started
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :return: N/A
    """
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=game)
    await client.get_user(eclipse_id).send('Ready and Active')


switcher = {'ping': ping, 'version': version, 'quit': quit, 'profile': profile, 'ref': ref, 'setref': set_ref,
            'addref': add_ref, 'oc': oc, 'random_ref': random_ref, 'randomref': random_ref, 'rr': random_ref,
            'setup':setup, 'verify': verify}


@client.event
async def on_message(message):
    """
    When a message happens, it scans the message for
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :param message: the message sent
    :return: n/a
    """

    if message.author.bot:
        return
    
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        if not message.author.guild_permissions.mention_everyone:
            await AntiScam.scan_message(message)
    content = message.content.lower()

    if message.guild is None or content.find(AntiScam.code) != -1 or message.author.guild_permissions.administrator:
        pass
    else:
        await AntiScam.scan_message(message, client)

    if message.content.startswith(prefix):
        command = message.content[1:].lower().split(' ', 1)
        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            pass
        if command[0] == 'print':
            print(message.content)


def run_antiscam():
    if len(sys.argv) > 1:
        inp = int(sys.argv[1])
    else:
        inp = int(input('Input a bot num\n1. Anti-scam\n'))

    if inp == 1:
        client.run(os.environ.get('ANTI-SCAM_TOKEN'))


if __name__ == '__main__':
    run_antiscam()
