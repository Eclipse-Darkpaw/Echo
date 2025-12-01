import discord
import io
import json
import os
import time

from discord.ext import commands

from base_bot import EchoBot
from config import Paths
from util import get_user_id


class Moderation(commands.Cog):
    def __init__(self, bot: EchoBot):
        self.bot = bot

        os.makedirs(Paths.data_dir, exist_ok=True)
        if not os.path.exists(Paths.servers_warns):
            with open(Paths.servers_warns, 'w') as f:
                f.write('{}')

        self.bot.logger.info(f'✔ Moderation cog loaded')

    @commands.hybrid_command(brief="🔐 manage_roles | Suspend a user for given reason")
    @commands.guild_only()
    async def suspend(self, ctx: commands.Context, user: discord.User, reason: str):
        """
        🔐 manage_roles | Suspend a user for given reason

        This command will add the reason as a new warn to
        the user's warn list and then add the suspended role
        of this guild to that user.

        If possible a thread will be made where the suspended user
        can ask questions if needed.

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.3.0

        :param ctx: Context object for the invoked command
        :param user: User to suspend
        :param reason: Reason to suspend
        :return: None
        """
        # load the json file
        with open(Paths.servers_warns) as file:
            data = json.load(file)

        # make sure the guild has an existing log entry
        # if it doesn't, make one
        try:
            data[str(ctx.guild.id)]
        except KeyError:
            data[str(ctx.guild.id)] = {}

        # Check the user has permission to use the command
        if ctx.author.guild_permissions.manage_roles or str(ctx.author.id) in self.bot.config.guardians:
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
            with open(Paths.servers_warns, 'w') as file:
                file.write(json.dumps(data, indent=4))

            # load the json file
            with open(Paths.servers_settings) as file:
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
                await ctx.respond(f'<@{user.id}> suspended.')
            except discord.Forbidden:
                await ctx.respond(f'<@{user.id}> suspended. unable to create thread')
        else:
            await ctx.reply('Invalid Permissions')

    @commands.hybrid_command(brief="🔐 manage_roles | Give a user a warning")
    @commands.guild_only()
    async def warn(self, ctx: commands.Context, user: discord.User, reason: str):
        """
        🔐 manage_roles | Give a user a warning
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.3.0

        :param ctx: Context object for the invoked command
        :param user: User to warn
        :param reason: Reason for warn
        :return: None
        """
        # load the json file
        with open(Paths.servers_warns) as file:
            data = json.load(file)

        # make sure the guild has an existing log entry
        # if it doesn't, make one
        try:
            data[str(ctx.guild.id)]
        except KeyError:
            data[str(ctx.guild.id)] = {}

        # Check the user has permission to use the command
        if ctx.author.guild_permissions.manage_roles or str(ctx.author.id) in self.bot.config.guardians:
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
            with open(Paths.servers_warns, 'w') as file:
                file.write(json.dumps(data, indent=4))

            # create message and post it in the warning log
            with open(Paths.servers_warns) as file:
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

    @commands.hybrid_command(brief="🔐 manage_roles | Lists a user's warns")
    @commands.guild_only()
    async def show_warns(self, ctx: commands.Context, user: discord.User):
        """
        🔐 manage_roles | Lists a user's warns in an embed

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0

        :param ctx: Context object for the invoked command
        :param user: user to list warns for
        :return: None
        """
        # load the json file
        with open(Paths.servers_warns) as file:
            data = json.load(file)

        # make sure the guild has an existing log entry
        # if it doesn't, make one
        try:
            data[str(ctx.guild.id)]
        except KeyError:
            data[str(ctx.guild.id)] = {}

        # Check the user has permission to use the command
        if ctx.author.guild_permissions.manage_roles or str(ctx.author.id) in self.bot.config.guardians:
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
            await ctx.respond(embed=embed)

    @commands.hybrid_command(brief="🔐 kick_members | Remove a warn from a user")
    @commands.guild_only()
    async def remove_warn(self, ctx: commands.Context, user: discord.User, warn: int):
        """
        🔐 kick_members | Remove a warn from a user

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param ctx: Context object for the invoked command
        :param user: User to remove a warn from
        :param warn: Warn to remove
        :return: None
        """
        # load the json file
        with open(Paths.servers_warns) as file:
            data = json.load(file)

        # make sure the guild has an existing log entry
        # if it doesn't, make one
        try:
            data[str(ctx.guild.id)]
        except KeyError:
            data[str(ctx.guild.id)] = {}

        # Check the user has permission to use the command
        if ctx.author.guild_permissions.kick_members or str(ctx.author.id) in self.bot.config.guardians:
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
            with open(Paths.servers_warns, 'w') as file:
                file.write(json.dumps(data, indent=4))

            await ctx.send(f'Warn {warn} removed')

    @commands.hybrid_command(brief="🔐 kick_members | Kick a server member")
    @commands.guild_only()
    async def kick(self, ctx: commands.Context, user: discord.User, reason: str = 'No reason specified.'):
        """
        🔐 kick_members | Kick a user out of the server

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0

        :param ctx: Context object for the invoked command
        :param user: User to kick
        :param reason: Reason for kick (users will not see this)
        :return: None
        """
        if ctx.author.guild_permissions.kick_members or str(ctx.author.id) in self.bot.config.guardians:
            target = user.id
            try:
                await ctx.guild.kick(user, reason=reason)
                await ctx.send(f'<@!{target}> was kicked.')
            except discord.Forbidden:
                await ctx.respond('__**Error 403: Forbidden**__\nPlease verify I have the proper permissions.')

        else:
            await ctx.respond('Unauthorized usage.')

    @commands.hybrid_command(brief="🔐 kick_members | Ban a user from the server")
    @commands.guild_only()
    async def ban(self, ctx: commands.Context, user: discord.User, reason: str):
        """
        🔐 kick_members | Bans a user from the server

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.3.0

        :param ctx: Context object for the invoked command
        :param user: User to ban
        :param reason: Reason for ban (users will not see this)
        :return: None
        """
        if ctx.author.guild_permissions.kick_members or str(ctx.author.id) in self.bot.config.guardians:
            target = user.id
            try:
                await ctx.guild.ban(user, reason=reason)
                await ctx.send(f'<@!{target}> was kicked.')
            except discord.Forbidden:
                await ctx.respond('__**Error 403: Forbidden**__\nPlease verify I have the proper permissions.')

        else:
            await ctx.respond('Unauthorized usage.')

    @commands.hybrid_command(brief="🔐 ban_members | Export banned users")
    @commands.guild_only()
    async def export_bans(self, ctx: commands.Context, limit=1000, after=None):
        """
        🔐 ban_members | Exports a list of banned users in the server

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0

        :param ctx: Context object for the invoked command
        :param limit: Limit of bans to fetch (defaults tp 1000, the discord api limit)
        :param after: User ID to start after (optional)
        :return: None
        """
        bans = [entry async for entry in ctx.guild.bans(limit=limit, after=after)]
        out = ''

        for ban in bans:
            userid = ban.user.id
            username = ban.user.name
            reason = ban.reason
            out += f'{username} {userid} {reason};\n'

        file = discord.File(
            io.BytesIO(out.encode('utf-8')),
            filename=f'bans_{ctx.guild.id}.txt'
        )
        await ctx.reply(file=file)

    @commands.hybrid_command(brief="🔐 ban_members | Import banned users (from list)")
    @commands.guild_only()
    async def import_bans(self, ctx: commands.Context, bans: str):
        """
        🔐 ban_members | imports a list of banned users in the format "username userID reason;"

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -Autumna1Equin0x V4.4.0

        :param ctx: Context object for the invoked command
        :param format: Format for the list. Txt and json available
        :return: None
        """
        lines = bans.split(';')
        for line in lines:
            try:
                username, userid, reason = line.split(maxsplit=2)
            except:
                continue
            user = await ctx.bot.fetch_user(userid)
            await ctx.guild.ban(user=user, reason=reason)
        await ctx.reply(f'{len(lines)}')

