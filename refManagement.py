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
        await message.reply(content='Ref set!')
    except IndexError:
        await message.channel.send('No ref_sheet attached!')


async def ref(message):
    # NOTE: THIS METHOD NEEDS MEMBERS INTENT ACTIVE
    command = message.content.split()
    try:
        if len(command) == 1:
            target = message.author.id
        elif len(command[1]) == 18:
            target = int(command[1])
        elif len(message.mentions) == 1:
            target = message.mentions[0].id
        else:
            # TODO: Allow users to search by name
            print(command[1])
            target = message.guild.get_member_named(command[1])
            print(target)

            if target == None:
                await message.channel.send('User not found.')
                return
            else:
                target = target.id
    except ValueError:
        await message.channel.send('Invalid user')
        return
    msg = await message.channel.send('Finding ref, please wait')
    try:
        ref_sheet = open(ref_path(target), 'rb')
        file = discord.File(ref_sheet)
        await msg.edit(content='Ref Found! Uploading, Please wait!')
        await message.reply(file=file)
    except FileNotFoundError:
        await msg.edit(content='User has not set their ref.')
