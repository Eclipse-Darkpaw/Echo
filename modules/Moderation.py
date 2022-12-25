import discord
import json
import time

from fileManagement import server_settings_path, server_warns_path
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
        body = await read_line(client, dm, 'Body (attachements will not be sent):', sender, delete_prompt=False,
                               delete_response=False)
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


async def warn(message):
    """
    Gives a user a warning
    :param message:
    :return:
    """
    # check message isn't in DMs
    if message.guild is None:
        await message.channel.send('Unable to warn in DMs. Please use this in a guild.')
        return
    
    # load the json file
    with open(server_warns_path) as file:
        data = json.load(file)
    
    # make sure the guild has an existing log entry
    # if it doesn't, make one
    try:
        data[str(message.guild.id)]
    except KeyError:
        data[str(message.guild.id)] = {}
    
    # Check the user has permission to use the command
    if message.author.guild_permissions.manage_roles:
        user_id = get_user_id(message)
        # Todo: ensure there are enough arguments in the command
        try:
            reason = message.content.split(' ', 2)[2]
        except IndexError:
            await message.reply('Not enough arguments. please tag the user being warned, and give a reason to warn '
                                'the user')
            return
        # check if the user has previous warns
        try:
            warns = data[str(message.guild.id)][str(user_id)]
        except KeyError:
            # if no previous warns, create empty list
            warns = []
        # save current time for calculations
        warn_time = int(time.time())
        
        # add the new warn to the list
        warns.append({'time': warn_time,
                      'issuer_id': int(message.author.id),
                      'issuer_name': str(message.author),
                      'reason': reason,
                      })
        
        # calculate the number of warns in the last week
        num_warns = 0
        for warn in warns:
            # if the warn was within the year
            if int(time.strftime('%Y', time.gmtime(warn_time - warn['time']))) == 1970:
                # year needs to be 1970 bc thats when the unix epoch started
                # if warn was within the last week
                if 0 <= int(time.strftime('%j', time.gmtime(warn_time - warn['time']))) < 7:
                    num_warns += 1
        await message.channel.send(f'<@{user_id}> has been warned for {reason}')
        data[str(message.guild.id)][str(user_id)] = warns
        
        # save data to the file
        with open(server_warns_path, 'w') as file:
            file.write(json.dumps(data, indent=4))
            
        # create message and post it in the warning log
        with open(server_settings_path) as file:
            data = json.load(file)
        
        try:
            warn_log_id = data[str(message.guild.id)]['channels']['warn log']
        except KeyError:
            await message.channel.send('Unable to log to warn channel.')
            return
        
        warn_log = message.guild.get_channel(warn_log_id)
        await warn_log.send(f'Warning given to <@{user_id}> | `{message.guild.get_member(user_id)}`| `{user_id}` \n'
                            f'Reason cited: {reason}\n'
                            f'Of {len(warns)} total, {num_warns} have been within the last week.\n'
                            f'`Given by {message.author} on {time.strftime("%Y-%m-%d", time.gmtime(warn_time))}`')
        
        # suspend if more than 2 warns in the last week
        if num_warns > 2:
            await message.guild.get_member(user_id).add_roles(message.guild.get_role(data[str(message.guild.id)][
                                                                                         'roles']['suspended']))
            await warn_log.send(f'<@{user_id}> suspended for {num_warns} warns in one week')
    else:
        # user does not have permission to assign warns
        await message.channel.send('You are not allowed to use that command')


async def show_warns(message):
    """
    Displays a users warnings in an embed
    :param message:
    :return:
    """
    # check message isn't in DMs
    if message.guild is None:
        await message.channel.send('Unable to warn in DMs. Please use this in a guild.')
        return
    
    # load the json file
    with open(server_warns_path) as file:
        data = json.load(file)
    
    # make sure the guild has an existing log entry
    # if it doesn't, make one
    try:
        data[str(message.guild.id)]
    except KeyError:
        data[str(message.guild.id)] = {}
    
    # Check the user has permission to use the command
    if message.author.guild_permissions.manage_roles:
        user_id = get_user_id(message)
        # check if the user has previous warns
        try:
            warns = data[str(message.guild.id)][str(user_id)]
        except KeyError:
            warns = []
        embed = discord.Embed(title=f"{message.guild.get_member(user_id)}'s warns",
                              description=f'<@{user_id}>|`{user_id}`')
        
        counter = 1
        for warn in warns:
            embed.add_field(name=str(counter),
                            value=f"Reason cited: {warn['reason']}\n"
                                  f"Given by {warn['issuer_name']}(`{warn['issuer_id']}`) on <t:{warn['time']}:d>",
                            inline=False)
            counter += 1
        await message.channel.send(embed=embed)
            

async def remove_warn(message):
    """
        Displays a users warnings in an embed
        :param message:
        :return:
        """
    # check message isn't in DMs
    if message.guild is None:
        await message.channel.send('Unable to warn in DMs. Please use this in a guild.')
        return
    
    # load the json file
    with open(server_warns_path) as file:
        data = json.load(file)
    
    # make sure the guild has an existing log entry
    # if it doesn't, make one
    try:
        data[str(message.guild.id)]
    except KeyError:
        data[str(message.guild.id)] = {}
    
    # Check the user has permission to use the command
    if message.author.guild_permissions.manage_roles:
        user_id = get_user_id(message)
        
        # check to make sure the user id could be found
        if user_id == -1:
            await message.channel.send('User not found')
            return
        
        # check if the user has previous warns
        try:
            warns = data[str(message.guild.id)][str(user_id)]
        except KeyError:
            await message.channel.send(f'<@{user_id}> has no warnings')
            return
        
        #remove the warn from the list of warns
        try:
            warns.pop(int(message.content.split()[2])-1)
        except TypeError:
            await message.channel.send(f'Invalid argument, Please give a number instead of "{message.content.split()[2]}"')
            return
        except IndexError:
            await message.channel.send(f'Number out of range. please select the warn you want to remove.')
        
        # put modified list back into data
        data[str(message.guild.id)][str(user_id)] = warns

        # save data to the file
        with open(server_warns_path, 'w') as file:
            file.write(json.dumps(data, indent=4))
        
        await message.channel.send(f'Warn {message.content.split()[2]} removed')


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
            embed = discord.Embed(title='Ban Command usage', description='All bans have the server name appended to '
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
