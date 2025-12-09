import discord
import datetime

from base_bot import EchoBot
from discord.ui import Modal, Select, TextInput, View
from repositories import ArtfightRepo
from util import (
    date_to_utc_midnight_unix_timestamp,
    time_to_utc_at_epoch_timestamp
)

def artfight_configuration_embed(artfight_repo: ArtfightRepo, guild_id) -> discord.Embed:
    start_date = artfight_repo.get_start_date(guild_id)
    end_date = artfight_repo.get_end_date(guild_id)
    next_prompt_hour = artfight_repo.get_next_prompt_hour(guild_id)
    artfight_role = artfight_repo.get_artfight_role(guild_id)
    points_name = artfight_repo.get_points_name(guild_id)

    start_date_unix = date_to_utc_midnight_unix_timestamp(start_date) if start_date else None
    end_date_unix = date_to_utc_midnight_unix_timestamp(end_date) if end_date else None
    next_prompt_hour_unix = time_to_utc_at_epoch_timestamp(next_prompt_hour) if next_prompt_hour else None

    # Format dates - UTC underneath
    if start_date:
        start_str = f'<t:{start_date_unix}:d>\n`{start_date.strftime("%Y-%m-%d")}`'
    else:
        start_str = '*not set*'
    
    if end_date:
        end_str = f'<t:{end_date_unix}:d>\n`{end_date.strftime("%Y-%m-%d")}`'
    else:
        end_str = '*not set*'
    
    if next_prompt_hour:
        time_str = f'<t:{next_prompt_hour_unix}:t>\n`{next_prompt_hour.strftime("%H:%M")} UTC`'
    else:
        time_str = '*not set*'

    # Teams
    teams = artfight_repo.get_teams(guild_id)
    if teams:
        team_list = '\n'.join(f'• {name}: <@&{role_id}>' for name, role_id in teams.items())
    else:
        team_list = '*No teams set*'

    # Daily Prompts
    prompts = artfight_repo.get_prompts(guild_id) or {}
    if prompts:
        prompt_entries = []
        for day_str in sorted(prompts.keys(), key=lambda x: int(x)):
            prompt = prompts[day_str]
            prompt_short = (prompt[:30] + '..') if len(prompt) > 32 else prompt
            prompt_entries.append(f'`{int(day_str):2}` {prompt_short}')
        prompts_content = '\n'.join(prompt_entries)
    else:
        prompts_content = '*No prompts set*'

    # Daily Yaps
    yaps = artfight_repo.get_yap_messages(guild_id) or {}
    if yaps:
        yap_entries = []
        for day_str in sorted(yaps.keys(), key=lambda x: int(x)):
            yap = yaps[day_str]
            yap_short = (yap[:30] + '..') if len(yap) > 32 else yap
            yap_entries.append(f'`{int(day_str):2}` {yap_short}')
        yaps_content = '\n'.join(yap_entries)
    else:
        yaps_content = '*No yaps set*'

    # Build embed with white sidebar
    embed = discord.Embed(
        title='Artfight Configuration',
        color=discord.Color.from_rgb(255, 255, 255),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    # General settings
    embed.add_field(
        name='Artfight Role',
        value=f'<@&{artfight_role}>' if artfight_role else '*not set*',
        inline=True
    )
    embed.add_field(
        name='Points Name/Symbol',
        value=points_name,
        inline=True
    )
    embed.add_field(name='', value='', inline=True)

    # Schedule
    embed.add_field(name='Start Date', value=start_str, inline=True)
    embed.add_field(name='End Date', value=end_str, inline=True)
    embed.add_field(name='Prompt Time', value=time_str, inline=True)

    # Channels
    sub_ch = artfight_repo.get_submissions_channel(guild_id)
    prompt_ch = artfight_repo.get_prompts_channel(guild_id)
    embed.add_field(
        name='Submissions Channel',
        value=f'<#{sub_ch}>' if sub_ch else '*not set*',
        inline=True
    )
    embed.add_field(
        name='Prompts Channel',
        value=f'<#{prompt_ch}>' if prompt_ch else '*not set*',
        inline=True
    )
    embed.add_field(name='', value='', inline=True)

    # Teams
    embed.add_field(name='Teams', value=team_list, inline=False)

    # Daily Prompts
    embed.add_field(
        name='Daily Prompts',
        value=prompts_content[:1024] if len(prompts_content) > 1024 else prompts_content,
        inline=True
    )

    # Daily Yaps
    embed.add_field(
        name='Daily Yaps',
        value=yaps_content[:1024] if len(yaps_content) > 1024 else yaps_content,
        inline=True
    )

    embed.set_footer(text='⚠️ Changes take effect immediately! Use /artfight archive to backup first.')

    return embed    

class ChannelSelect(Select):
    def __init__(
        self,
        channel_type: str,
        placeholder: str,
        *,
        channels: list[discord.TextChannel],
        current_channel_id: int | None
    ):
        options: list[discord.SelectOption] = []

        for channel in channels[:25]:
            label = f'#{channel.name}'
            options.append(discord.SelectOption(
                label=label[:100],
                description=f'ID: {channel.id}'[:100],
                value=str(channel.id),
                default=(current_channel_id == channel.id)
            ))

        if not options:
            options = [discord.SelectOption(label='No text channels available', value='noop', default=True)]

        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, disabled=(options[0].value == 'noop'))
        self.channel_type = channel_type

    async def callback(self, interaction: discord.Interaction):
        if self.disabled:
            await interaction.response.send_message('⚠ No channels available for selection.', ephemeral=True)
            return

        selected_channel_id = int(self.values[0])
        view: 'ChannelSelectView' = self.view  # type: ignore
        await view.handle_channel_selection(interaction, self.channel_type, selected_channel_id)


