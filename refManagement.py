import discord
import os
from fileManagement import ref_path
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
            for ref in message.attachments:
                refs.write(ref.url + '\n')
        await message.reply(content='Refs added!')
    except IndexError:
        await message.channel.send('No ref_sheet attached!')


async def add_char(message):
    #>OC add_char <name> [file path] <description/ref>
    command = message.content.split(' ',3)
    os.mkdir(command[2],)


async def list_chars_in_dir(message):
    # shows a list of the chars/folders in the current directory
    # >OC
    pass


async def ref(message):
    # NOTE: THIS METHOD NEEDS MEMBERS INTENT ACTIVE
    command = message.content.split(' ', 2)
    if command[1] == 'set':
        set_ref(message)
    elif command[1] == 'add':
        add_ref()
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


async def create_folder(message):
    #>OC create_folder <folder> <name> <path>
    command = message.content.split(' ',4)
    os.mkdir()


async def file_tree(message):
    root = 'C:\\Users\\leebe\\Desktop\\Bot-files\\' + str(message.author.id)
