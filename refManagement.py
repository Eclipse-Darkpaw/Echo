import discord
from fileManagement import ref_path
# FIXME: increase speed of retrieving a ref. Current operation takes more than ten seconds per ref
# TODO: allow multiple refs.
# TODO: allow for multiple OCs
# TODO: Add a loading animation to show it actually is working. make it a simple spinner using  -/|\



async def set_ref(message):
    try:
        ref_sheet = message.attachments[0]
        path = ref_path(message.author.id)
        await ref_sheet.save(fp=path)
        await message.channel.send(content='Ref set!')
    except IndexError:
        await message.channel.send('No ref_sheet attached!')


async def ref(message):
    command = message.content.split()
    try:
        if len(command) == 1:
            target = message.author.id
        elif len(command[1]) == 18:
            target = int(command[1])
        elif len(message.mentions) == 1:
            target = int(command[2:-2])
        elif len(command[1]) == 22:
            target = int(command[3:-2])
        else:
            # TODO: Allow users to search by name
            target = message.guild.get_member_named(command[1]).id
            if target == None:
                await message.channel.send('Not a valid user!')
                return
    except ValueError:
        await message.channel.send('Invalid user')
        return
    msg = message.channel.send('Finding ref, please wait')
    try:
        ref_sheet = open(ref_path(target), 'rb')
        file = discord.File(ref_sheet)
        await message.channel.send(file=file)
    except FileNotFoundError:
        await message.channel.send('User has not set their ref.')




