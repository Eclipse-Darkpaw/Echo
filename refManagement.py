import discord
from fileManagement import ref_path
from main import get_user_id
# FIXME: increase speed of retrieving a ref. Current operation takes more than ten seconds per ref
# TODO: allow multiple refs.
# TODO: allow for multiple OCs
# CANCELLED: Add a loading animation to show it actually is working. make it a simple spinner using  -/|\


async def set_ref(message):
    try:
        with open(ref_path(message.author.id), 'w') as refs:
            for ref in message.attachments:
                refs.write(ref.url + '\n')
        await message.reply(content='Refs set!')
    except IndexError:
        await message.channel.send('No ref_sheet attached!')


async def ref(message):
    # NOTE: THIS METHOD NEEDS MEMBERS INTENT ACTIVE
    target = get_user_id(message)

    if target == None:
        await message.channel.send('User not found.')
        return

    target = target.id
    msg = await message.channel.send('Finding ref, please wait')
    try:
        ref_sheet = open(ref_path(target))
        await msg.edit(content='Ref Found! Uploading, Please wait!')
        await message.reply(content=ref_sheet.read())
        # await message.reply(file=file)      # old system
    except FileNotFoundError:
        await msg.edit(content='User has not set their ref.')