class ChannelSelectView(View):
    def __init__(self, repository: ArtfightRepo, guild: discord.Guild, update_callback):
        super().__init__(timeout=120)
        self.repository = repository
        self.guild = guild
        self.update_callback = update_callback

        available_channels = self._get_channel_candidates()
        submission_id = repository.get_submissions_channel(guild.id)
        prompts_id = repository.get_prompts_channel(guild.id)

        self.add_item(ChannelSelect(
            'submissions',
            placeholder='Select submissions channel',
            channels=available_channels,
            current_channel_id=submission_id
        ))
        self.add_item(ChannelSelect(
            'prompts',
            placeholder='Select prompts channel',
            channels=available_channels,
            current_channel_id=prompts_id
        ))

    def _get_channel_candidates(self) -> list[discord.TextChannel]:
        me = self.guild.me
        channels = [
            channel for channel in self.guild.text_channels
            if me is None or channel.permissions_for(me).view_channel
        ]
        channels.sort(key=lambda c: c.position)
        return channels

    async def handle_channel_selection(self, interaction: discord.Interaction, channel_type: str, channel_id: int):
        try:
            if channel_type == 'submissions':
                self.repository.set_submissions_channel(self.guild.id, channel_id)
            else:
                self.repository.set_prompts_channel(self.guild.id, channel_id)
        except Exception as exc:
            await interaction.response.send_message(f'❌ Failed to update channel: `{exc}`', ephemeral=True)
            return

        await interaction.response.send_message('✔ Channel updated', ephemeral=True)
        await self.update_callback(interaction)

class DateSetup(Modal):
    def __init__(self, repository: ArtfightRepo, guild_id: int, update_callback):
        super().__init__(title='Artfight Dates & Prompt Time Configuration')
        self.add_item(TextInput(
            label='Start Date (YYYY-MM-DD) UTC 00:00 day start',
            placeholder='e.g. 2025-03-01',
            default=(date.strftime('%Y-%m-%d') if (date := repository.get_start_date(guild_id=guild_id)) else None)
        ))
        self.add_item(TextInput(
            label='End Date (YYYY-MM-DD) UTC 00:00 day start',
            placeholder='e.g. 2025-03-10',
            default=(date.strftime('%Y-%m-%d') if (date := repository.get_end_date(guild_id=guild_id)) else None)
        ))
        self.add_item(TextInput(
            label='Next Prompt Hour (HH:MM) in UTC time',
            placeholder="e.g. 18:00",
            default=(time.strftime('%H:%M') if (time := repository.get_next_prompt_hour(guild_id=guild_id)) else None)
        ))

        self.repository = repository
        self.update_callback = update_callback

    async def on_submit(self, interaction: discord.Interaction):
        start_date_str = self.children[0].value.strip()
        end_date_str = self.children[1].value.strip()
        next_prompt_hour_str = self.children[2].value.strip()
        import datetime
        try:
            start_date = datetime.date.fromisoformat(start_date_str)
            end_date = datetime.date.fromisoformat(end_date_str)
            next_prompt_hour = datetime.time.fromisoformat(next_prompt_hour_str)
        except Exception:
            await interaction.response.send_message('⚠ Invalid date/time format.', ephemeral=True)
            return

        try:
            self.repository.set_start_date(guild_id=interaction.guild.id, date=start_date)
            self.repository.set_end_date(guild_id=interaction.guild.id, date=end_date)
            self.repository.set_next_prompt_hour(guild_id=interaction.guild.id, time=next_prompt_hour)
        except Exception as e:
            await interaction.response.send_message(f'❌ Failed to update:\n```\n{e}\n```', ephemeral=True)

        await interaction.response.send_message('✔ Dates and prompt time updated', ephemeral=True)
        await self.update_callback(interaction)

