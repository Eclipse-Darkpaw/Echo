import asyncio
import discord

from datetime import datetime, timedelta, timezone
from discord import app_commands
from discord.ext import commands

from base_bot import EchoBot
from modules.purge_ui import SurvivePurgeView, build_survive_embed
from util.progress_tracker import ProgressTracker


class Purge(commands.GroupCog, name="purge", description="Commands for managing inactive members"):
    """
    Cog for identifying inactive server members by scanning message history.
    
    Last docstring edit: -FoxyHunter V4.5.0
    Last class edit: -FoxyHunter V4.5.0
    """
    
    # Retry configuration for failed channel scans
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 5
    
    # Rate limiting delays
    CHANNEL_SCAN_DELAY = 0.5  # Delay between channels
    MESSAGE_BATCH_DELAY = 0.1  # Small delay during message iteration
    
    def __init__(self, bot: EchoBot):
        self.bot = bot
        
        # Persistent view for survive button
        self._survive_view = SurvivePurgeView()
        
        self.bot.logger.info(f'✔ Purge cog loaded')
    
    async def cog_load(self):
        """Called when the cog is loaded. Registers persistent views."""
        repo = self._get_repo()
        self._survive_view.set_repo(repo)
        self.bot.add_view(self._survive_view)
    
    def _get_repo(self):
        """Get the servers settings repository."""
        return self.bot.repositories.get('servers_settings_repo')
    
    async def _auto_populate_ignored_members(self, guild: discord.Guild) -> list[int]:
        """
        Auto-populate ignored members list with members who have roles
        higher than the bot's highest role.
        
        :param guild: The guild to check
        :return: List of member IDs to ignore
        """
        bot_member = guild.me
        bot_top_role = bot_member.top_role
        
        ignored_ids = []
        for member in guild.members:
            if member.bot:
                # Always ignore bots
                ignored_ids.append(member.id)
            elif member.top_role > bot_top_role:
                # Ignore members with higher roles than the bot
                ignored_ids.append(member.id)
        
        return ignored_ids
    
    async def _get_ignored_members(self, guild: discord.Guild) -> set[int]:
        """
        Get the set of member IDs to ignore during purge analysis.
        Always re-checks for members above bot's role to catch new mods.
        
        :param guild: The guild to get ignored members for
        :return: Set of member IDs to ignore
        """
        repo = self._get_repo()
        guild_id = str(guild.id)
        
        # Get stored ignored members
        stored_ignored = repo.get_purge_ignored_members(guild_id) or []
        
        # Always refresh: add any members currently above bot's role + bots
        # This catches newly promoted mods
        current_auto_ignored = await self._auto_populate_ignored_members(guild)
        
        # Merge: stored list + current auto-detected (in case someone was manually added)
        merged = set(stored_ignored) | set(current_auto_ignored)
        
        # Update storage if changed
        if set(stored_ignored) != merged:
            repo.set_purge_ignored_members(guild_id, list(merged))
            self.bot.logger.info(
                f'Updated ignored members for purge in {guild.name}: {len(merged)} total'
            )
        
        return merged
    
    def _get_survivors(self, guild_id: str) -> set[int]:
        """
        Get the set of member IDs who clicked the survive button.
        
        :param guild_id: The guild ID
        :return: Set of survivor member IDs
        """
        repo = self._get_repo()
        survivors = repo.get_purge_survivors(guild_id) or []
        return set(survivors)
    
    def _get_readable_channels(self, guild: discord.Guild) -> list[discord.TextChannel]:
        """
        Get all text channels the bot can read message history from.
        
        :param guild: The guild to check channels in
        :return: List of readable text channels
        """
        readable = []
        for channel in guild.text_channels:
            permissions = channel.permissions_for(guild.me)
            if permissions.read_message_history and permissions.view_channel:
                readable.append(channel)
        return readable
    
    async def _scan_channel_history(
        self,
        channel: discord.TextChannel,
        cutoff_date: datetime,
        active_users: set[int],
        ignored_users: set[int],
        progress_tracker: ProgressTracker,
        channel_index: int,
        total_channels: int
    ) -> bool:
        """
        Scan a channel's message history and collect active user IDs.
        Implements retry logic for resilience.
        
        :param channel: The channel to scan
        :param cutoff_date: Only consider messages after this date
        :param active_users: Set to add active user IDs to (modified in place)
        :param ignored_users: Set of user IDs to ignore (not added to active_users)
        :param progress_tracker: Progress tracker for status updates
        :param channel_index: Current channel index (1-based)
        :param total_channels: Total number of channels to scan
        :return: True if scan succeeded, False if all retries failed
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                message_count = 0
                retry_text = f" (retry {attempt})" if attempt > 1 else ""
                
                progress_tracker.update(
                    status=f"Channel: #{channel.name} ({channel_index}/{total_channels})\n"
                           f"Reading messages...{retry_text}\n"
                           f"Active users found: {len(active_users)}"
                )
                await progress_tracker.send_update()
                
                async for message in channel.history(
                    limit=None,
                    after=cutoff_date,
                    oldest_first=False
                ):
                    # Only count non-ignored users as active
                    if message.author.id not in ignored_users:
                        active_users.add(message.author.id)
                    message_count += 1
                    
                    # Periodic progress update and small delay
                    if message_count % 500 == 0:
                        progress_tracker.update(
                            status=f"Channel: #{channel.name} ({channel_index}/{total_channels})\n"
                                   f"Read {message_count} messages...\n"
                                   f"Active users found: {len(active_users)}"
                        )
                        await progress_tracker.send_update()
                        await asyncio.sleep(self.MESSAGE_BATCH_DELAY)
                
                self.bot.logger.info(
                    f'Scanned #{channel.name}: {message_count} messages, {len(active_users)} active users so far'
                )
                return True
                
            except discord.Forbidden:
                # Permission error - skip this channel
                self.bot.logger.warning(
                    f'Permission denied for #{channel.name}, skipping'
                )
                return True  # Don't retry permission errors
                
            except Exception as e:
                self.bot.logger.warning(
                    f'Error scanning #{channel.name} (attempt {attempt}/{self.MAX_RETRIES}): {e}'
                )
                
                if attempt < self.MAX_RETRIES:
                    progress_tracker.update(
                        status=f"Channel: #{channel.name} ({channel_index}/{total_channels})\n"
                               f"Error, retrying in {self.RETRY_DELAY_SECONDS}s... (attempt {attempt}/{self.MAX_RETRIES})"
                    )
                    await progress_tracker.send_update()
                    await asyncio.sleep(self.RETRY_DELAY_SECONDS)
                else:
                    self.bot.logger.error(
                        f'Failed to scan #{channel.name} after {self.MAX_RETRIES} attempts'
                    )
                    return False
        
        return False
    
    def _format_inactive_list(
        self,
        inactive_members: list[discord.Member],
        ignored_members_in_server: list[discord.Member],
        survivor_count: int,
        days: int,
        channels_scanned: int,
        total_members: int,
        active_count: int,
        failed_channels: list[str]
    ) -> list[str]:
        """
        Format the inactive members list into Discord messages.
        Splits into multiple messages if needed to stay under 2000 char limit.
        
        :param inactive_members: List of inactive members
        :param ignored_members_in_server: List of ignored members currently in server
        :param survivor_count: Number of members who clicked the survive button
        :param days: Number of days checked
        :param channels_scanned: Number of channels scanned
        :param total_members: Total member count (excluding bots)
        :param active_count: Number of active members found
        :param failed_channels: List of channel names that failed to scan
        :return: List of message strings
        """
        messages = []
        
        # Header
        header = (
            f"**Inactive Members Report**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"**Period:** Last {days} days\n"
            f"**Channels scanned:** {channels_scanned}\n"
            f"**Total server members:** {total_members} (excl. bots)\n"
            f"**Active members:** {active_count}\n"
            f"**Survivors (button):** {survivor_count}\n"
            f"**Ignored members:** {len(ignored_members_in_server)}\n"
        )
        
        if ignored_members_in_server:
            ignored_names = ", ".join(m.display_name for m in ignored_members_in_server[:10])
            if len(ignored_members_in_server) > 10:
                ignored_names += f" (+{len(ignored_members_in_server) - 10} more)"
            header += f"-# Ignored: {ignored_names}\n"
        
        if failed_channels:
            header += f"**Failed channels:** {', '.join(failed_channels)}\n"
        
        header += f"\n**Inactive Members ({len(inactive_members)}):**\n"
        
        if not inactive_members:
            header += "_Nauurrr I really wanted there to be some people to go boom, but sad, seems like I found no inactive peoples smh_"
            return [header]
        
        # Build message chunks with member mentions
        current_message = header
        max_length = 1900  # Leave some buffer below 2000
        
        for i, member in enumerate(inactive_members):
            mention = f"<@{member.id}>"
            separator = ", " if i < len(inactive_members) - 1 else ""
            addition = mention + separator
            
            if len(current_message) + len(addition) > max_length:
                messages.append(current_message)
                current_message = addition
            else:
                current_message += addition
        
        if current_message:
            messages.append(current_message)
        
        return messages
    
    @app_commands.command(
        name="list-inactive",
        description="🔐 manage_roles | List members inactive for X days"
    )
    @app_commands.describe(
        days="Number of days to look back (default: 93, ~3 months)",
        exclude_survivors="Exclude members protected by the survive button (default: True)"
    )
    @app_commands.guild_only()
    async def list_inactive_members(
        self, 
        interaction: discord.Interaction, 
        days: int = 93,
        exclude_survivors: bool = True
    ):
        """
        🔐 manage_roles | List server members who haven't sent a message in X days
        
        Scans all accessible channels for message history and identifies
        members who have not sent any messages within the specified time period.
        This operation may take a long time for large servers.
        
        Last docstring edit: -FoxyHunter V4.5.0
        Last method edit: -FoxyHunter V4.5.0
        
        :param ctx: Context object for the invoked command
        :param days: Number of days to look back (default: 93, ~3 months)
        :return: None
        """
        # Permission check
        if not (interaction.user.guild_permissions.manage_roles or 
                str(interaction.user.id) in self.bot.config.guardians):
            await interaction.response.send_message("Nah, not doing that for you, get permissions first 🙄")
            return
        
        if days < 1:
            await interaction.response.send_message("You really wanna blow up the whole server huh, nah, not doing it 🥰")
            return
        
        if days > 365:
            await interaction.response.send_message("Brooo!! nahh that's too much work, 365 max I'll go, gotta purge at least some people 💥")
            return
        
        # Send initial loading message
        await interaction.response.send_message("```\nLoading data...\n```")
        message = await interaction.original_response()
        
        # Setup progress tracker
        progress = ProgressTracker(min_update_interval=3.0)
        progress.set_message(message)
        
        try:
            # Get ignored members
            progress.update(
                status="Lemme see...\nLoading ignored members list",
                progress=0
            )
            await progress.force_update()
            
            ignored_members = await self._get_ignored_members(interaction.guild)
            
            # Get readable channels
            progress.update(
                status="Prying through ya server...\nFinding accessible channels",
                progress=5
            )
            await progress.force_update()
            
            channels = self._get_readable_channels(interaction.guild)
            
            if not channels:
                await message.edit(content="I can't find shit, lemme at least see some channels ya baffoon")
                return
            
            progress.update(
                status=f"Found {len(channels)} channels\nStarting scan...",
                progress=10
            )
            await progress.force_update()
            
            # Calculate cutoff date
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Scan all channels
            active_users: set[int] = set()
            failed_channels: list[str] = []
            
            for i, channel in enumerate(channels, 1):
                # Calculate progress (10% to 85% for channel scanning)
                channel_progress = 10 + (75 * i / len(channels))
                progress.update(progress=channel_progress)
                
                success = await self._scan_channel_history(
                    channel=channel,
                    cutoff_date=cutoff_date,
                    active_users=active_users,
                    ignored_users=ignored_members,
                    progress_tracker=progress,
                    channel_index=i,
                    total_channels=len(channels)
                )
                
                if not success:
                    failed_channels.append(f"#{channel.name}")
                
                # Small delay between channels to respect rate limits
                await asyncio.sleep(self.CHANNEL_SCAN_DELAY)
            
            # Fetch all guild members (excluding bots AND ignored members)
            progress.update(
                status=f"Wrapping up...\nFetching member list\nActive users found: {len(active_users)}",
                progress=90
            )
            await progress.force_update()
            
            # Force fetch members - get ALL non-bot members first
            all_server_members = []
            async for member in interaction.guild.fetch_members(limit=None):
                if not member.bot:
                    all_server_members.append(member)
            
            # Separate ignored members from consideration
            ignored_members_in_server = [
                m for m in all_server_members if m.id in ignored_members
            ]
            
            # "Considered" members = everyone except bots and ignored
            # These are the only members we care about for active/inactive
            considered_members = [
                m for m in all_server_members if m.id not in ignored_members
            ]
            
            # Get survivors (users who clicked the survive button)
            guild_id = str(interaction.guild.id)
            survivors = self._get_survivors(guild_id) if exclude_survivors else set()
            
            # Active = considered members who sent a message
            active_members_list = [
                m for m in considered_members if m.id in active_users
            ]
            
            # Inactive = considered members who did NOT send a message AND are not survivors (if excluding)
            inactive_members = [
                m for m in considered_members 
                if m.id not in active_users and m.id not in survivors
            ]
            
            # Count survivors who are still in the server and would have been inactive
            survivor_members = [
                m for m in considered_members 
                if m.id in survivors and m.id not in active_users
            ] if exclude_survivors else []
            
            # Debug logging
            self.bot.logger.info(
                f'Purge debug - All server members (non-bot): {[m.display_name for m in all_server_members]}'
            )
            self.bot.logger.info(
                f'Purge debug - Ignored (not considered): {[m.display_name for m in ignored_members_in_server]}'
            )
            self.bot.logger.info(
                f'Purge debug - Considered members: {[m.display_name for m in considered_members]}'
            )
            self.bot.logger.info(
                f'Purge debug - Active: {[m.display_name for m in active_members_list]}'
            )
            self.bot.logger.info(
                f'Purge debug - Survivors (button): {[m.display_name for m in survivor_members]}'
            )
            self.bot.logger.info(
                f'Purge debug - Inactive: {[m.display_name for m in inactive_members]}'
            )
            
            # Sort by join date (oldest first) for easier review
            inactive_members.sort(key=lambda m: m.joined_at or datetime.min.replace(tzinfo=timezone.utc))
            
            progress.update(
                status="Looks about right 🥱\nWriting it down...",
                progress=95
            )
            await progress.force_update()
            
            # Stats are based on considered members only
            active_count = len(active_members_list)
            
            # Format and send results
            result_messages = self._format_inactive_list(
                inactive_members=inactive_members,
                ignored_members_in_server=ignored_members_in_server,
                days=days,
                channels_scanned=len(channels),
                total_members=len(considered_members),
                active_count=active_count,
                failed_channels=failed_channels,
                survivor_count=len(survivor_members)
            )
            
            # Edit original message with first result, send rest as follow-ups
            await message.edit(content=result_messages[0])
            
            for msg_content in result_messages[1:]:
                await interaction.followup.send(msg_content)
            
            self.bot.logger.info(
                f'Purge scan complete for {interaction.guild.name}: '
                f'{len(inactive_members)} inactive / {len(active_members_list)} active / '
                f'{len(survivor_members)} survivors / {len(ignored_members_in_server)} ignored / '
                f'{len(considered_members)} considered'
            )
            
            # Sanity check: active + inactive + survivors should equal considered
            accounted = len(inactive_members) + len(active_members_list) + len(survivor_members)
            if accounted != len(considered_members):
                self.bot.logger.warning(
                    f'Purge sanity check FAILED: {accounted} (active+inactive+survivors) != {len(considered_members)} considered'
                )
            
        except Exception as e:
            self.bot.logger.error(f'Error in list_inactive_members: {e}', exc_info=True)
            await message.edit(
                content=f"An error occurred during the scan:\n```\n{str(e)[:500]}\n```"
            )
    
    @app_commands.command(
        name="send-button",
        description="Send a 'Survive Purge' button in this channel"
    )
    @app_commands.default_permissions(administrator=True)
    async def send_survive_button(
        self,
        interaction: discord.Interaction
    ):
        """Send a persistent 'Survive Purge' button in the current channel."""
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message(
                "This command can only be used in text channels.",
                ephemeral=True
            )
            return
        
        # Check bot permissions in channel
        bot_permissions = interaction.channel.permissions_for(interaction.guild.me)
        if not bot_permissions.send_messages or not bot_permissions.embed_links:
            await interaction.response.send_message(
                "I don't have permission to send messages or embeds here.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            from modules.purge_ui import SurvivePurgeView, build_survive_embed
            
            embed = build_survive_embed()
            view = SurvivePurgeView(self._get_repo())
            
            await interaction.channel.send(embed=embed, view=view)
            
            await interaction.followup.send(
                "✅ Survive button sent!",
                ephemeral=True
            )
            
            self.bot.logger.info(
                f'Survive button sent in #{interaction.channel.name} ({interaction.guild.name}) '
                f'by {interaction.user.name}'
            )
            
        except Exception as e:
            self.bot.logger.error(f'Error sending survive button: {e}', exc_info=True)
            await interaction.followup.send(
                f"Failed to send survive button: {str(e)[:200]}",
                ephemeral=True
            )
    
    @app_commands.command(
        name="list-survivors",
        description="List all members who have clicked the survive button"
    )
    @app_commands.default_permissions(administrator=True)
    async def list_survivors(self, interaction: discord.Interaction):
        """List all members who have marked themselves as survivors."""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = str(interaction.guild.id)
        survivors = self._get_survivors(guild_id)
        
        if not survivors:
            await interaction.followup.send(
                "No members have clicked the survive button yet.",
                ephemeral=True
            )
            return
        
        # Get member objects for survivors who are still in the server
        survivor_members = []
        left_count = 0
        
        for user_id in survivors:
            member = interaction.guild.get_member(user_id)
            if member:
                survivor_members.append(member)
            else:
                left_count += 1
        
        if not survivor_members and left_count > 0:
            await interaction.followup.send(
                f"All {left_count} survivor(s) have left the server.",
                ephemeral=True
            )
            return
        
        # Format the list
        lines = [f"**Survivors ({len(survivor_members)})**"]
        if left_count > 0:
            lines.append(f"*({left_count} survivors have left the server)*")
        lines.append("")
        
        for member in survivor_members:
            lines.append(f"• {member.mention} ({member.display_name})")
        
        await interaction.followup.send("\n".join(lines), ephemeral=True)
    
    @app_commands.command(
        name="clear-survivors",
        description="Clear all survivors from the list"
    )
    @app_commands.default_permissions(administrator=True)
    async def clear_survivors(self, interaction: discord.Interaction):
        """Clear all members from the survivors list."""
        guild_id = str(interaction.guild.id)
        survivors = self._get_survivors(guild_id)
        
        if not survivors:
            await interaction.response.send_message(
                "The survivors list is already empty.",
                ephemeral=True
            )
            return
        
        count = len(survivors)
        self._get_repo().set_purge_survivors(guild_id, set())
        
        await interaction.response.send_message(
            f"Cleared {count} member(s) from the survivors list.",
            ephemeral=True
        )
        
        self.bot.logger.info(
            f'Survivors list cleared in {interaction.guild.name} by {interaction.user.name} '
            f'({count} survivors removed)'
        )


async def setup(bot: EchoBot):
    await bot.add_cog(Purge(bot))
