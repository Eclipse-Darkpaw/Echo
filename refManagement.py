import discord
from fileManagement import ref_path
from main import get_user_id
# FIXME: increase speed of retrieving a ref. Current operation takes more than ten seconds per ref
# TODO: allow multiple refs.
# TODO: allow for multiple OCs
# CANCELLED: Add a loading animation to show it actually is working. make it a simple spinner using  -/|\


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


async def ref(message):
    # NOTE: THIS METHOD NEEDS MEMBERS INTENT ACTIVE
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
