import time
import discord
import os
import sys


start_time = time.time()
# todo: add uptime feature
# todo: add a master prefix only applicable to you as a back door

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

# NOTE: THIS METHOD NEEDS MEMBERS INTENT ACTIVE
def get_user_id(message):
    command = message.content.split(maxsplit=1)
    if len(command) == 1:
        target = message.author.id
    elif len(command[1]) == 18:
        target = int(command[1])
    elif len(message.mentions) == 1:
        target = message.mentions[0].id
    else:
        target = message.guild.get_member_named(command[1]).id

    return target


async def ping(message):
    log(message)
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit)


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
'''

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

async def help(message):
    embed = discord.Embed(title="SunReek Command list", color=0x45FFFF)
    embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    embed.add_field(name='`'+prefix+'help`', value="That's this command!", inline=False)
    embed.add_field(name='`'+prefix+'verify`', value='Verifies an un verified member.', inline=False)
    embed.add_field(name='`'+prefix+'modmail`', value='Sends a private message to the moderators.', inline=False)
    embed.add_field(name='`'+prefix+'test`', value='Tests if the bot is online', inline=False)
    embed.add_field(name='`'+prefix+'version_num`', value='What version the bot is currently on')
    embed.add_field(name='`'+prefix+'profile [member tag/member id]/[edit]`', value="Gets a tagged user's profile or your profile")
    embed.add_field(name='`'+prefix+'edit`', value='Saves all important files')
    embed.add_field(name='`'+prefix+'ref [member tag/member id]`', value="gets a user's ref sheet")
    embed.add_field(name='`'+prefix+'set_ref <attachment>`', value="Sets a user's ref")

    embed.add_field(name='Moderator Commands', value='Commands that only mods can use', inline=False)
    embed.add_field(name='`'+prefix+'quit`', value='quits the bot', inline=False)
    await message.channel.send(embed=embed)

'''RNG base on a string a human creates then converts each word into an int by using its position on the list of words.
add each int and mod '''