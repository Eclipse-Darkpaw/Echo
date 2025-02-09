import discord
import datetime

from base_bot import EchoBot
from discord.ui import Modal, TextInput, View
from repositories import ArtfightRepo
from util import (
    date_to_utc_midnight_unix_timestamp,
    time_to_utc_at_epoch_timestamp
)

def artfight_configuration_message(artfight_repo: ArtfightRepo, guild_id):
    start_date = artfight_repo.get_start_date(guild_id)
    end_date = artfight_repo.get_end_date(guild_id)
    next_prompt_hour = artfight_repo.get_next_prompt_hour(guild_id)

    start_date_unix = date_to_utc_midnight_unix_timestamp(start_date)
    end_date_unix = date_to_utc_midnight_unix_timestamp(end_date)
    next_prompt_hour_unix = time_to_utc_at_epoch_timestamp(next_prompt_hour)

    start_date_human_str = start_date.strftime('%Y-%m-%d') if start_date else ''
    end_date_human_str = end_date.strftime('%Y-%m-%d') if end_date else ''
    next_prompt_hour_human_str = next_prompt_hour.strftime('%H:%M') if next_prompt_hour else ''

    teams = artfight_repo.get_teams(guild_id)
    if len(teams) > 0:
        team_list = '\n'.join(
            f'{i+1}. **{team_name}**: <@&{role_id}>' for i, (team_name, role_id) in enumerate(teams.items())
        )
    else:
        team_list = '`No teams set.`'

    prompts = artfight_repo.get_prompts(guild_id)
    if len(prompts) > 0:
        prompt_list = '\n'.join(
            f'{nr}. {prompt if len(prompt) <= 50 else f'{prompt[:50]}..'} ' for nr, prompt in prompts.items()
        )
    else:
        prompt_list = '`No prompts set.`'

    return (
        '## Artfight Configuration\n\n'
        '### Channels\n'
        f'- **Submissions Channel**: <#{artfight_repo.get_submissions_channel(guild_id) or "`not set`"}>\n'
        f'- **Prompts Channel**: <#{artfight_repo.get_prompts_channel(guild_id) or "`not set`"}>\n'
        
        '### Dates & Prompt hour\n'
        f'- **Start Date**: {f"<t:{start_date_unix}:d> (`{start_date_human_str}` UTC)" if start_date else "`not set`"}\n'
        f'- **End Date**: {f"<t:{end_date_unix}:d> (`{end_date_human_str}` UTC)" if end_date else "`not set`"}\n'
        f'- **Next Prompt Hour**: {f"<t:{next_prompt_hour_unix}:t> (`{next_prompt_hour_human_str}` UTC)" if next_prompt_hour else "`not set`"}\n'

        '### Teams\n'
        f'{team_list}\n'

        '### Prompts\n'
        f'{prompt_list}\n'
        
        '## Configuration Notes:\n'
        '> **⚠ HEADS UP!**\n'
        '> Changes take effect immediately. Be careful when modifying settings!\n\n'
        f'-# message last updated: <t:{int(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>'
    )    

class ChannelSetup(Modal):
    def __init__(self, repository: ArtfightRepo, guild_id: int, update_callback):
        super().__init__(title='Artfight Channels Configuration')
        self.add_item(TextInput(
            label='Submissions Channel ID*',
            placeholder="Enter channel ID",
            default=repository.get_submissions_channel(guild_id=guild_id)
        ))
        self.add_item(TextInput(
            label='Prompts Channel ID',
            placeholder='Enter channel ID',
            default=repository.get_prompts_channel(guild_id=guild_id)
        ))

        self.repository = repository
        self.update_callback = update_callback

    async def on_submit(self, interaction: discord.Interaction):
        subs_channel = self.children[0].value.strip()
        prompts_channel = self.children[1].value.strip()

        try:
            self.repository.set_submissions_channel(guild_id=interaction.guild.id, channel_id=subs_channel)
            self.repository.set_prompts_channel(guild_id=interaction.guild.id, channel_id=prompts_channel)
        except Exception as e:
            await interaction.response.send_message(f'❌ Failed to update:\n```\n{e}\n```', ephemeral=True)

        await interaction.response.send_message('✔ Channels updated', ephemeral=True)
        await self.update_callback(interaction)

