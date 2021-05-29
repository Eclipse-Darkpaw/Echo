import discord
from fileManagement import ref_path
from main import get_user_id
# FIXME: increase speed of retrieving a ref. Current operation takes more than ten seconds per ref
# TODO: allow multiple refs.
# TODO: allow for multiple OCs
# CANCELLED: Add a loading animation to show it actually is working. make it a simple spinner using  -/|\


async def set_ref(message):
    try:
        ref_sheet = message.attachments[0]
        path = ref_path(message.author.id)
        await ref_sheet.save(fp=path)
        await message.reply(content='Ref set!')
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
        ref_sheet = open(ref_path(target), 'rb')
        file = discord.File(ref_sheet)
        await msg.edit(content='Ref Found! Uploading, Please wait!')
        await message.reply(file=file)
    except FileNotFoundError:
        await msg.edit(content='User has not set their ref.')
