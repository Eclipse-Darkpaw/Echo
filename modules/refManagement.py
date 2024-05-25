import os
from fileManagement import ref_path, nsfw_ref_path
from main import get_user_id, Message
from random import randint


async def set_ref(message, nsfw=False):
    try:
        trim = message.content[8:]
        command = trim.split('\n')
        
        if nsfw:
            path = nsfw_ref_path(message.author.id)
        else:
            path = ref_path(message.author.id)
        
        with open(path, 'w') as refs:
            for line in command:
                try:
                    refs.write(line + '\n')
                except UnicodeEncodeError:
                    await message.channel.send('Line failed to save. Please use ASCII characters\n> ' + line)
            for ref in message.attachments:
                refs.write(ref.url + '\n')
        await message.reply(content='Refs set! Do not delete that message or the refs wont appear!')
    except IndexError:
        await message.channel.send('No ref_sheet attached!')


async def add_ref(message, nsfw=False):
    """add_ref method
    adds a ref to a user's ref document"""
    try:
        trim = message.content[8:]
        command = trim.split('\n')
        
        if nsfw:
            path = nsfw_ref_path(message.author.id)
        else:
            path = ref_path(message.author.id)

        with open(path, 'a') as refs:
            for line in command:
                try:
                    refs.write(line + '\n')
                except UnicodeEncodeError:
                    for char in line:
                        try:
                            refs.write(char)
                        except UnicodeEncodeError:
                            await message.channel.send('Line failed to save. Please use ASCII characters\n> ' + char)
            for ref_sheet in message.attachments:
                refs.write(ref_sheet.url + '\n')
        await message.reply(content='Refs added!')
    except IndexError:
        await message.channel.send('No ref attached!')


async def random_ref(message, refs_in_guild=True):
    """
    >random ref (all)
    :param message:
    :param refs_in_guild:
    :return:
    """
    command = message.content[1:].split(' ', 1)
    if len(command) == 2 and (command[0] == 'rr' or command[0] == 'randomref' or command[0] == 'random_ref'):
        refs_in_guild = False
    guild = message.guild
    
    ref_ids = [int(f[:-5]) for f in os.listdir('resources/refs') if f[-5:] == '.refs']
    ref_ids.remove(message.author.id)
    target_id = int(ref_ids[randint(0, len(ref_ids))])
    target_in_guild = False
    
    if guild is not None:
        member_ids = [m.id for m in message.guild.members]
        if target_id in member_ids:
            target_in_guild = True
    
        if refs_in_guild:
            while not target_in_guild:
                if target_id in member_ids:
                    target_in_guild = True
                else:
                    ref_ids.remove(target_id)
                    target_id = int(ref_ids[randint(0, len(ref_ids))])
                
    await ref(Message('ref ' + str(target_id), message.channel, target_message=message))
    
    if target_in_guild:
        target = message.guild.get_member(target_id)
        await message.channel.send(target.name + "'s ref sheet(s)\n`ID: " + str(target_id) + '`')
    else:
        await message.channel.send('<@' + str(target_id) + ">'s ref sheet")


async def ref(message, nsfw=False):
    # NOTE: THIS METHOD NEEDS MEMBERS INTENT ACTIVE
    command = message.content.split(' ', 2)

    if len(command) == 1:
        target = message.author.id

        if target is None:
            await message.channel.send('User not found.')
            return

        msg = await message.channel.send('Finding ref, please wait')
        try:
        
            if nsfw:
                path = nsfw_ref_path(message.author.id)
            else:
                path = ref_path(message.author.id)
            ref_sheet = open(path)
            await msg.edit(content='Ref Found! Uploading, Please wait!')
            await message.reply(content=ref_sheet.read())
        except FileNotFoundError:
            if nsfw:
                await msg.edit(content='User has not set NSFW ref. Retrieving SFW ref')
                await ref(message, False)
            else:
                await msg.edit(content='User has not set their SFW ref.')
    elif command[1] == 'set':
        await set_ref(message)
        await message.reply('Ref set!')
    elif command[1] == 'add':
        await add_ref(message)
        await message.reply('Ref added!')
    elif command[1] == 'random':
        await random_ref(message, len(command) == 2)
    else:
        target = get_user_id(message)

        if target is None:
            await message.channel.send('User not found.')
            return

        msg = await message.channel.send('Finding ref, please wait')
        try:
            if nsfw:
                path = nsfw_ref_path(target)
            else:
                path = ref_path(target)
            ref_sheet = open(path)
            await msg.edit(content='Ref Found! Uploading, Please wait!')
            await message.reply(content=ref_sheet.read())
        except FileNotFoundError:
            await msg.edit(content='User has not set their ref.')
            if nsfw:
                await msg.edit(content='User has not set NSFW ref. Retrieving SFW ref')
                await ref(message, False)
            else:
                await msg.edit(content='User has not set their SFW ref.')