class SetTeam(Modal):
    def __init__(self, repository: ArtfightRepo, update_callback):
        super().__init__(title='Add a Team')
        self.add_item(TextInput(label='Team Name', placeholder='Enter team name'))
        self.add_item(TextInput(label='Team Role ID', placeholder='Enter role ID or mention'))

        self.repository = repository
        self.update_callback = update_callback

    async def on_submit(self, interaction: discord.Interaction):
        team_name = self.children[0].value.strip()
        team_role = self.children[1].value.strip()

        try:
            team_role_id = int(team_role.strip('<@&>'))
        except Exception:
            await interaction.response.send_message('Invalid role ID.', ephemeral=True)
            return
        
        try:
            self.repository.add_team(guild_id=interaction.guild.id, name=team_name, role_id=team_role_id)
        except Exception as e:
            await interaction.response.send_message(f'❌ Failed to update:\n```\n{e}\n```', ephemeral=True)

        await interaction.response.send_message(f'✔ Team "{team_name}" added', ephemeral=True)
        await self.update_callback(interaction)

class RemoveTeam(Modal):
    def __init__(self, repository: ArtfightRepo, update_callback):
        super().__init__(title='Remove a Team')
        self.add_item(TextInput(label='Team Name', placeholder='Enter team name'))

        self.repository = repository
        self.update_callback = update_callback

    async def on_submit(self, interaction: discord.Interaction):
        team_name = self.children[0].value.strip()
        
        try:
            self.repository.remove_team(guild_id=interaction.guild.id, name=team_name)
        except Exception as e:
            await interaction.response.send_message(f'❌ Failed to update:\n```\n{e}\n```', ephemeral=True)

        await interaction.response.send_message(f'✔ Team "{team_name}" removed')
        await self.update_callback(interaction)


class PromptDaySelect(Select):
    def __init__(self, repository: ArtfightRepo, guild_id: int):
        self.repository = repository
        self.guild_id = guild_id
        
        duration = repository.get_duration_in_days(guild_id) or 0
        prompts = repository.get_prompts(guild_id) or {}
        
        options = []
        for day in range(1, min(duration + 1, 26)):  # Max 25 options
            existing = prompts.get(str(day))
            if existing:
                label = f'Day {day} (overwrite)'
                desc = existing[:50] + '..' if len(existing) > 50 else existing
            else:
                label = f'Day {day} (new)'
                desc = 'No prompt set'
            options.append(discord.SelectOption(label=label, value=str(day), description=desc))
        
        if not options:
            options = [discord.SelectOption(label='No days available', value='0', description='Set dates first')]
        
        super().__init__(placeholder='Select a day', options=options)

    async def callback(self, interaction: discord.Interaction):
        view: 'SetPromptView' = self.view
        view.selected_day = int(self.values[0])
        
        if view.selected_day == 0:
            await interaction.response.send_message('Set start & end dates first.', ephemeral=True)
            return
        
        existing = self.repository.get_prompt(self.guild_id, view.selected_day)
        action = 'overwrite' if existing else 'set'
        
        await interaction.response.send_message(
            f'**{action.title()} prompt for Day {view.selected_day}**\n\n'
            f'Type your prompt message below.\n'
            f'-# Type `cancel` to abort.',
            ephemeral=True
        )
        await view.wait_for_prompt_message(interaction)


