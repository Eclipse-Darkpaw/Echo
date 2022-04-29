import time
import discord
import os
import sys

project_version = '2.0.1'

start_time = time.time()
# todo: add uptime feature
# todo: add a master prefix only applicable to you as a back door


class Message:
    def __init__(self, content, channel, target_message = None):
        self.content = content
        self.channel = channel
        self.author = target_message.author
        self.message = target_message

    async def reply(self, content):
        await self.message.reply(content)
        

async def read_line(client, channel, prompt, target, delete_prompt=True, delete_response=True):
    show = await channel.send(prompt)

    def check(msg):
        return msg.author != client.user and msg.author == target and msg.channel == channel

    msg = await client.wait_for('message', check=check)

    if delete_response:
        try:
            await msg.delete()
        finally:
            pass
    if delete_prompt:
        await show.delete()

    return msg


# NOTE: THIS METHOD NEEDS MEMBERS INTENT ACTIVE
def get_user_id(message, arg=1):
    """
    
    :param message:
    :param arg:
    :return: Returns a user ID as an int. returns -1 if unable to complete task. works in 100% of cases if used right,
    so don't worry about it ever returning -1.
    """
    command = message.content.split(' ')
    if len(command) == arg:
        return message.author.id
    elif len(command[arg]) == 18:
        return int(command[arg])
    elif len(message.mentions) == 1:
        return message.mentions[0].id
    elif message.guild is not None:
        return message.guild.get_member_named(command[1]).id
    else:
        return -1


async def ping(message):
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit)


async def quit(message):
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def restart(message):
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        os.execl(sys.executable,__file__,'main.py')
    else:
        await message.channel.send('You do not have permission to turn me off!')

'''RNG base on a string a human creates then converts each word into an int by using its position on the list of words.
add each int and mod '''