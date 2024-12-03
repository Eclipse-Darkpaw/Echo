import discord
import json
import time

from discord.ext import commands
from fileManagement import server_settings_path, server_warns_path
from main import read_line, get_user_id


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def __log_warn__(self, ctx):
        # load the json file
        with open(server_warns_path) as file:
            data = json.load(file)

        # make sure the guild has an existing log entry
        # if it doesn't, make one
        try:
            data[str(ctx.guild.id)]
        except KeyError:
            data[str(ctx.guild.id)] = {}

        # Check the user has permission to use the command
        if ctx.author.guild_permissions.manage_roles:
            # check if the user has previous warns
            try:
                warns = data[str(ctx.guild.id)][str(user.id)]
            except KeyError:
                # if no previous warns, create empty list
                warns = []
            # save current time for calculations
            warn_time = int(time.time())

            # add the new warn to the list
            warns.append({'time': warn_time,
                          'issuer_id': int(ctx.author.id),
                          'issuer_name': str(ctx.author),
                          'reason': reason,
                          })

    @commands.hybrid_command()
    @commands.guild_only()
    async def suspend(self, ctx: discord.Interaction, user: discord.User, reason: str):
        """
        Suspends a user for given reason
        Last docstring edit: -Autumn V4.0.0
        Last method edit: -Autumn V4.0.0
        :param ctx:
        :param user: User to suspend
        :param reason: reason to suspend
        :return:
        """
        # load the json file
        with open(server_warns_path) as file:
            data = json.load(file)

        # make sure the guild has an existing log entry
        # if it doesn't, make one
        try:
            data[str(ctx.guild.id)]
        except KeyError:
            data[str(ctx.guild.id)] = {}

        # Check the user has permission to use the command
        if ctx.author.guild_permissions.manage_roles:
            # check if the user has previous warns
            try:
                warns = data[str(ctx.guild.id)][str(user.id)]
            except KeyError:
                # if no previous warns, create empty list
                warns = []
            # save current time for calculations
            warn_time = int(time.time())

            # add the new warn to the list
            warns.append({'time': warn_time,
                          'issuer_id': int(ctx.author.id),
                          'issuer_name': str(ctx.author),
                          'reason': reason,
                          })
            with open(server_warns_path, 'w') as file:
                file.write(json.dumps(data, indent=4))

            # load the json file
            with open(server_settings_path) as file:
                data = json.load(file)

            try:
                warn_log_id = data[str(ctx.guild.id)]['channels']['warn log']
            except KeyError:
                await ctx.send('Unable to log to warn channel.')
                return

            warn_log = ctx.guild.get_channel(warn_log_id)

            await user.add_roles(ctx.guild.get_role(data[str(ctx.guild.id)]['roles']['suspended']))
            await warn_log.send(f'<@{user.id}> suspended for {reason}.')

            thread_name = f'{user.name} {time.strftime("%Y-%m-%d", time.gmtime(time.time()))} supsension (' \
                          f'TBD)'
            suspension = ctx.guild.get_channel(data[str(ctx.guild.id)]['channels']['suspended'])
            try:
                thread = await suspension.create_thread(name=thread_name, auto_archive_duration=1440)
                await thread.send(f'<@{user.id}> You have been suspended by <@{ctx.author.id}> for excessive '
                                  f'infractions. If you have any questions, please send them in this thread.')
                await ctx.reply(f'<@{user.id}> suspended.')
            except discord.Forbidden:
                await ctx.reply(f'<@{user.id}> suspended. unable to create thread')
        else:
            await ctx.reply('Invalid Permissions')

    @commands.hybrid_command()
    @commands.guild_only()
    async def warn(self, ctx: discord.Interaction, user: discord.User, reason: str):
        """
        Give a user a warning
        Last docstring edit: -Autumn V4.0.0
        Last method edit: -Autumn V4.0.0
        :param ctx: Interaction calling the command
        :param user: User to warn
        :param reason: Reason for warn
        :return:
        """
        # load the json file
        with open(server_warns_path) as file:
            data = json.load(file)

        # make sure the guild has an existing log entry
        # if it doesn't, make one
        try:
            data[str(ctx.guild.id)]
        except KeyError:
            data[str(ctx.guild.id)] = {}

        # Check the user has permission to use the command
        if ctx.author.guild_permissions.manage_roles:
            # check if the user has previous warns
            try:
                warns = data[str(ctx.guild.id)][str(user.id)]
            except KeyError:
                # if no previous warns, create empty list
                warns = []
            # save current time for calculations
            warn_time = int(time.time())

            # add the new warn to the list
            warns.append({'time': warn_time,
                          'issuer_id': int(ctx.author.id),
                          'issuer_name': str(ctx.author),
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
            await ctx.send(f'<@{user.id}> has been warned for {reason}')
            data[str(ctx.guild.id)][str(user.id)] = warns

            # save data to the file
            with open(server_warns_path, 'w') as file:
                file.write(json.dumps(data, indent=4))

            # create message and post it in the warning log
            with open(server_settings_path) as file:
                data = json.load(file)

            try:
                warn_log_id = data[str(ctx.guild.id)]['channels']['warn log']
            except KeyError:
                await ctx.send('Unable to log to warn channel.')
                return

            warn_log = ctx.guild.get_channel(warn_log_id)
            await warn_log.send(f'Warning given to <@{user.id}> | `{ctx.guild.get_member(user.id)}`| `{user.id}` \n'
                                f'Reason cited: {reason}\n'
                                f'Of {len(warns)} total, {num_warns} have been within the last week.\n'
                                f'`Given by {ctx.author} on {time.strftime("%Y-%m-%d", time.gmtime(warn_time))}`')

            # suspend if more than 2 warns in the last week
            if num_warns > 2:
                await self.suspend(ctx, user=user, reason=f'{num_warns} warns in one week')
                await ctx.guild.get_member(user.id).add_roles(ctx.guild.get_role(data[str(ctx.guild.id)][
                                                                                             'roles']['suspended']))
                await warn_log.send(f'<@{user.id}> suspended for {num_warns} warns in one week')
                thread_name = f'{ctx.author.name} {time.strftime("%Y-%m-%d", time.gmtime(time.time()))} supsension (' \
                              f'TBD)'
                suspension = ctx.guild.get_channel(data[str(ctx.guild.id)]['channels']['suspended'])
                try:
                    thread = await suspension.create_thread(name=thread_name, auto_archive_duration=1440)
                    await thread.send(f'<@{user.id}> You have been suspended by <@{ctx.author.id}> for excessive '
                                      f'infractions. If you have any questions, please send them in this thread.')
                except discord.Forbidden:
                    await ctx.send(f'<@{user.id}> suspended. unable to create thread')
        else:
            # user does not have permission to assign warns
            await ctx.send('You are not allowed to use that command')

    @commands.hybrid_command()
    async def show_warns(self, ctx: discord.Interaction, user: discord.User):
        """
        Lists a users warns in an embed
        Last docstring edit: -Autumn V4.0.0
        Last method edit: -Autumn V4.0.0
        :param ctx: Message calling the command
        :param user: user to list warns for
        :return:
        """
        # load the json file
        with open(server_warns_path) as file:
            data = json.load(file)

        # make sure the guild has an existing log entry
        # if it doesn't, make one
        try:
            data[str(ctx.guild.id)]
        except KeyError:
            data[str(ctx.guild.id)] = {}

        # Check the user has permission to use the command
        if ctx.author.guild_permissions.manage_roles:
            # check if the user has previous warns
            try:
                warns = data[str(ctx.guild.id)][str(user.id)]
            except KeyError:
                warns = []
            embed = discord.Embed(title=f"{ctx.guild.get_member(user.id)}'s warns",
                                  description=f'<@{user.id}>|`{user.id}`')

            counter = 1
            for warn in warns:
                embed.add_field(name=str(counter),
                                value=f"Reason cited: {warn['reason']}\n"
                                      f"Given by {warn['issuer_name']}(`{warn['issuer_id']}`) on <t:{warn['time']}:d>",
                                inline=False)
                counter += 1
            await ctx.reply(embed=embed)

    @commands.hybrid_command()
    async def remove_warn(self, ctx: discord.Interaction, user: discord.User, warn: int):
        """
        Removes a warn from a user
        Last docstring edit: -Autumn V4.0.0
        Last method edit: -Autumn V4.0.0
        :param ctx: Message calling the command
        :param user: user to remove a warn from
        :param warn: warn to remove
        """
        # load the json file
        with open(server_warns_path) as file:
            data = json.load(file)

        # make sure the guild has an existing log entry
        # if it doesn't, make one
        try:
            data[str(ctx.guild.id)]
        except KeyError:
            data[str(ctx.guild.id)] = {}

        # Check the user has permission to use the command
        if ctx.author.guild_permissions.kick_members:
            user_id = get_user_id(ctx)
            # check if the user has previous warns
            try:
                warns = data[str(ctx.guild.id)][str(user.id)]
            except KeyError:
                await ctx.send(f'<@{user.id}> has no warnings')
                return

            # remove the warn from the list of warns
            try:
                warns.pop(warn-1)
            except IndexError:
                await ctx.send(f'Number out of range. please select the warn you want to remove.')

            # put modified list back into data
            data[str(ctx.guild.id)][str(user_id)] = warns

            # save data to the file
            with open(server_warns_path, 'w') as file:
                file.write(json.dumps(data, indent=4))

            await ctx.send(f'Warn {warn} removed')

    @commands.hybrid_command()
    async def kick(self, ctx: discord.Interaction, user: discord.User, reason: str = 'No reason specified.'):
        """
        Kicks a user out of the server for given reason
        Last docstring edit: -Autumn V4.0.0
        Last method edit: -Autumn V4.0.0
        Method added: V1.16.0
        :param ctx:The message that called the command
        :param user: User to kick
        :param reason: Reason for kick (users will not see this)
        """
        if ctx.author.guild_permissions.kick_members:
            target = user.id
            try:
                await ctx.guild.kick(user, reason=reason)
                await ctx.send(f'<@!{target}> was kicked.')
            except discord.Forbidden:
                await ctx.reply('__**Error 403: Forbidden**__\nPlease verify I have the proper permissions.')

        else:
            await ctx.reply('Unauthorized usage.')

    @commands.hybrid_command()
    @commands.guild_only()
    async def ban(self, ctx: discord.Interaction, user: discord.User, reason: str):
        """
        Bans a user from the server for given reason
        Last docstring edit: -Autumn V4.0.0
        Last method edit: -Autumn V4.0.0
        Method added: V1.16.0
        :param ctx: The message that called the command
        :param user: User to ban
        :param reason: Reason for ban (users will not see this)
        """
        if ctx.author.guild_permissions.kick_members:
            target = user.id
            try:
                await ctx.guild.ban(user, reason=reason)
                await ctx.send(f'<@!{target}> was kicked.')
            except discord.Forbidden:
                await ctx.reply('__**Error 403: Forbidden**__\nPlease verify I have the proper permissions.')

        else:
            await ctx.reply('Unauthorized usage.')