class SetPromptView(View):
    def __init__(self, bot: EchoBot, repository: ArtfightRepo, guild_id: int, update_callback):
        super().__init__(timeout=120)
        self.bot = bot
        self.repository = repository
        self.guild_id = guild_id
        self.update_callback = update_callback
        self.selected_day = None
        
        self.add_item(PromptDaySelect(repository, guild_id))

    async def wait_for_prompt_message(self, interaction: discord.Interaction):
        def check(m):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

        try:
            msg = await self.bot.wait_for('message', timeout=120.0, check=check)
            
            try:
                await msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

            if msg.content.lower().strip() == 'cancel':
                await interaction.followup.send('Cancelled.', ephemeral=True)
                return
            
            try:
                self.repository.add_prompt(self.guild_id, self.selected_day, msg.content)
                await interaction.followup.send(f'✔ Prompt for day {self.selected_day} set!', ephemeral=True)
                await self.update_callback(interaction)
            except Exception as e:
                await interaction.followup.send(f'❌ Failed: {e}', ephemeral=True)
                
        except TimeoutError:
            await interaction.followup.send('⏰ Timed out.', ephemeral=True)


class YapDaySelect(Select):
    def __init__(self, repository: ArtfightRepo, guild_id: int):
        self.repository = repository
        self.guild_id = guild_id
        
        duration = repository.get_duration_in_days(guild_id) or 0
        yaps = repository.get_yap_messages(guild_id) or {}
        
        options = []
        for day in range(1, min(duration + 1, 26)):  # Max 25 options
            existing = yaps.get(str(day))
            if existing:
                label = f'Day {day} (overwrite)'
                desc = existing[:50] + '..' if len(existing) > 50 else existing
            else:
                label = f'Day {day} (new)'
                desc = 'No yap set'
            options.append(discord.SelectOption(label=label, value=str(day), description=desc))
        
        if not options:
            options = [discord.SelectOption(label='No days available', value='0', description='Set dates first')]
        
        super().__init__(placeholder='Select a day', options=options)

    async def callback(self, interaction: discord.Interaction):
        view: 'SetYapView' = self.view
        view.selected_day = int(self.values[0])
        
        if view.selected_day == 0:
            await interaction.response.send_message('Set start & end dates first.', ephemeral=True)
            return
        
        existing = self.repository.get_yap_message(self.guild_id, view.selected_day)
        action = 'overwrite' if existing else 'set'
        
        await interaction.response.send_message(
            f'**{action.title()} yap for Day {view.selected_day}**\n\n'
            f'Type your yap message below. Emotes are supported!\n'
            f'-# Use server emotes or standard emotes for best compatibility.\n'
            f'-# Type `cancel` to abort.',
            ephemeral=True
        )
        await view.wait_for_yap_message(interaction)


class SetYapView(View):
    def __init__(self, bot: EchoBot, repository: ArtfightRepo, guild_id: int, update_callback):
        super().__init__(timeout=120)
        self.bot = bot
        self.repository = repository
        self.guild_id = guild_id
        self.update_callback = update_callback
        self.selected_day = None
        
        self.add_item(YapDaySelect(repository, guild_id))

    async def wait_for_yap_message(self, interaction: discord.Interaction):
        def check(m):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

        try:
            msg = await self.bot.wait_for('message', timeout=120.0, check=check)
            
            try:
                await msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

            if msg.content.lower().strip() == 'cancel':
                await interaction.followup.send('Cancelled.', ephemeral=True)
                return
            
            try:
                self.repository.add_yap_message(self.guild_id, self.selected_day, msg.content)
                await interaction.followup.send(f'✔ Yap for day {self.selected_day} set!', ephemeral=True)
                await self.update_callback(interaction)
            except Exception as e:
                await interaction.followup.send(f'❌ Failed: {e}', ephemeral=True)
                
        except TimeoutError:
            await interaction.followup.send('⏰ Timed out.', ephemeral=True)


class RemovePromptSelect(Select):
    def __init__(self, repository: ArtfightRepo, guild_id: int, update_callback):
        self.repository = repository
        self.guild_id = guild_id
        self.update_callback = update_callback
        
        prompts = repository.get_prompts(guild_id) or {}
        
        options = []
        for day_str in sorted(prompts.keys(), key=lambda x: int(x)):
            prompt = prompts[day_str]
            desc = prompt[:50] + '..' if len(prompt) > 50 else prompt
            options.append(discord.SelectOption(label=f'Day {day_str}', value=day_str, description=desc))
        
        if not options:
            options = [discord.SelectOption(label='No prompts to remove', value='0')]
        
        super().__init__(placeholder='Select a prompt to remove', options=options)

    async def callback(self, interaction: discord.Interaction):
        day = int(self.values[0])
        
        if day == 0:
            await interaction.response.edit_message(content='No prompts to remove.', view=None)
            return
        
        try:
            self.repository.remove_prompt(self.guild_id, day)
            await interaction.response.edit_message(content=f'✔ Prompt for day {day} removed', view=None)
            await self.update_callback(interaction)
        except Exception as e:
            await interaction.response.edit_message(content=f'❌ Failed: {e}', view=None)


