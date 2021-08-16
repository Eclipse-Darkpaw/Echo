import discord
import os
from fileManagement import ref_path, oc_folder_path, oc_path
from main import get_user_id
# TODO: allow for multiple OCs


async def set_ref(message):
    try:
        trim = message.content[8:]
        command = trim.split('\n')

        with open(ref_path(message.author.id), 'w') as refs:
            for line in command:
                try:
                    refs.write(line + '\n')
                except UnicodeEncodeError:
                    await message.channel.send('Line failed to save. Please use ASCII characters\n> ' + line)
            for ref in message.attachments:
                refs.write(ref.url + '\n')
        await message.reply(content='Refs set! Do not delete that message or the refs wont appear!' )
    except IndexError:
        await message.channel.send('No ref_sheet attached!')


async def add_ref(message):
    """add_ref method
    adds a ref to a user's ref document"""
    try:
        trim = message.content[8:]
        command = trim.split('\n')

        with open(ref_path(message.author.id), 'a') as refs:
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


async def ref(message):
    # NOTE: THIS METHOD NEEDS MEMBERS INTENT ACTIVE
    command = message.content.split(' ', 2)
    if command[1] == 'set':
        set_ref(message)
    elif command[1] == 'add':
        add_ref(message)
    else:
        target = get_user_id(message)

        if target == None:
            await message.channel.send('User not found.')
            return

        msg = await message.channel.send('Finding ref, please wait')
        try:
            ref_sheet = open(ref_path(target))
            await msg.edit(content='Ref Found! Uploading, Please wait!')
            await message.reply(content=ref_sheet.read())
        except FileNotFoundError:
            await msg.edit(content='User has not set their ref.')


async def oc(message):
    # >OC <add/show/edit/tree>
    command = message.content.split(' ',2)
    if command[1] == 'add':
        await add_oc(message)
    elif command[1] == 'show':
        await show_oc(message)
    elif command[1] == 'edit':
        await edit_oc(message)
    elif command[1] == 'tree':
        await oc_tree(message)


async def add_oc(message):
    # >OC add <name> <description/ref>
    """creates a new characters ref file"""
    command = message.content.split(' ', 3)
    target = message.author.id
    target_folder = oc_folder_path(target)
    try:
        os.chdir(target_folder)
    except FileNotFoundError:
        os.mkdir(target_folder)
    target_file = target_folder + '\\' + command[2] + '.ref'
    try:
        file = open(target_file, 'x')
        file.close()
    except FileExistsError:
        await message.reply('Error: OC already exists. Please rename the OC file')
        return
    if len(command) == 4:
        with open(target_file, 'w') as file:
            try:
                file.write(command[3] + '\n')
            except UnicodeEncodeError:
                await message.channel.send('Line failed to save. Please use ASCII characters\n> ' + line)
            attachments = message.attachments
            for attachment in attachments:
                file.write(attachment.url)
    await message.reply('OC created.')


async def show_oc(message):
    # >OC get <ownerId/tagged> <name>
    command = message.content.split(' ', 3)
    if len(command) < 4:
        await message.reply('Error: TypeError\n missing 1 required positional argument: \'name\'')
        return
    else:
        with open(oc_path(command[2], command[3])) as file:
            pass
        target = get_user_id(message, 2)

        if target is None:
            await message.channel.send('User not found.')
            return

        msg = await message.channel.send('Finding ref, please wait')
        try:
            ref_sheet = open(oc_path(target, command[3]))
            await msg.edit(content='Ref Found! Uploading, Please wait!')
            await message.reply(content=ref_sheet.read())
        except FileNotFoundError:
            await msg.edit(content='User has no oc with this name.')


async def edit_oc(message):
    # >OC edit <name> <description/ref>
    """edits a characters ref file"""
    command = message.content.split(' ', 3)
    target = message.author.id
    target_folder = oc_folder_path(target)
    target_file = target_folder + '\\' + command[2] + '.ref'
    try:
        file = open(target_file, 'r')
        file.close()
    except FileNotFoundError:
        await message.reply('Error: OC not found. please create an OC with that name')
        return
    if len(command) == 4:
        with open(target_file, 'w') as file:
            try:
                file.write(command[3] + '\n')
            except UnicodeEncodeError:
                await message.channel.send('Line failed to save. Please use ASCII characters\n> ' + line)
            attachments = message.attachments
            for attachment in attachments:
                file.write(attachment.url)
    await message.reply('OC created.')


async def oc_tree(message):
    # >OC tree <ownerID/tagged>
    file = oc_folder_path(get_user_id(message, 2))
    try:
        os.chdir(file)
        tree = '```\n'+str(get_user_id(message, 2))
        children = os.listdir()
        for child in children:
            if child == children[-1]:
                tree += '\n└───' + str(child)
            else:
                tree += '\n├───' + str(child)
        tree += '```'
        os.chdir('C:\\Users\\leebe\\Desktop\\Echo')
    except FileNotFoundError:
        tree = 'No OCs found'
    await message.reply(content=tree)
