import discord
import json
from fileManagement import server_settings_path

from main import read_line, get_user_id


async def modmail(message, client):
    """
    Sends a message to the moderators. Alerts the user if an error occurs during the process
    Last docstring edit: -Autumn V1.14.4
    Last method edit: Unknown
    :param message: Message that called the bot
    :return: None
    """
    with open(server_settings_path) as file:
        mail_inbox = json.load(file)[str(message.guild.id)]['channels']['mailbox']
    sender = message.author
    await message.delete()

    dm = await sender.create_dm()
    try:
        subject = await read_line(client, dm, 'Subject Line:', sender, delete_prompt=False, delete_response=False)
        subject = 'Modmail | ' + subject.content
        body = await read_line(client, dm, 'Body:', sender, delete_prompt=False, delete_response=False)
        await dm.send('Your message has been sent')
    except discord.Forbidden:
        message.reply('Unable to DM. Check your privacy settings')
        return

    mail = discord.Embed(title=subject, color=0xadd8ff)
    try:
        avatar_url = sender.guild_avatar.url
    except AttributeError:
        avatar_url = sender.avatar.url
    mail.set_author(name=sender.name, icon_url=avatar_url)
    mail.add_field(name='Message', value=body.content)
    await message.guild.get_channel(mail_inbox).send(embed=mail)
    


async def kick(message):
    """
        Method designed to kick users from the server the command originated.
        >kick [user] [reason]
        Last docstring edit: -Autumn V1.16.0
        Last method edit: -Autumn V3.3.0
        Method added: V1.16.0
        :param message:The message that called the command
        :return: None
        """
    if message.author.guild_permissions.kick_members:
        command = message.content[1:].split(' ', 2)
        if len(command) == 1:
            embed = discord.Embed(title='Kick Command usage')
            embed.add_field(name='}kick [user]', value='Kicks a user from the server')
            embed.add_field(name='}kick [user] [reason]', value='Kicks a user with the reason provided')
            await message.channel.send(embed=embed)
            return

        target = get_user_id(message)

        if len(command) > 2:
            reason = command[2]
        else:
            reason = 'No reason specified.'
        try:
            await message.guild.kick(message.guild.get_member(target), reason=reason)
            await message.channel.send('<@!' + target + '> was kicked.')
        except discord.Forbidden:
            await message.reply('__**Error 403: Forbidden**__\nPlease verify I have the proper permissions.')

    else:
        await message.reply('Unauthorized usage.')


async def ban(message):
    """
        Method designed to ban users from the server the command originated. Deletes User messages from the last 24
        hours
        >ban [user] [reason]
        Last docstring edit: -Autumn V1.16.0
        Last method edit: -Autumn V1.16.3
        Method added: -Autumn V1.16.0
        :param message:The message that called the command
        :return: None
        """
    if message.author.guild_permissions.ban_members:
        command = message.content[1:].split(' ', 2)
        if len(command) == 1:
            embed = discord.Embed(title='Ban Command usage', description='All bans have the ` | Rikoland` appended to '
                                                                         'the reason for documentation in the Server '
                                                                         'Protector database')
            embed.add_field(name='}ban [user]', value='Bans a user from the server')
            embed.add_field(name='}ban [user] [reason]', value='Bans a user with the reason provided')
            await message.channel.send(embed=embed)
            return

        target = get_user_id(message, 1)

        if len(command) > 2:
            reason = command[2]
        else:
            reason = 'No reason specified.'

        try:
            await message.guild.ban(message.guild.get_member(target),
                                    reason=f'{reason} | {message.guild.name}',
                                    delete_message_days=1)
            await message.channel.send('<@!' + str(target) + '> was banned.')
        except discord.Forbidden:
            await message.reply('__**Error 403: Forbidden**__\nPlease verify I have the proper permissions.')

    else:
        await message.reply('Unauthorized usage.')