class RemovePromptView(View):
    def __init__(self, repository: ArtfightRepo, guild_id: int, update_callback):
        super().__init__(timeout=60)
        self.add_item(RemovePromptSelect(repository, guild_id, update_callback))


class RemoveYapSelect(Select):
    def __init__(self, repository: ArtfightRepo, guild_id: int, update_callback):
        self.repository = repository
        self.guild_id = guild_id
        self.update_callback = update_callback
        
        yaps = repository.get_yap_messages(guild_id) or {}
        
        options = []
        for day_str in sorted(yaps.keys(), key=lambda x: int(x)):
            yap = yaps[day_str]
            desc = yap[:50] + '..' if len(yap) > 50 else yap
            options.append(discord.SelectOption(label=f'Day {day_str}', value=day_str, description=desc))
        
        if not options:
            options = [discord.SelectOption(label='No yaps to remove', value='0')]
        
        super().__init__(placeholder='Select a yap to remove', options=options)

    async def callback(self, interaction: discord.Interaction):
        day = int(self.values[0])
        
        if day == 0:
            await interaction.response.edit_message(content='No yaps to remove.', view=None)
            return
        
        try:
            self.repository.remove_yap_message(self.guild_id, day)
            await interaction.response.edit_message(content=f'✔ Yap for day {day} removed', view=None)
            await self.update_callback(interaction)
        except Exception as e:
            await interaction.response.edit_message(content=f'❌ Failed: {e}', view=None)


class RemoveYapView(View):
    def __init__(self, repository: ArtfightRepo, guild_id: int, update_callback):
        super().__init__(timeout=60)
        self.add_item(RemoveYapSelect(repository, guild_id, update_callback))


class RoleSelect(discord.ui.RoleSelect):
    def __init__(self, repository: ArtfightRepo, update_callback):
        current_text = "Select the Artfight role (given to all participants)"
        super().__init__(placeholder=current_text, min_values=0, max_values=1)
        self.repository = repository
        self.update_callback = update_callback

    async def callback(self, interaction: discord.Interaction):
        if self.values:
            selected_role = self.values[0]
            self.repository.set_artfight_role(interaction.guild.id, selected_role.id)
            await interaction.response.send_message(
                f'✔ Artfight role set to {selected_role.mention}\n\n'
                f'Now, **reply to this message** with what you want to call points (emotes welcome! 🎄⭐).\n'
                f'Or type `skip` to keep the current setting.',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'No role selected.\n\n'
                f'**Reply to this message** with what you want to call points (emotes welcome! 🎄⭐).\n'
                f'Or type `skip` to keep the current setting.',
                ephemeral=True
            )
        
        # Wait for message reply for points name
        view: 'GeneralSettingsView' = self.view
        await view.wait_for_points_name(interaction)


class GeneralSettingsView(View):
    def __init__(self, bot: EchoBot, repository: ArtfightRepo, guild_id: int, update_callback):
        super().__init__(timeout=120)
        self.bot = bot
        self.repository = repository
        self.guild_id = guild_id
        self.update_callback = update_callback
        
        self.add_item(RoleSelect(repository, update_callback))

    async def wait_for_points_name(self, interaction: discord.Interaction):
        """Wait for user to reply with points name."""
        def check(m):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            
            # Delete the user's message to keep things clean
            try:
                await msg.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

            if msg.content.lower().strip() != 'skip':
                self.repository.set_points_name(self.guild_id, msg.content.strip())
                await interaction.followup.send(f'✔ Points name set to: {msg.content.strip()}', ephemeral=True)
            else:
                await interaction.followup.send('✔ Points name unchanged.', ephemeral=True)
            
            await self.update_callback(interaction)
            
        except TimeoutError:
            await interaction.followup.send('⏰ Timed out waiting for points name. Role setting was saved.', ephemeral=True)
            await self.update_callback(interaction)