class DateSetup(Modal):
    def __init__(self, repository: ArtfightRepo, guild_id: int, update_callback):
        super().__init__(title='Artfight Dates & Prompt Time Configuration')
        self.add_item(TextInput(
            label='Start Date (YYYY-MM-DD) *UTC 00:00 day start*',
            placeholder='e.g. 2025-03-01',
            default=(date.strftime('%Y-%m-%d') if (date := repository.get_start_date(guild_id=guild_id)) else None)
        ))
        self.add_item(TextInput(
            label='End Date (YYYY-MM-DD) *UTC 00:00 day start*',
            placeholder='e.g. 2025-03-10',
            default=(date.strftime('%Y-%m-%d') if (date := repository.get_end_date(guild_id=guild_id)) else None)
        ))
        self.add_item(TextInput(
            label='Next Prompt Hour (HH:MM) *in UTC time*',
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

class SetPrompt(Modal):
    def __init__(self, repository: ArtfightRepo, update_callback):
        super().__init__(title='Add a Prompt')
        self.add_item(TextInput(label='Day of Artfight', placeholder='Enter day number', style=discord.TextStyle.short))
        self.add_item(TextInput(label="Prompt Message", placeholder="Enter prompt message", style=discord.TextStyle.long))

        self.repository = repository
        self.update_callback = update_callback

    async def on_submit(self, interaction: discord.Interaction):
        day_str = self.children[0].value.strip()
        prompt_message = self.children[1].value.strip()

        try:
            day = int(day_str)
        except ValueError:
            await interaction.response.send_message("Invalid day number.", ephemeral=True)
            return

        try:
            self.repository.add_prompt(guild_id=interaction.guild.id, day_of_artfight=day, prompt=prompt_message)
        except Exception as e:
            await interaction.response.send_message(f'❌ Failed to update:\n```\n{e}\n```', ephemeral=True)

        await interaction.response.send_message(f"✔ Prompt for day {day} set", ephemeral=True)
        await self.update_callback(interaction)

class RemovePrompt(Modal):
    def __init__(self, repository: ArtfightRepo, update_callback):
        super().__init__(title='remove a Prompt')
        self.add_item(TextInput(label='Day of Artfight', placeholder='Enter day number', style=discord.TextStyle.short))

        self.repository = repository
        self.update_callback = update_callback

    async def on_submit(self, interaction: discord.Interaction):
        day_str = self.children[0].value.strip()

        try:
            day = int(day_str)
        except ValueError:
            await interaction.response.send_message("Invalid day number.", ephemeral=True)
            return

        try:
            self.repository.remove_prompt(guild_id=interaction.guild.id, day_of_artfight=day)
        except Exception as e:
            await interaction.response.send_message(f'❌ Failed to update:\n```\n{e}\n```', ephemeral=True)

        await interaction.response.send_message(f"✔ Prompt for day {day} removed", ephemeral=True)
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
            new_message = artfight_configuration_message(self.repository, self.guild_id)
            await self.message.edit(content=new_message)

    @discord.ui.button(label='Update Channels', style=discord.ButtonStyle.secondary)
    async def configure_channels(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ChannelSetup(repository=self.repository, guild_id=self.guild_id, update_callback=self.update_message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Update Dates & Prompt Time', style=discord.ButtonStyle.secondary)
    async def sync(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DateSetup(repository=self.repository, guild_id=self.guild_id, update_callback=self.update_message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Set Team', style=discord.ButtonStyle.secondary, row=1)
    async def set_team(self, interaction: discord.Interaction,  button: discord.ui.Button):
        modal = SetTeam(repository=self.repository, update_callback=self.update_message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Remove Team', style=discord.ButtonStyle.danger, row=1)
    async def remove_team(self, interaction: discord.Interaction,  button: discord.ui.Button):
        modal = RemoveTeam(repository=self.repository, update_callback=self.update_message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Set Prompt', style=discord.ButtonStyle.secondary, row=2)
    async def set_prompt(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = SetPrompt(repository=self.repository, update_callback=self.update_message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Remove Prompt', style=discord.ButtonStyle.danger, row=2)
    async def remove_prompt(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RemovePrompt(repository=self.repository, update_callback=self.update_message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Update message', style=discord.ButtonStyle.primary, row=3)
    async def fetch_new_data(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_message(interaction)
        await interaction.response.send_message(content='✔ Fetched latest data', ephemeral=True)