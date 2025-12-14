import asyncio
import discord
import datetime
import json
import time

from dataclasses import dataclass
from discord import app_commands
from modules.artfight_ui import (
    artfight_configuration_embed,
    build_daily_status_embed,
    build_fancy_leaderboard_embed,
    build_final_scores_message,
    build_join_embed,
    build_prompt_embed,
    build_scores_message,
    build_submission_embed,
    build_unregistered_members_embed,
    build_warning_message,
    build_yap_with_ping,
    calculate_score,
    ConfigurationView,
    get_user_team,
    JoinArtfightView,
    JoinArtfightDisabledView,
    split_score_for_collab,
    SubmissionData,
    SubmissionFlowView,
    UnregisteredMembersView,
    update_join_message_for_end
)
from base_bot import EchoBot
from config import MAX_DISCORD_MESSAGE_LEN, Paths
from discord.ext import commands, tasks
from random import randint
from repositories import ArtfightRepo
from typing import Optional
from util import read_line, get_current_artfight_day


@dataclass
class ScheduledTimes:
    """Cached scheduled times for a guild's artfight."""
    warning_time: datetime.time   # 30 min before prompt
    scores_time: datetime.time    # 5 min before prompt
    prompt_time: datetime.time    # The prompt time


class Artfight(commands.GroupCog, name="artfight"):

    def __init__(self, bot: EchoBot):
        self.bot = bot
        self.artfight_repo = ArtfightRepo()
        
        # Persistent view for join button
        self._join_view = JoinArtfightView(self.artfight_repo)

        # guilds with active/upcoming artfight
        self._active_guilds: set[int] = set()
        
        # Cached scheduled times per guild
        self._scheduled_times: dict[int, ScheduledTimes] = {}
        
        # Member sync tracking
        self._initial_sync_done: dict[int, bool] = {}                # guild_id: whether initial sync on day 1 is done
        self._post_buffer_sync_done: dict[int, bool] = {}            # guild_id: whether 5-min buffer sync is done
        self._artfight_start_time: dict[int, datetime.datetime] = {} # guild_id: when artfight prompt was first sent
        self._minute_counter: dict[int, int] = {}                    # guild_id: minutes since last hourly check
        
        # Track if artfight end was already handled for each guild
        self._artfight_end_handled: dict[int, bool] = {}

        self.bot.logger.info(f'✔ Artfight cog loaded')

    def _calculate_scheduled_times(self, guild_id: int) -> ScheduledTimes | None:
        """
        Calculate the warning, scores, and prompt times for a guild.
        Returns None if prompt time is not configured.
        """
        prompt_time = self.artfight_repo.get_next_prompt_hour(guild_id)
        if prompt_time is None:
            return None

        # datetime objects to do time maths
        # Using a dummy date, only care about the time part of it tho
        dummy_date = datetime.date(2000, 1, 1)
        prompt_dt = datetime.datetime.combine(dummy_date, prompt_time)
        
        warning_dt = prompt_dt - datetime.timedelta(minutes=30)
        scores_dt = prompt_dt - datetime.timedelta(minutes=5)
        
        return ScheduledTimes(
            warning_time=warning_dt.time(),
            scores_time=scores_dt.time(),
            prompt_time=prompt_time
        )

    def _update_scheduled_times_for_guild(self, guild_id: int):
        times = self._calculate_scheduled_times(guild_id)
        if times:
            self._scheduled_times[guild_id] = times
            self.bot.logger.debug(f'Updated scheduled times for guild {guild_id}: warning={times.warning_time}, scores={times.scores_time}, prompt={times.prompt_time}')
        elif guild_id in self._scheduled_times:
            del self._scheduled_times[guild_id]

    async def cog_load(self):
        """Called when the cog is loaded. Starts the daily artfight check task and registers persistent views."""
        # Register persistent view for the join button
        self.bot.add_view(self._join_view)
        self.daily_artfight_check.start()

    async def cog_unload(self):
        """Called when the cog is unloaded. Stops all tasks."""
        self.daily_artfight_check.cancel()
        if self.prompt_minute_check.is_running():
            self.prompt_minute_check.cancel()

    @tasks.loop(hours=24)
    async def daily_artfight_check(self):
        """
        Runs once every 24 hours to check if any artfight is active or starting within 24h.
        If so, ensures the minute-check loop is running.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        """
        await self._evaluate_artfight_activity()

    @daily_artfight_check.before_loop
    async def before_daily_artfight_check(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()
        await self._evaluate_artfight_activity()

    async def _evaluate_artfight_activity(self):
        """
        Evaluates all guilds to determine if any artfight is active or starting within 24 hours.
        Starts or stops the minute-check loop accordingly.
        This method can be called externally when configuration changes.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        """
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        current_date_utc = now_utc.date()
        tomorrow_utc = current_date_utc + datetime.timedelta(days=1)

        self._active_guilds.clear()

        for guild in self.bot.guilds:
            try:
                if self._is_artfight_active_or_imminent(guild.id, current_date_utc, tomorrow_utc):
                    self._active_guilds.add(guild.id)
            except Exception as e:
                self.bot.logger.error(f'Error evaluating artfight activity for guild {guild.id}: {e}')

        for guild_id in self._active_guilds:
            self._update_scheduled_times_for_guild(guild_id)

        if self._active_guilds:
            if not self.prompt_minute_check.is_running():
                self.prompt_minute_check.start()
                self.bot.logger.info(f'Started prompt minute check for {len(self._active_guilds)} guild(s)')
        else:
            if self.prompt_minute_check.is_running():
                self.prompt_minute_check.cancel()
                self.bot.logger.info('Stopped prompt minute check - no active artfights')

    def _is_artfight_active_or_imminent(
        self,
        guild_id: int,
        current_date: datetime.date,
        tomorrow: datetime.date
    ) -> bool:
        """
        Checks if an artfight is currently active or will start within the next 24 hours.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param guild_id: The guild ID to check
        :param current_date: Current UTC date
        :param tomorrow: Tomorrow's UTC date
        :return: True if artfight is active or starting within 24h
        """
        start_date = self.artfight_repo.get_start_date(guild_id)
        end_date = self.artfight_repo.get_end_date(guild_id)

        if start_date is None or end_date is None:
            return False

        # Active: current date is within the artfight period
        if start_date <= current_date <= end_date:
            return True

        # Imminent: artfight starts today or tomorrow (within 24h window)
        if current_date <= start_date <= tomorrow:
            return True

        return False

    async def on_artfight_configuration_changed(self, guild_id: int):
        """
        Should be called when artfight configuration is changed for a guild.
        Re-evaluates whether the minute loop should be running and updates scheduled times.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param guild_id: The guild whose configuration changed
        """
        self.bot.logger.debug(f'Artfight configuration changed for guild {guild_id}, re-evaluating activity')
        self._update_scheduled_times_for_guild(guild_id)
        await self._evaluate_artfight_activity()

    @tasks.loop(minutes=1)
    async def prompt_minute_check(self):
        """
        Runs every minute when artfight is active/imminent.
        Handles:
        - Sending daily prompts at the configured time
        - Member sync on artfight start (day 1)
        - Grace period buffer - sync members 5 minutes after start
        - Hourly unregistered member checks
        
        Uses UTC time to ensure consistency regardless of server timezone.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        """
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        current_date_utc = now_utc.date()

        for guild_id in self._active_guilds.copy():
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                continue

            try:
                await self._process_guild_minute_tick(guild, now_utc, current_date_utc)
            except Exception as e:
                self.bot.logger.error(f'Error in minute tick for guild {guild_id}: {e}')

    @prompt_minute_check.before_loop
    async def before_prompt_minute_check(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()

    async def _process_guild_minute_tick(
        self,
        guild: discord.Guild,
        now_utc: datetime.datetime,
        current_date_utc: datetime.date
    ):
        """
        Process all minute-based checks for a single guild.
        Handles: artfight end, warning message, scores message, prompt message, member sync.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param guild: The Discord guild to process
        :param now_utc: Current UTC datetime
        :param current_date_utc: Current UTC date
        """
        # Check if artfight has ended and update the join message
        await self._check_and_handle_artfight_end(guild, current_date_utc)
        
        # Send daily messages (warning, scores, prompt)
        await self._check_and_send_daily_messages(guild, now_utc, current_date_utc)
        
        if guild.id in self._artfight_start_time:
            await self._handle_member_sync_timing(guild, now_utc)

    async def _check_and_send_daily_messages(
        self,
        guild: discord.Guild,
        now_utc: datetime.datetime,
        current_date_utc: datetime.date
    ):
        """
        Check and send the daily messages: warning (30min before), scores (5min before), yap & prompt.
        Skips warning and scores on day 1.
        On last day: still sends warning (without grace period reminder).
        At prompt hour on last day: sends final scores + fancy leaderboard stats instead of new prompt.

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param guild: The Discord guild
        :param now_utc: Current UTC datetime
        :param current_date_utc: Current UTC date
        """
        start_date = self.artfight_repo.get_start_date(guild.id)
        end_date = self.artfight_repo.get_end_date(guild.id)

        if start_date is None or end_date is None:
            return

        # Check if artfight is active today
        if not (start_date <= current_date_utc <= end_date):
            return

        scheduled = self._scheduled_times.get(guild.id)
        if scheduled is None:
            return

        prompts_channel_id = self.artfight_repo.get_prompts_channel(guild.id)
        if prompts_channel_id is None:
            return

        prompts_channel = guild.get_channel(prompts_channel_id)
        if prompts_channel is None:
            return

        current_time = now_utc.time()
        artfight_day = (current_date_utc - start_date).days + 1
        is_day_one = artfight_day == 1
        is_last_day = current_date_utc == end_date
        artfight_role_id = self.artfight_repo.get_artfight_role(guild.id)

        def time_passed(target_time: datetime.time) -> bool:
            return current_time >= target_time

        # Day 1: Skip warning and scores, only send prompt
        if not is_day_one:
            # 30 minutes before: Send warning (including on last day)
            if (not self.artfight_repo.has_sent_message(guild.id, artfight_day, 'warning') and 
                time_passed(scheduled.warning_time) and 
                not time_passed(scheduled.scores_time)):
                # Build full datetime for Discord timestamp
                prompt_datetime = datetime.datetime.combine(
                    current_date_utc, 
                    scheduled.prompt_time, 
                    tzinfo=datetime.timezone.utc
                )
                await self._send_warning_message(prompts_channel, artfight_role_id, prompt_datetime, is_last_day)
                self.artfight_repo.mark_message_sent(guild.id, artfight_day, 'warning')

            # 5 minutes before: Send scores (but NOT on last day)
            if (not is_last_day and
                not self.artfight_repo.has_sent_message(guild.id, artfight_day, 'status') and 
                time_passed(scheduled.scores_time) and 
                not time_passed(scheduled.prompt_time)):
                await self._send_scores_message(prompts_channel, guild.id, artfight_role_id)
                self.artfight_repo.mark_message_sent(guild.id, artfight_day, 'status')

        # At prompt time
        if time_passed(scheduled.prompt_time):
            
            if is_last_day:
                # Last day: Send final scores and fancy leaderboard
                if not self.artfight_repo.has_sent_message(guild.id, artfight_day, 'hall_of_fame'):
                    await self._send_final_results(prompts_channel, guild, artfight_role_id)
                    self.artfight_repo.mark_message_sent(guild.id, artfight_day, 'hall_of_fame')
            else:
                # Normal day: Send yap message + prompt
                if not self.artfight_repo.has_sent_message(guild.id, artfight_day, 'yap'):
                    await self._send_yap_message(prompts_channel, guild, artfight_day, artfight_role_id)
                    self.artfight_repo.mark_message_sent(guild.id, artfight_day, 'yap')
                
                if not self.artfight_repo.has_sent_message(guild.id, artfight_day, 'prompt'):
                    await self._send_prompt_message(prompts_channel, guild, artfight_day, artfight_role_id)
                    self.artfight_repo.mark_message_sent(guild.id, artfight_day, 'prompt')
            
            # Day 1: trigger member sync (only once per day, use prompt as trigger since it's last)
            if is_day_one and not self._initial_sync_done.get(guild.id, False):
                self._artfight_start_time[guild.id] = now_utc
                self._initial_sync_done[guild.id] = False
                self._post_buffer_sync_done[guild.id] = False
                self._minute_counter[guild.id] = 0
                
                await self._sync_team_members_from_roles(guild)
                self._initial_sync_done[guild.id] = True
                self.bot.logger.info(f'Performed initial member sync for guild {guild.id}')

    async def _send_warning_message(
        self,
        channel: discord.TextChannel,
        artfight_role_id: int | None,
        prompt_datetime: datetime.datetime | None = None,
        is_last_day: bool = False
    ):
        try:
            message = build_warning_message(artfight_role_id, prompt_datetime, is_last_day)
            await channel.send(message)
            self.bot.logger.info(f'Sent warning message in guild {channel.guild.id}')
        except discord.HTTPException as e:
            self.bot.logger.error(f'Failed to send warning message: {e}')

    async def _send_scores_message(
        self,
        channel: discord.TextChannel,
        guild_id: int,
        artfight_role_id: int | None
    ):
        try:
            message = build_scores_message(self.artfight_repo, guild_id, artfight_role_id)
            await channel.send(message)
            self.bot.logger.info(f'Sent scores message in guild {guild_id}')
        except discord.HTTPException as e:
            self.bot.logger.error(f'Failed to send scores message: {e}')

    async def _send_yap_message(
        self,
        channel: discord.TextChannel,
        guild: discord.Guild,
        artfight_day: int,
        artfight_role_id: int | None
    ):
        """Send the yap message with ping."""
        try:
            yap_message = self.artfight_repo.get_yap_message(guild.id, artfight_day)
            yap_content = build_yap_with_ping(yap_message, artfight_role_id, artfight_day)
            await channel.send(yap_content)
            self.bot.logger.info(f'Sent day {artfight_day} yap message for guild {guild.id}')
        except discord.HTTPException as e:
            self.bot.logger.error(f'Failed to send yap message: {e}')

    async def _send_prompt_message(
        self,
        channel: discord.TextChannel,
        guild: discord.Guild,
        artfight_day: int,
        artfight_role_id: int | None
    ):
        """Send the prompt embed (no ping)."""
        try:
            artfight_role = guild.get_role(artfight_role_id) if artfight_role_id else None
            prompt = self.artfight_repo.get_prompt(guild.id, artfight_day)
            prompt_embed = build_prompt_embed(prompt, artfight_day, artfight_role)
            await channel.send(embed=prompt_embed)
            self.bot.logger.info(f'Sent day {artfight_day} prompt for guild {guild.id}')
        except discord.HTTPException as e:
            self.bot.logger.error(f'Failed to send prompt message: {e}')

    async def _send_final_results(
        self,
        channel: discord.TextChannel,
        guild: discord.Guild,
        artfight_role_id: int | None
    ):
        """
        Send the final scores message and fancy leaderboard at the end of artfight.
        Called at prompt hour on the last day.

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param channel: The prompts channel
        :param guild: The Discord guild
        :param artfight_role_id: The artfight role ID to ping (or None)
        """
        try:
            # Get artfight role for embed color
            artfight_role = guild.get_role(artfight_role_id) if artfight_role_id else None
            role_color = artfight_role.color if artfight_role else None
            
            # Send final scores message (with ping, announces closure)
            content, final_scores_embed = build_final_scores_message(
                self.artfight_repo, guild.id, artfight_role_id, role_color
            )
            await channel.send(content=content if content else None, embed=final_scores_embed)

            # Send Hall of Fame message (plain text with markdown)
            leaderboard_message = build_fancy_leaderboard_embed(self.artfight_repo, guild, guild.id, artfight_role)
            await channel.send(content=leaderboard_message)

            self.bot.logger.info(f'Sent final results for guild {guild.id}')
        except discord.HTTPException as e:
            self.bot.logger.error(f'Failed to send final results: {e}')

    async def _check_and_handle_artfight_end(
        self,
        guild: discord.Guild,
        current_date_utc: datetime.date
    ):
        """
        Check if artfight has ended and update the join message accordingly.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param guild: The Discord guild to check
        :param current_date_utc: Current UTC date
        """
        # Check if we already handled the end for this guild
        if self._artfight_end_handled.get(guild.id, False):
            return

        end_date = self.artfight_repo.get_end_date(guild.id)
        if end_date is None:
            return

        # Check if artfight just ended (we're now past the end date)
        if current_date_utc > end_date:
            self._artfight_end_handled[guild.id] = True
            
            try:
                await update_join_message_for_end(self.artfight_repo, guild)
                self.bot.logger.info(f'Updated join message for artfight end in guild {guild.id}')
            except Exception as e:
                self.bot.logger.error(f'Failed to update join message for artfight end in guild {guild.id}: {e}')

    async def _handle_member_sync_timing(
        self,
        guild: discord.Guild,
        now_utc: datetime.datetime
    ):
        """
        Handle the timing logic for member sync checks:
        - 5 minutes after start: run sync one more time
        - Every hour after: check for unregistered members and warn
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param guild: The Discord guild
        :param now_utc: Current UTC datetime
        """
        start_time = self._artfight_start_time.get(guild.id)
        if start_time is None:
            return

        minutes_since_start = (now_utc - start_time).total_seconds() / 60

        # 5-minute buffer sync
        if not self._post_buffer_sync_done.get(guild.id, False) and minutes_since_start >= 5:
            await self._sync_team_members_from_roles(guild)
            self._post_buffer_sync_done[guild.id] = True
            self._minute_counter[guild.id] = 0  # Reset counter for hourly checks
            self.bot.logger.info(f'Performed post-buffer member sync for guild {guild.id}')
            return

        # Hourly checks (only after the 5-minute buffer sync is done)
        if self._post_buffer_sync_done.get(guild.id, False):
            self._minute_counter[guild.id] = self._minute_counter.get(guild.id, 0) + 1
            
            if self._minute_counter[guild.id] >= 60:
                self._minute_counter[guild.id] = 0
                await self._check_and_warn_unregistered_members(guild)

    async def _sync_team_members_from_roles(self, guild: discord.Guild):
        """
        Syncs all members who have artfight team roles.
        Adds any member with a team role to the artfight data.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param guild: The Discord guild to sync
        """
        teams = self.artfight_repo.get_teams(guild.id)
        
        if not teams:
            self.bot.logger.warning(f'No teams configured for guild {guild.id}, skipping member sync')
            return

        synced_count = 0
        
        for team_name, role_id in teams.items():
            role = guild.get_role(role_id)
            if role is None:
                self.bot.logger.warning(f'Could not find role {role_id} for team {team_name} in guild {guild.id}')
                continue

            for member in role.members:
                # Check if member is already registered
                existing_member = self.artfight_repo.get_team_member(guild.id, team_name, member.id)
                if existing_member is None:
                    try:
                        self.artfight_repo.add_team_member(guild.id, team_name, member.id)
                        synced_count += 1
                    except Exception as e:
                        self.bot.logger.error(f'Failed to sync member {member.id} to team {team_name}: {e}')

        if synced_count > 0:
            self.bot.logger.info(f'Synced {synced_count} members from roles for guild {guild.id}')

    async def _check_and_warn_unregistered_members(self, guild: discord.Guild):
        """
        Checks for members who have artfight team roles but are not registered in the bot.
        If found, sends a warning to the warn_log channel asking what to do.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param guild: The Discord guild to check
        """
        teams = self.artfight_repo.get_teams(guild.id)
        
        if not teams:
            return

        unregistered_members: dict[str, list[discord.Member]] = {}
        
        for team_name, role_id in teams.items():
            role = guild.get_role(role_id)
            if role is None:
                continue

            unregistered_in_team = []
            for member in role.members:
                existing_member = self.artfight_repo.get_team_member(guild.id, team_name, member.id)
                if existing_member is None:
                    unregistered_in_team.append(member)

            if unregistered_in_team:
                unregistered_members[team_name] = unregistered_in_team

        if not unregistered_members:
            return

        warn_log_channel_id = None
        if 'servers_settings_repo' in self.bot.repositories:
            warn_log_channel_id = self.bot.repositories['servers_settings_repo'].get_guild_channel(
                str(guild.id), 'warn_log'
            )

        if warn_log_channel_id is None:
            self.bot.logger.warning(
                f'No warn_log channel configured for guild {guild.id}, '
                f'cannot report {sum(len(m) for m in unregistered_members.values())} unregistered members'
            )
            return

        warn_log_channel = guild.get_channel(warn_log_channel_id)
        if warn_log_channel is None:
            self.bot.logger.warning(f'Could not find warn_log channel {warn_log_channel_id} in guild {guild.id}')
            return

        embed = build_unregistered_members_embed(guild, unregistered_members)
        view = UnregisteredMembersView(
            self.artfight_repo,
            guild,
            unregistered_members
        )

        try:
            message = await warn_log_channel.send(embed=embed, view=view)
            view.message = message
            self.bot.logger.info(
                f'Sent unregistered members warning for guild {guild.id}: '
                f'{sum(len(m) for m in unregistered_members.values())} members'
            )
        except discord.Forbidden:
            self.bot.logger.error(f'Missing permissions to send message in warn_log channel for guild {guild.id}')
        except discord.HTTPException as e:
            self.bot.logger.error(f'Failed to send unregistered members warning for guild {guild.id}: {e}')

    @commands.hybrid_command(brief="Configure artfight settings")
    @commands.guild_only()
    async def configuration(self, ctx: commands.Context):
        """
        Configure the artfight settings.
        At runtime alterations are possible, caution is advised!
        Note: These changes will persist immediately, if you wish to archive the current configuration before overwriting, use /artfight archive

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0

        :param ctx: The context calling the command
        :return: None
        """
        message = await ctx.reply(content='Loading configuration...')
        while not self.artfight_repo.ensure_guild_entry(ctx.guild.id):
            message.edit(content='Preparing data structure...')
            time.sleep(0.2)

        view = ConfigurationView(self.bot, self.artfight_repo, ctx.guild.id)
        embed = artfight_configuration_embed(self.artfight_repo, ctx.guild.id)
        await message.edit(content=None, embed=embed, view=view)
        view.message = message

    @commands.hybrid_command(name="set_join_button", brief="Create a persistent join button for artfight")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def set_join_button(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        """
        Creates an embed with a persistent 'Join Artfight!' button.
        
        Before artfight starts: Users can choose their team.
        After artfight starts: Users are auto-assigned to the balanced team.
        When artfight ends: The button is disabled.
        
        Requirements:
        - At least one team must be configured
        - Artfight role must be configured (optional but recommended)
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param ctx: The command context
        :param channel: The channel to post the join message in
        :param message: The custom message to display in the embed
        """
        await ctx.defer()

        # Validate configuration
        teams = self.artfight_repo.get_teams(ctx.guild.id)
        if not teams:
            await ctx.reply('❌ No teams are configured. Please configure at least one team first using `/artfight configuration`.')
            return

        start_date = self.artfight_repo.get_start_date(ctx.guild.id)
        end_date = self.artfight_repo.get_end_date(ctx.guild.id)
        if start_date is None or end_date is None:
            await ctx.reply('❌ Artfight dates are not configured. Please set start and end dates first using `/artfight configuration`.')
            return

        artfight_role = self.artfight_repo.get_artfight_role(ctx.guild.id)
        if artfight_role is None:
            await ctx.reply('⚠️ Warning: Artfight role is not configured. Users will only receive team roles. You can set this in `/artfight configuration`.')

        # Check if artfight is already over
        current_date_utc = datetime.datetime.now(datetime.timezone.utc).date()
        artfight_over = current_date_utc > end_date

        # Build and send the embed
        embed = build_join_embed(message, artfight_over=artfight_over)
        
        if artfight_over:
            view = JoinArtfightDisabledView()
        else:
            view = self._join_view

        try:
            sent_message = await channel.send(embed=embed, view=view)
        except discord.Forbidden:
            await ctx.reply(f'❌ I don\'t have permission to send messages in {channel.mention}.')
            return
        except discord.HTTPException as e:
            await ctx.reply(f'❌ Failed to send message: {e}')
            return

        # Store the message ID for persistence
        self.artfight_repo.set_join_message(ctx.guild.id, channel.id, sent_message.id)

        await ctx.reply(f'✅ Join button created in {channel.mention}!')

    @commands.hybrid_command(brief="Join an ongoing artfight, your team is picked for you")
    @commands.guild_only()
    async def join(self, ctx: commands.Context):
        """
        Joins a user to an Artfight team. The bot automatically assigns
        the user to the team with the least members. If teams are equal
        in size, it picks the team with the least points. If still equal,
        it picks randomly.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param ctx: The command context
        """
        # Defer response first, repo operations may take longer than the initial
        # max response time before discord sees the interaction or slash command as failed.
        await ctx.defer()

        current_date_utc = datetime.datetime.now(datetime.timezone.utc).date()
        start_date = self.artfight_repo.get_start_date(ctx.guild.id)
        end_date = self.artfight_repo.get_end_date(ctx.guild.id)

        if start_date is None or end_date is None:
            await ctx.reply('Artfight is not scheduled for this server.')
            return

        if current_date_utc > end_date:
            await ctx.reply('Artfight has already ended.')
            return

        # Get configured teams
        teams = self.artfight_repo.get_teams(ctx.guild.id)
        if not teams:
            await ctx.reply('Artfight teams are not configured yet.')
            return

        # Check if user is already on a team (using internal data)
        for team_name in teams.keys():
            if self.artfight_repo.get_team_member(ctx.guild.id, team_name, ctx.author.id) is not None:
                await ctx.reply('You are already on a team!')
                return

        # Build team data for comparison using internal data
        team_data = []
        for team_name, role_id in teams.items():
            role = ctx.guild.get_role(role_id)
            if role is None:
                self.bot.logger.warning(f'Could not find role {role_id} for team {team_name} in guild {ctx.guild.id}')
                continue
            
            team_members = self.artfight_repo.get_team_members(ctx.guild.id, team_name) or {}
            member_count = len(team_members)
            team_data.append({
                'name': team_name,
                'role': role,
                'member_count': member_count
            })

        if not team_data:
            # Find guardians who are in this guild
            guardian_mentions = []
            for guardian_id in self.bot.config.guardians:
                member = ctx.guild.get_member(int(guardian_id))
                if member:
                    guardian_mentions.append(member.mention)
            
            contact = ', '.join(guardian_mentions) if guardian_mentions else 'a moderator'
            await ctx.reply(f'Could not find any of the configured team data. Please contact {contact}.')
            return

        team_data.sort(key=lambda t: t['member_count'])
        min_member_count = team_data[0]['member_count']
        all_teams_tied = all(t['member_count'] == min_member_count for t in team_data)

        if not all_teams_tied:
            selected_team = team_data[0]
        else:
            # Fallback to scores
            for team in team_data:
                team['score'] = self.artfight_repo.get_team_score(ctx.guild.id, team['name']) or 0
            
            team_data.sort(key=lambda t: t['score'])
            min_score = team_data[0]['score']
            all_scores_tied = all(t['score'] == min_score for t in team_data)
            
            if not all_scores_tied:
                selected_team = team_data[0]
            else:
                # Fallback to random
                selected_team = team_data[randint(0, len(team_data) - 1)]

        # Get artfight role (optional but recommended)
        artfight_role_id = self.artfight_repo.get_artfight_role(ctx.guild.id)
        artfight_role = ctx.guild.get_role(artfight_role_id) if artfight_role_id else None

        # First, try to register the member in the repository
        try:
            self.artfight_repo.add_team_member(ctx.guild.id, selected_team['name'], ctx.author.id)
        except Exception as e:
            self.bot.logger.error(f'Failed to register member {ctx.author.id} in artfight data: {e}')
            await ctx.reply('Failed to register you in the artfight data. Please try again later.')
            return

        # Data saved successfully, now assign the roles
        roles_to_add = [selected_team['role']]
        if artfight_role:
            roles_to_add.append(artfight_role)

        try:
            await ctx.author.add_roles(*roles_to_add)
        except discord.Forbidden:
            # Role assignment failed - rollback the data
            try:
                self.artfight_repo.remove_team_member(ctx.guild.id, selected_team['name'], ctx.author.id)
            except Exception:
                self.bot.logger.error(f'Failed to rollback member {ctx.author.id} after role assignment failure')
            await ctx.reply('I don\'t have permission to assign roles.')
            return
        except discord.HTTPException as e:
            # Role assignment failed - rollback the data
            try:
                self.artfight_repo.remove_team_member(ctx.guild.id, selected_team['name'], ctx.author.id)
            except Exception:
                self.bot.logger.error(f'Failed to rollback member {ctx.author.id} after role assignment failure')
            await ctx.reply(f'Failed to assign role: {e}')
            return

        await ctx.reply(f'Welcome to the fight! You have been assigned to **{selected_team["role"].name}**!')

    async def _get_prompt_choices(self, guild_id: int) -> list[app_commands.Choice[int]]:
        """
        Build prompt choices for the submit command autocomplete.
        Shows current day as (Current) and previous days as (Late).
        Does not show future prompts.
        Includes a "No Prompt" option for unrelated art submissions.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        """
        start_date = self.artfight_repo.get_start_date(guild_id)
        if start_date is None:
            return []
        
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        prompt_time = self.artfight_repo.get_next_prompt_hour(guild_id)
        
        # Calculate current day based on when prompts drop, not calendar date
        current_day = get_current_artfight_day(start_date, prompt_time, now_utc)
        
        # Check if within grace period (first 15 min after prompt hour)
        is_within_grace = False
        if prompt_time:
            prompt_datetime = datetime.datetime.combine(now_utc.date(), prompt_time, tzinfo=datetime.timezone.utc)
            time_since_prompt = (now_utc - prompt_datetime).total_seconds() / 60
            is_within_grace = 0 <= time_since_prompt <= 15
        
        prompts = self.artfight_repo.get_prompts(guild_id) or {}
        choices = []
        
        for day in range(current_day, 0, -1):  # Current day down to day 1
            day_str = str(day)
            prompt_text = prompts.get(day_str, f"Day {day}")
            
            # Truncate prompt text if too long
            display_prompt = prompt_text[:60] + "..." if len(prompt_text) > 60 else prompt_text
            
            if day == current_day:
                label = f"(Current) Day {day}: {display_prompt}"
            elif day == current_day - 1 and is_within_grace:
                label = f"(Grace Period) Day {day}: {display_prompt}"
            else:
                label = f"(Late) Day {day}: {display_prompt}"
            
            # Discord choice names limited to 100 chars
            choices.append(app_commands.Choice(name=label[:100], value=day))
        
        # Add "No Prompt" option at the end for unrelated art (value 0)
        choices.append(app_commands.Choice(name="(No Points) Unrelated art - not for any prompt", value=0))
        
        return choices[:25]  # Discord limit

    @commands.hybrid_command(brief="Submit artwork to artfight")
    @commands.guild_only()
    @app_commands.describe(
        prompt_day="Which prompt is this submission for? Defaults to today's prompt."
    )
    async def submit(self, ctx: commands.Context, prompt_day: Optional[int] = None):
        """
        Submit artwork to artfight. The submission process continues in DMs.
        
        You'll be guided through selecting collaborators (if any), uploading your art,
        and providing details about your submission.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param ctx: The command context
        :param prompt_day: Which prompt day this submission is for (defaults to current)
        """
        await ctx.defer(ephemeral=True)
        
        # Check if artfight is configured and running
        start_date = self.artfight_repo.get_start_date(ctx.guild.id)
        end_date = self.artfight_repo.get_end_date(ctx.guild.id)
        
        if start_date is None or end_date is None:
            await ctx.reply("❌ Artfight is not configured for this server.", ephemeral=True)
            return
        
        current_date_utc = datetime.datetime.now(datetime.timezone.utc).date()
        
        if not (start_date <= current_date_utc <= end_date):
            await ctx.reply("❌ Artfight is not currently running.", ephemeral=True)
            return
        
        # Calculate current artfight day (based on when prompts drop, not calendar date)
        prompt_time = self.artfight_repo.get_next_prompt_hour(ctx.guild.id)
        current_day = get_current_artfight_day(start_date, prompt_time)
        
        # Validate prompt_day if provided (0 = no prompt/unrelated art)
        if prompt_day is not None:
            if prompt_day < 0 or prompt_day > current_day:
                await ctx.reply(
                    f"❌ Invalid prompt day. Must be between 0 and {current_day} (current day).",
                    ephemeral=True
                )
                return
        else:
            prompt_day = current_day  # Default to current day
        
        # Check if user is on a team
        submitter_team = get_user_team(self.artfight_repo, ctx.guild.id, ctx.author.id)
        if submitter_team is None:
            await ctx.reply(
                "❌ You must be on a team to submit. Use the join button or `/artfight join` first.",
                ephemeral=True
            )
            return
        
        # Check for submissions channel
        submissions_channel_id = self.artfight_repo.get_submissions_channel(ctx.guild.id)
        if submissions_channel_id is None:
            await ctx.reply(
                "❌ Submissions channel is not configured. Please contact an admin.",
                ephemeral=True
            )
            return
        
        submissions_channel = ctx.guild.get_channel(submissions_channel_id)
        if submissions_channel is None:
            await ctx.reply(
                "❌ Could not find the submissions channel. Please contact an admin.",
                ephemeral=True
            )
            return
        
        # Determine submission status for display
        if prompt_day == 0:
            prompt_status = "(No Points - Unrelated Art)"
        elif prompt_day < current_day:
            prompt_status = "(Late)"
        else:
            prompt_status = "(Current)"
        
        # Build the DM intro message
        if prompt_day == 0:
            dm_intro = "## Starting submission process!\nSubmitting: **Unrelated art** (no prompt, no points)\n---"
        else:
            dm_intro = f"## Starting submission process!\nSubmitting for: Day {prompt_day} {prompt_status}\n---"
        
        # Try to create DM
        try:
            dm_channel = await ctx.author.create_dm()
            await dm_channel.send(dm_intro)
        except discord.Forbidden:
            await ctx.reply(
                "❌ I can't DM you! Please enable DMs from server members and try again.",
                ephemeral=True
            )
            return
        
        await ctx.reply(
            "✅ Check your DMs to continue with your submission!",
            ephemeral=True
        )
        
        # Create and start the submission flow (prompt_day already determined)
        flow = SubmissionFlowView(
            artfight_repo=self.artfight_repo,
            guild=ctx.guild,
            submitter=ctx.author,
            submitter_team=submitter_team,
            prompt_day=prompt_day,
            dm_channel=dm_channel,
            submissions_channel=submissions_channel
        )
        
        # Start the flow - will ask for collaborators first
        await flow.start()
        
        # Set up message listener for the DM flow
        def check(message: discord.Message) -> bool:
            return (
                message.author.id == ctx.author.id and 
                message.channel.id == dm_channel.id
            )
        
        # Handle the submission flow
        # Only wait_for messages when the flow expects text input (not during button steps)
        BUTTON_TIMEOUT = 300  # 5 minutes for button steps (matches View timeout)
        button_wait_start = None
        
        try:
            while not flow.is_finished():
                if flow.expects_message():
                    button_wait_start = None  # Reset button timer
                    try:
                        message = await self.bot.wait_for('message', check=check, timeout=600)
                        await flow.handle_message(message)
                    except TimeoutError:
                        await dm_channel.send("❌ Submission timed out. Please start again with `/artfight submit`.")
                        return
                else:
                    # Button step - track how long we've been waiting
                    if button_wait_start is None:
                        button_wait_start = time.time()
                    elif time.time() - button_wait_start > BUTTON_TIMEOUT:
                        await dm_channel.send("❌ Submission timed out. Please start again with `/artfight submit`.")
                        return
                    await asyncio.sleep(1)
                    
        except Exception as e:
            self.bot.logger.error(f"Error in submit flow for user {ctx.author.id}: {e}")
            await dm_channel.send(f"❌ An error occurred: {e}")

    @submit.autocomplete('prompt_day')
    async def prompt_day_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[int]]:
        """Autocomplete for the prompt_day parameter."""
        return await self._get_prompt_choices(interaction.guild_id)

    @commands.hybrid_command(name='score')
    @commands.guild_only()
    async def scores(self, ctx: commands.Context):
        """
        Shows the scores for the teams. Admin only.
        Non-admins get a polite rejection (with a 1% chance of gaslighting).
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param ctx: The command context
        """
        # Check permissions
        if not ctx.author.guild_permissions.manage_roles:
            # 1% chance of gaslighting with dog image
            if randint(1, 100) == 1:
                # Send the dog eyes image
                import os
                dog_image_path = os.path.join(
                    os.path.dirname(__file__), 
                    'artfight_ui', 
                    'dog-eyes.png'
                )
                try:
                    await ctx.reply(
                        "Why do you want to know?",
                        file=discord.File(dog_image_path)
                    )
                except FileNotFoundError:
                    await ctx.reply("Why do you want to know?")
            else:
                await ctx.reply("This command is only for admins.")
            return
        
        # Get teams from repo
        teams = self.artfight_repo.get_teams(ctx.guild.id)
        if not teams:
            await ctx.reply("No teams are configured for this server.")
            return
        
        points_name = self.artfight_repo.get_points_name(ctx.guild.id)
        
        # Build team data with scores
        team_data = []
        for team_name, role_id in teams.items():
            role = ctx.guild.get_role(role_id)
            if role is None:
                continue
            score = self.artfight_repo.get_team_score(ctx.guild.id, team_name) or 0
            team_data.append({
                'name': team_name,
                'role': role,
                'score': score
            })
        
        if not team_data:
            await ctx.reply("Could not find any team roles.")
            return
        
        # Sort by score descending
        team_data.sort(key=lambda t: t['score'], reverse=True)
        
        # Build the embed
        score_embed = discord.Embed(title='Team Scores')
        
        # Check for tie
        scores_tied = len(set(t['score'] for t in team_data)) == 1
        
        if scores_tied:
            # Randomly pick which team's color to use
            score_embed.color = team_data[randint(0, len(team_data) - 1)]['role'].color
            score_embed.set_footer(text='Points are tied!')
        else:
            # Use leading team's color
            score_embed.color = team_data[0]['role'].color
            lead = team_data[0]['score'] - team_data[1]['score']
            score_embed.set_footer(text=f"{team_data[0]['role'].name} is {lead:,} {points_name} ahead!")
        
        # Add fields for each team
        for i, team in enumerate(team_data):
            prefix = "🥇" if i == 0 and not scores_tied else "🥈" if i == 1 else ""
            score_embed.add_field(
                name=f"{prefix} {team['role'].name}",
                value=f"**{team['score']:,}** {points_name}",
                inline=True
            )
        
        await ctx.reply(embed=score_embed)

    @commands.hybrid_command(name='modify_points', brief="Modify points for a submission")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @app_commands.describe(
        member="The member whose submission points to modify",
        submission_url="The URL of the submission (from the submissions channel)",
        point_change="Amount to add (positive) or subtract (negative)"
    )
    async def modify_points(
        self,
        ctx: commands.Context,
        member: discord.Member,
        submission_url: str,
        point_change: int
    ):
        """
        Modify points for a specific submission. Admin only.
        Use positive numbers to add points, negative to subtract.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param ctx: The command context
        :param member: The member whose submission to modify
        :param submission_url: The submission URL (unique identifier)
        :param point_change: Amount to add or subtract
        """
        # Find which team the member is on
        member_team = get_user_team(self.artfight_repo, ctx.guild.id, member.id)
        if member_team is None:
            await ctx.reply(f"❌ {member.mention} is not registered in artfight.", ephemeral=True)
            return
        
        # Get the submission
        submission = self.artfight_repo.get_team_member_submission(
            ctx.guild.id, member_team, member.id, submission_url
        )
        if submission is None:
            await ctx.reply(
                f"❌ Could not find a submission with that URL for {member.mention}.\n"
                f"Make sure you copied the full URL from the submission embed.",
                ephemeral=True
            )
            return
        
        old_points = submission.get('points', 0)
        title = submission.get('title', 'Untitled')
        
        # Apply the modification
        new_points = self.artfight_repo.modify_submission_points(
            ctx.guild.id, member_team, member.id, submission_url, point_change
        )
        
        if new_points is None:
            await ctx.reply("❌ Failed to modify points.", ephemeral=True)
            return
        
        points_name = self.artfight_repo.get_points_name(ctx.guild.id)
        
        # Build confirmation embed
        embed = discord.Embed(
            title="✅ Points Modified",
            color=discord.Color.green() if point_change >= 0 else discord.Color.orange()
        )
        embed.add_field(name="Member", value=member.mention, inline=True)
        embed.add_field(name="Submission", value=title, inline=True)
        embed.add_field(name="Change", value=f"{point_change:+d} {points_name}", inline=True)
        embed.add_field(name="Before", value=f"{old_points} {points_name}", inline=True)
        embed.add_field(name="After", value=f"{new_points} {points_name}", inline=True)
        embed.set_footer(text=f"Modified by {ctx.author}")
        
        await ctx.reply(embed=embed)
        self.bot.logger.info(
            f"Points modified for {member.id} submission '{title}': {old_points} -> {new_points} "
            f"(delta: {point_change}) by {ctx.author.id}"
        )

    @commands.hybrid_command(name="remove_member", brief="Remove a member from artfight")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @app_commands.describe(
        member="The member to remove from artfight",
        keep_submissions="Keep this member's submissions and points on the board? (Default: Yes)"
    )
    async def remove_member(
        self,
        ctx: commands.Context,
        member: discord.Member,
        keep_submissions: bool = True
    ):
        """
        Remove a member from artfight. Admin only.
        Removes the member from internal data and their team/artfight roles.
        
        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0
        
        :param ctx: The command context
        :param member: The Discord member to remove
        :param keep_submissions: Whether to keep their submissions (True) or remove them (False)
        """
        # Find which team the member is on
        member_team = get_user_team(self.artfight_repo, ctx.guild.id, member.id)
        if member_team is None:
            await ctx.reply(f"❌ {member.mention} is not registered in artfight.", ephemeral=True)
            return
        
        # Get member data for the confirmation embed
        member_data = self.artfight_repo.get_team_member(ctx.guild.id, member_team, member.id)
        points = member_data.get('points', 0) if member_data else 0
        submissions = member_data.get('submissions', {}) if member_data else {}
        submission_count = len(submissions)
        
        # Get team role
        teams = self.artfight_repo.get_teams(ctx.guild.id)
        team_role_id = teams.get(member_team)
        team_role = ctx.guild.get_role(team_role_id) if team_role_id else None
        
        # Get artfight role
        artfight_role_id = self.artfight_repo.get_artfight_role(ctx.guild.id)
        artfight_role = ctx.guild.get_role(artfight_role_id) if artfight_role_id else None
        
        points_name = self.artfight_repo.get_points_name(ctx.guild.id)
        
        # Build confirmation embed
        embed = discord.Embed(
            title="⚠️ Confirm Member Removal",
            color=discord.Color.orange()
        )
        embed.add_field(name="Member", value=member.mention, inline=True)
        embed.add_field(name="Team", value=team_role.mention if team_role else member_team, inline=True)
        embed.add_field(name="Points", value=f"{points} {points_name}", inline=True)
        embed.add_field(name="Submissions", value=str(submission_count), inline=True)
        embed.add_field(
            name="Keep Submissions?",
            value="✅ Yes - Points stay on the board" if keep_submissions else "❌ No - Points will be removed",
            inline=False
        )
        embed.set_footer(text="This action cannot be undone!")
        
        # Store references for the view callbacks
        artfight_repo = self.artfight_repo
        bot = self.bot
        guild_id = ctx.guild.id
        
        class RemoveMemberView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.result = None
            
            @discord.ui.button(label="Remove Member", style=discord.ButtonStyle.danger, emoji="🗑️")
            async def confirm_remove(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("Only the command invoker can confirm.", ephemeral=True)
                    return
                
                try:
                    # Remove from repo (this handles point deduction if keep_submissions is False)
                    if not keep_submissions:
                        # Remove all submissions first (this deducts points)
                        for sub_url in list(submissions.keys()):
                            artfight_repo.remove_team_member_submission(guild_id, member_team, member.id, sub_url)
                    
                    # Remove member from repo
                    artfight_repo.remove_team_member(guild_id, member_team, member.id)
                    
                    # Remove roles
                    roles_to_remove = []
                    if team_role:
                        roles_to_remove.append(team_role)
                    if artfight_role:
                        roles_to_remove.append(artfight_role)
                    
                    role_removal_errors = []
                    if roles_to_remove:
                        try:
                            await member.remove_roles(*roles_to_remove)
                        except discord.Forbidden:
                            role_removal_errors.append("Missing permissions to remove roles")
                        except discord.HTTPException as e:
                            role_removal_errors.append(f"Failed to remove roles: {e}")
                    
                    # Build result message
                    result_embed = discord.Embed(
                        title="✅ Member Removed",
                        color=discord.Color.green()
                    )
                    result_embed.add_field(name="Member", value=member.mention, inline=True)
                    result_embed.add_field(name="Team", value=member_team, inline=True)
                    
                    if keep_submissions:
                        result_embed.add_field(
                            name="Submissions",
                            value=f"Kept {submission_count} submission(s) ({points} {points_name})",
                            inline=False
                        )
                    else:
                        result_embed.add_field(
                            name="Submissions",
                            value=f"Removed {submission_count} submission(s) ({points} {points_name} deducted)",
                            inline=False
                        )
                    
                    if role_removal_errors:
                        result_embed.add_field(
                            name="⚠️ Role Removal Issues",
                            value="\n".join(role_removal_errors),
                            inline=False
                        )
                    
                    await interaction.response.edit_message(embed=result_embed, view=None)
                    bot.logger.info(f"Member {member.id} removed from artfight in guild {guild_id} by {ctx.author.id}")
                    self.result = "removed"
                    
                except Exception as e:
                    await interaction.response.send_message(f"❌ Error removing member: {e}", ephemeral=True)
                    bot.logger.error(f"Error removing member {member.id}: {e}")
                    self.result = "error"
                
                self.stop()
            
            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("Only the command invoker can cancel.", ephemeral=True)
                    return
                
                await interaction.response.edit_message(
                    embed=discord.Embed(title="❌ Cancelled", color=discord.Color.grey()),
                    view=None
                )
                self.result = "cancelled"
                self.stop()
        
        view = RemoveMemberView()
        await ctx.reply(embed=embed, view=view)
        await view.wait()
        
        if view.result is None:
            # Timed out
            await ctx.channel.send("Member removal timed out.", reference=ctx.message)