class ConfigurationView(View):
    def __init__(self, bot: EchoBot, repository: ArtfightRepo, guild_id: int):
        super().__init__(timeout=180)
        self.bot = bot
        self.repository = repository
        self.guild_id = guild_id
        self.message: discord.Message = None

    async def update_message(self, interaction: discord.Interaction):
        if self.message:
            new_embed = artfight_configuration_embed(self.repository, self.guild_id)
            await self.message.edit(content=None, embed=new_embed)
        
        # Notify the Artfight cog that configuration has changed
        artfight_cog = self.bot.get_cog('artfight')
        if artfight_cog is not None and hasattr(artfight_cog, 'on_artfight_configuration_changed'):
            await artfight_cog.on_artfight_configuration_changed(self.guild_id)

    # Row 0: Core settings
    @discord.ui.button(label='General Settings', style=discord.ButtonStyle.secondary, row=0)
    async def general_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild is None:
            await interaction.response.send_message('⚠ This action can only be used inside a server.', ephemeral=True)
            return

        view = GeneralSettingsView(
            bot=self.bot,
            repository=self.repository,
            guild_id=self.guild_id,
            update_callback=self.update_message
        )
        current_role_id = self.repository.get_artfight_role(self.guild_id)
        current_points = self.repository.get_points_name(self.guild_id)
        
        await interaction.response.send_message(
            f'**Current settings:**\n'
            f'• Artfight Role: {f"<@&{current_role_id}>" if current_role_id else "`not set`"}\n'
            f'• Points Name: `{current_points}`\n\n'
            f'Select a role below, then you\'ll be asked to set the points name.',
            view=view,
            ephemeral=True
        )

    @discord.ui.button(label='Dates & Time', style=discord.ButtonStyle.secondary, row=0)
    async def dates_time(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DateSetup(repository=self.repository, guild_id=self.guild_id, update_callback=self.update_message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Channels', style=discord.ButtonStyle.secondary, row=0)
    async def configure_channels(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild is None:
            await interaction.response.send_message('⚠ This action can only be used inside a server.', ephemeral=True)
            return

        view = ChannelSelectView(
            repository=self.repository,
            guild=interaction.guild,
            update_callback=self.update_message
        )
        await interaction.response.send_message('Select channels:', view=view, ephemeral=True)

    # Row 1: Teams
    @discord.ui.button(label='Add Team', style=discord.ButtonStyle.secondary, row=1)
    async def set_team(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = SetTeam(repository=self.repository, update_callback=self.update_message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Remove Team', style=discord.ButtonStyle.danger, row=1)
    async def remove_team(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RemoveTeam(repository=self.repository, update_callback=self.update_message)
        await interaction.response.send_modal(modal)

    # Row 2: Prompts & Yaps
    @discord.ui.button(label='Set Prompt', style=discord.ButtonStyle.secondary, row=2)
    async def set_prompt(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = SetPromptView(
            bot=self.bot,
            repository=self.repository,
            guild_id=self.guild_id,
            update_callback=self.update_message
        )
        await interaction.response.send_message('Select which day to set the prompt for:', view=view, ephemeral=True)

    @discord.ui.button(label='Remove Prompt', style=discord.ButtonStyle.danger, row=2)
    async def remove_prompt(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = RemovePromptView(
            repository=self.repository,
            guild_id=self.guild_id,
            update_callback=self.update_message
        )
        await interaction.response.send_message('Select which prompt to remove:', view=view, ephemeral=True)

    @discord.ui.button(label='Set Yap', style=discord.ButtonStyle.secondary, row=2)
    async def set_yap(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = SetYapView(
            bot=self.bot,
            repository=self.repository,
            guild_id=self.guild_id,
            update_callback=self.update_message
        )
        await interaction.response.send_message('Select which day to set the yap for:', view=view, ephemeral=True)

    @discord.ui.button(label='Remove Yap', style=discord.ButtonStyle.danger, row=2)
    async def remove_yap(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = RemoveYapView(
            repository=self.repository,
            guild_id=self.guild_id,
            update_callback=self.update_message
        )
        await interaction.response.send_message('Select which yap to remove:', view=view, ephemeral=True)

    # Row 3: Utility
    @discord.ui.button(label='Refresh', style=discord.ButtonStyle.primary, row=3)
    async def fetch_new_data(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_message(interaction)
        await interaction.response.send_message(content='✔ Refreshed', ephemeral=True)