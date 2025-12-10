import discord
import datetime
import math

from discord.ui import View, Button, Select, Modal, TextInput
from discord import SelectOption
from repositories import ArtfightRepo
from typing import Callable, Awaitable


# Scoring constants
SCORE_BASE = {
    'bw_sketch': 5,
    'color_sketch': 10,
    'bw_lineart': 20,
    'full_color': 30
}
SCORE_SHADED = 10
SCORE_BACKGROUND = 20
SCORE_FRIENDLY_FIRE = 1
GRACE_PERIOD_MULTIPLIER = 0.75


class SubmissionData:
    """Holds all data collected during the submission process."""
    def __init__(self, guild_id: int, submitter_id: int, submitter_team: str):
        self.guild_id = guild_id
        self.submitter_id = submitter_id
        self.submitter_team = submitter_team
        
        self.image_url: str | None = None
        self.title: str | None = None
        self.submission_type: str | None = None  # Key from SCORE_BASE
        self.is_shaded: bool = False
        self.has_background: bool = False
        self.prompt_day: int | None = None
        self.prompt_text: str | None = None  # The actual prompt text
        self.collaborators: list[int] = []  # User IDs
        self.character_owners: list[int] = []  # User IDs for each character
        
        # Calculated during scoring
        self.base_score: int = 0
        self.final_score: int = 0
        self.is_grace_period: bool = False
        self.friendly_count: int = 0
        self.enemy_count: int = 0
        self.victims: list[int] = []  # Unique enemy user IDs


def calculate_score(
    data: SubmissionData,
    artfight_repo: ArtfightRepo,
    current_prompt_day: int,
    is_within_grace_period: bool
) -> int:
    """
    Calculate the score for a submission.
    
    Formula: ((prompt * ((base + shaded) * num_enemy_chars + bg)) * day_multiplier) + num_friendly_chars
    
    - If submitting for old prompt outside grace period: 0 points (but still +1 per friendly)
    - If within grace period for previous prompt: 75% of normal score
    - Friendly fire: +1 point per friendly character regardless of other modifiers
    
    :return: The calculated score (rounded to nearest int)
    """
    base = SCORE_BASE.get(data.submission_type, 0)
    shaded = SCORE_SHADED if data.is_shaded else 0
    background = SCORE_BACKGROUND if data.has_background else 0
    
    # Count friendly vs enemy characters
    friendly_count = 0
    enemy_count = 0
    victims = set()
    
    for owner_id in data.character_owners:
        owner_team = get_user_team(artfight_repo, data.guild_id, owner_id)
        if owner_team == data.submitter_team:
            friendly_count += 1
        else:
            enemy_count += 1
            victims.add(owner_id)
    
    data.friendly_count = friendly_count
    data.enemy_count = enemy_count
    data.victims = list(victims)
    
    # Day multiplier (every 4th day = x2)
    day_multiplier = 2 if data.prompt_day and data.prompt_day % 4 == 0 else 1
    
    # Prompt validity check
    prompt_multiplier = 1.0
    if data.prompt_day != current_prompt_day:
        if data.prompt_day == current_prompt_day - 1 and is_within_grace_period:
            # Within grace period for previous day
            prompt_multiplier = GRACE_PERIOD_MULTIPLIER
            data.is_grace_period = True
        else:
            # Old prompt, no points for enemy attacks
            prompt_multiplier = 0.0
    
    # Calculate base score (without friendly fire)
    base_score = ((base + shaded) * enemy_count + background) * day_multiplier
    base_score = base_score * prompt_multiplier
    
    # Add friendly fire points (always awarded, not affected by prompt/multipliers)
    total_score = base_score + (friendly_count * SCORE_FRIENDLY_FIRE)
    
    # Round to nearest integer
    data.base_score = round(base_score)
    data.final_score = round(total_score)
    
    return data.final_score


def get_user_team(artfight_repo: ArtfightRepo, guild_id: int, user_id: int) -> str | None:
    """Get which team a user is on."""
    teams = artfight_repo.get_teams(guild_id)
    for team_name in teams.keys():
        if artfight_repo.get_team_member(guild_id, team_name, user_id) is not None:
            return team_name
    return None


def get_all_participants(
    artfight_repo: ArtfightRepo,
    guild: 'discord.Guild',
    guild_id: int,
    exclude_user_id: int | None = None,
    team_filter: str | None = None
) -> list[tuple[int, str, str]]:
    """
    Get all artfight participants as (user_id, display_name, team_name).
    
    :param artfight_repo: The artfight repository
    :param guild: The Discord guild (for member lookups)
    :param guild_id: The guild ID
    :param exclude_user_id: User ID to exclude (e.g., the submitter)
    :param team_filter: If set, only return members of this team
    :return: List of (user_id, display_name, team_name) tuples
    """
    participants = []
    teams = artfight_repo.get_teams(guild_id)
    
    for team_name in teams.keys():
        if team_filter and team_name != team_filter:
            continue
        
        members = artfight_repo.get_team_members(guild_id, team_name) or {}
        for user_id_str in members.keys():
            user_id = int(user_id_str)
            if exclude_user_id and user_id == exclude_user_id:
                continue
            
            member = guild.get_member(user_id)
            if member:
                display_name = member.display_name[:50]
            else:
                display_name = f"User {user_id}"
            
            participants.append((user_id, display_name, team_name))
    
    return participants


def split_score_for_collab(total_score: int, num_collaborators: int, submitter_gets_extra: bool = True) -> list[int]:
    """
    Split score among collaborators.
    If not evenly divisible, submitter gets the extra point(s).
    
    :param total_score: The total score to split
    :param num_collaborators: Number of people to split between (including submitter)
    :param submitter_gets_extra: If True, submitter gets the remainder
    :return: List of scores, first element is submitter's share
    """
    if num_collaborators <= 1:
        return [total_score]
    
    base_share = total_score // num_collaborators
    remainder = total_score % num_collaborators
    
    shares = [base_share] * num_collaborators
    if submitter_gets_extra:
        shares[0] += remainder
    
    return shares


class SubmissionTypeSelect(Select):
    """Dropdown for selecting submission type."""
    def __init__(self):
        options = [
            SelectOption(
                label="Black & White (Rough) Sketch",
                value="bw_sketch",
                description=f"+{SCORE_BASE['bw_sketch']} base points"
            ),
            SelectOption(
                label="Colour (Rough) Sketch",
                value="color_sketch",
                description=f"+{SCORE_BASE['color_sketch']} base points"
            ),
            SelectOption(
                label="Black & White Lineart",
                value="bw_lineart",
                description=f"+{SCORE_BASE['bw_lineart']} base points"
            ),
            SelectOption(
                label="Full Colored",
                value="full_color",
                description=f"+{SCORE_BASE['full_color']} base points"
            ),
        ]
        super().__init__(
            placeholder="What type of submission is this?",
            options=options,
            custom_id="submission_type_select"
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.data.submission_type = self.values[0]
        await self.view.advance_step(interaction)


class PromptDaySelect(Select):
    """Dropdown for selecting which prompt day this submission is for."""
    def __init__(self, prompts: dict[str, str], current_day: int):
        options = []
        for day_str, prompt_text in sorted(prompts.items(), key=lambda x: int(x[0]), reverse=True):
            day = int(day_str)
            if day <= current_day:
                # Truncate prompt text if too long
                display_text = prompt_text[:50] + "..." if len(prompt_text) > 50 else prompt_text
                is_current = day == current_day
                options.append(SelectOption(
                    label=f"Day {day}{' (Current)' if is_current else ''}",
                    value=day_str,
                    description=display_text,
                    default=is_current
                ))
        
        # Limit to 25 options (Discord limit)
        options = options[:25]
        
        super().__init__(
            placeholder="Which prompt is this submission for?",
            options=options,
            custom_id="prompt_day_select"
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.data.prompt_day = int(self.values[0])
        await self.view.advance_step(interaction)


class ShadedView(View):
    """Buttons for shaded yes/no."""
    def __init__(self, parent_view: 'SubmissionFlowView'):
        super().__init__(timeout=300)
        self.parent_view = parent_view

    @discord.ui.button(label="Yes, it's shaded", style=discord.ButtonStyle.success, custom_id="shaded_yes")
    async def shaded_yes(self, interaction: discord.Interaction, button: Button):
        self.parent_view.data.is_shaded = True
        await self.parent_view.advance_step(interaction)

    @discord.ui.button(label="No shading", style=discord.ButtonStyle.secondary, custom_id="shaded_no")
    async def shaded_no(self, interaction: discord.Interaction, button: Button):
        self.parent_view.data.is_shaded = False
        await self.parent_view.advance_step(interaction)


class BackgroundView(View):
    """Buttons for background yes/no."""
    def __init__(self, parent_view: 'SubmissionFlowView'):
        super().__init__(timeout=300)
        self.parent_view = parent_view

    @discord.ui.button(label="Yes, has background", style=discord.ButtonStyle.success, custom_id="bg_yes")
    async def bg_yes(self, interaction: discord.Interaction, button: Button):
        self.parent_view.data.has_background = True
        await self.parent_view.advance_step(interaction)

    @discord.ui.button(label="No background", style=discord.ButtonStyle.secondary, custom_id="bg_no")
    async def bg_no(self, interaction: discord.Interaction, button: Button):
        self.parent_view.data.has_background = False
        await self.parent_view.advance_step(interaction)


class CharacterCountModal(Modal):
    """Modal to input number of characters."""
    def __init__(self, parent_view: 'SubmissionFlowView'):
        super().__init__(title="Character Count")
        self.parent_view = parent_view
        
        self.count_input = TextInput(
            label="How many characters are in your attack?",
            placeholder="Enter a number (e.g., 2)",
            min_length=1,
            max_length=3,
            required=True
        )
        self.add_item(self.count_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            count = int(self.count_input.value)
            if count <= 0:
                await interaction.response.send_message("❌ Please enter a number greater than 0.", ephemeral=True)
                return
            
            # First 9 days: max 5 characters
            if self.parent_view.current_day <= 9 and count > 5:
                await interaction.response.send_message("❌ Maximum 5 characters allowed during the first 9 days of artfight.", ephemeral=True)
                return
            
            self.parent_view.character_count = count
            await self.parent_view.advance_step(interaction)
        except ValueError:
            await interaction.response.send_message("❌ Please enter a valid number.", ephemeral=True)


class TitleModal(Modal):
    """Modal to input submission title."""
    def __init__(self, parent_view: 'SubmissionFlowView'):
        super().__init__(title="Submission Title")
        self.parent_view = parent_view
        
        self.title_input = TextInput(
            label="What is the title of this piece?",
            placeholder="Enter a title for your submission",
            min_length=1,
            max_length=100,
            required=True
        )
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.data.title = self.title_input.value
        await self.parent_view.advance_step(interaction)


class ConfirmationView(View):
    """Final confirmation view with Submit/Cancel."""
    def __init__(self, parent_view: 'SubmissionFlowView'):
        super().__init__(timeout=300)
        self.parent_view = parent_view

    @discord.ui.button(label="✅ SUBMIT", style=discord.ButtonStyle.success, custom_id="confirm_submit")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        await self.parent_view.finalize_submission(interaction)

    @discord.ui.button(label="❌ CANCEL", style=discord.ButtonStyle.danger, custom_id="cancel_submit")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="❌ Submission cancelled.", embed=None, view=None)
        self.parent_view.stop()


def build_submission_embed(
    data: SubmissionData,
    team_role: discord.Role | None,
    points_name: str,
    guild: discord.Guild
) -> discord.Embed:
    """
    Build the submission embed to be posted in the submissions channel.
    
    :param data: The submission data
    :param team_role: The attacking team's role (for color)
    :param points_name: The custom name for points
    :param guild: The Discord guild
    :return: The submission embed
    """
    embed = discord.Embed(
        title=data.title,
        color=team_role.color if team_role else discord.Color.purple()
    )
    
    # Set the image
    if data.image_url:
        embed.set_image(url=data.image_url)
    
    # Attackers (submitter + collaborators)
    attackers = [f"<@{data.submitter_id}>"]
    for collab_id in data.collaborators:
        attackers.append(f"<@{collab_id}>")
    embed.add_field(name="⚔️ Attack by", value=", ".join(attackers), inline=True)
    
    # Victims
    if data.victims:
        victim_mentions = [f"<@{v}>" for v in data.victims]
        embed.add_field(name="Victims", value=", ".join(victim_mentions), inline=True)
    
    # Friendly fire note (if any)
    if data.friendly_count > 0:
        embed.add_field(name="Friendly Fire", value=f"{data.friendly_count} teammate(s)", inline=True)
    
    # Score
    embed.add_field(name="Score", value=f"**{data.final_score}** {points_name}", inline=True)
    
    # Prompt - show actual text, truncated if needed
    if data.prompt_text:
        prompt_display = data.prompt_text[:80] + "..." if len(data.prompt_text) > 80 else data.prompt_text
        embed.add_field(name=f"Prompt (Day {data.prompt_day})", value=f"*{prompt_display}*", inline=False)
    else:
        embed.add_field(name="Prompt", value=f"Day {data.prompt_day}", inline=True)
    
    # Footer for grace period
    if data.is_grace_period:
        embed.set_footer(text="Submitted during grace period (75% score)")
    
    return embed


def build_preview_embed(
    data: SubmissionData,
    points_name: str,
    team_role: discord.Role | None = None
) -> discord.Embed:
    """Build a preview embed shown to the user before confirmation."""
    embed = discord.Embed(
        title=f"Submission Preview: {data.title}",
        color=team_role.color if team_role else discord.Color.blue()
    )
    
    if data.image_url:
        embed.set_image(url=data.image_url)
    
    # Submission details
    type_labels = {
        'bw_sketch': "Black & White Sketch",
        'color_sketch': "Colour Sketch",
        'bw_lineart': "Black & White Lineart",
        'full_color': "Full Colored"
    }
    embed.add_field(name="Type", value=type_labels.get(data.submission_type, "Unknown"), inline=True)
    embed.add_field(name="Shaded", value="Yes" if data.is_shaded else "No", inline=True)
    embed.add_field(name="Background", value="Yes" if data.has_background else "No", inline=True)
    embed.add_field(name="Prompt Day", value=str(data.prompt_day), inline=True)
    embed.add_field(name="Enemy Characters", value=str(data.enemy_count), inline=True)
    embed.add_field(name="Friendly Fire", value=str(data.friendly_count), inline=True)
    
    # Score breakdown
    score_text = f"**{data.final_score}** {points_name}"
    if data.is_grace_period:
        score_text += " *(75% - grace period)*"
    embed.add_field(name="Total Score", value=score_text, inline=False)
    
    if data.collaborators:
        collab_mentions = [f"<@{c}>" for c in data.collaborators]
        embed.add_field(name="Collaborators", value=", ".join(collab_mentions), inline=False)
    
    return embed


class SubmissionFlowView(View):
    """
    Main orchestrator for the submission flow in DMs.
    Guides the user through all steps of submitting artwork.
    """
    
    # Flow steps - Image upload first!
    STEP_IMAGE = 0
    STEP_TITLE = 1
    STEP_TYPE = 2
    STEP_SHADED = 3
    STEP_BACKGROUND = 4
    STEP_CHAR_COUNT = 5
    STEP_CHAR_OWNERS = 6  # Repeats for each character
    STEP_CHAR_OWNER_INPUT = 7  # For typing character owner user ID
    STEP_COLLABORATORS = 8
    STEP_COLLAB_INPUT = 9  # For typing collaborator user ID
    STEP_CONFIRM = 10
    
    def __init__(
        self,
        artfight_repo: ArtfightRepo,
        guild: discord.Guild,
        submitter: discord.Member,
        submitter_team: str,
        prompt_day: int,
        dm_channel: discord.DMChannel,
        submissions_channel: discord.TextChannel,
        on_complete: Callable[['SubmissionData'], Awaitable[None]] | None = None
    ):
        super().__init__(timeout=600)  # 10 minute timeout
        self.artfight_repo = artfight_repo
        self.guild = guild
        self.submitter = submitter
        self.submitter_team = submitter_team
        self.dm_channel = dm_channel
        self.submissions_channel = submissions_channel
        self.on_complete = on_complete
        
        self.data = SubmissionData(guild.id, submitter.id, submitter_team)
        self.data.prompt_day = prompt_day  # Set from command parameter
        
        self.current_step = self.STEP_IMAGE
        self.character_count = 0
        self.current_character = 0
        self.message: discord.Message | None = None
        
        # Cache participants for selection (populated in start())
        self._all_participants: list[tuple[int, str, str]] = []  # All participants (for char owners)
        self._team_participants: list[tuple[int, str, str]] = []  # Same team only (for collabs)
        
        # Get current artfight day info for grace period calculation
        start_date = artfight_repo.get_start_date(guild.id)
        prompt_time = artfight_repo.get_next_prompt_hour(guild.id)
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        
        if start_date:
            self.current_day = (now_utc.date() - start_date).days + 1
        else:
            self.current_day = 1
        
        # Check if within grace period (first 15 min after prompt hour)
        self.is_within_grace_period = False
        if prompt_time and start_date:
            prompt_datetime = datetime.datetime.combine(now_utc.date(), prompt_time, tzinfo=datetime.timezone.utc)
            time_since_prompt = (now_utc - prompt_datetime).total_seconds() / 60
            self.is_within_grace_period = 0 <= time_since_prompt <= 15

    def _is_artfight_over(self) -> bool:
        """
        Check if artfight has ended.
        Returns True if we're past the end date, or past prompt hour on the last day.
        Note: There is NO grace period at the end of artfight - only for late submissions during the event.
        """
        end_date = self.artfight_repo.get_end_date(self.guild.id)
        if end_date is None:
            return True  # No end date = not configured
        
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        current_date = now_utc.date()
        
        if current_date > end_date:
            return True
        
        if current_date == end_date:
            # On the last day, artfight ends at prompt hour - NO grace period
            prompt_time = self.artfight_repo.get_next_prompt_hour(self.guild.id)
            if prompt_time:
                if now_utc.time() >= prompt_time:
                    return True
        
        return False

    async def _check_artfight_active(self) -> bool:
        """
        Check if artfight is still active. If not, notify the user and return False.
        Call this before key steps to interrupt if time is up.
        """
        if self._is_artfight_over():
            await self.dm_channel.send(
                "**Sorry, artfight has ended!**\n"
                "The submission window has closed. "
                "Your submission could not be completed in time.\n"
            )
            self.stop()
            return False
        return True

    async def start(self):
        """Start the submission flow by asking for image upload."""
        # Cache all participants for character owner selection (excludes self)
        self._all_participants = get_all_participants(
            self.artfight_repo,
            self.guild,
            self.guild.id,
            exclude_user_id=self.submitter.id
        )
        
        # Cache same-team participants for collaborator selection (excludes self)
        self._team_participants = get_all_participants(
            self.artfight_repo,
            self.guild,
            self.guild.id,
            exclude_user_id=self.submitter.id,
            team_filter=self.submitter_team
        )
        
        # Start with image upload
        self.current_step = self.STEP_IMAGE
        await self.ask_for_image()

    async def show_collaborator_question(self):
        """Show the collaborator question with yes/no buttons."""
        view = View(timeout=300)
        
        async def collab_yes(interaction: discord.Interaction):
            await interaction.response.edit_message(content="Working with collaborators", view=None)
            await self.show_collaborator_select()
        
        async def collab_no(interaction: discord.Interaction):
            await interaction.response.edit_message(content="Solo submission", view=None)
            # No collaborators, go to confirmation
            await self.show_confirmation()
        
        yes_btn = Button(label="Yes, I collaborated", style=discord.ButtonStyle.success)
        yes_btn.callback = collab_yes
        no_btn = Button(label="No, solo submission", style=discord.ButtonStyle.secondary)
        no_btn.callback = collab_no
        
        view.add_item(yes_btn)
        view.add_item(no_btn)
        
        await self.dm_channel.send(
            "**Did you collaborate with anyone on this piece?**",
            view=view
        )

    async def show_collaborator_select(self):
        """Show the collaborator selection - dropdown(s) of team members or type user ID."""
        view = View(timeout=300)
        
        # Filter out already selected collaborators and the submitter themselves
        available = [p for p in self._team_participants 
                     if p[0] not in self.data.collaborators and p[0] != self.submitter.id]
        
        # Callback for when a collaborator is selected from any dropdown
        async def member_selected(interaction: discord.Interaction):
            selected_id = int(interaction.data['values'][0])
            if selected_id not in self.data.collaborators:
                self.data.collaborators.append(selected_id)
            
            collab_mentions = [f"<@{c}>" for c in self.data.collaborators]
            await interaction.response.edit_message(
                content=f"Collaborators: {', '.join(collab_mentions)}",
                view=None
            )
            # Ask if they want to add more
            await self.show_add_more_collaborators()
        
        # Create multiple dropdowns if needed (max 25 per dropdown, max 3 dropdowns to leave room for buttons)
        if available:
            # Sort by display name for better UX
            sorted_available = sorted(available, key=lambda p: p[1].lower())
            
            # Split into chunks of 25
            chunks = [sorted_available[i:i+25] for i in range(0, len(sorted_available), 25)]
            
            # Add up to 3 dropdowns (leaving room for Type ID and Done buttons)
            for chunk_idx, chunk in enumerate(chunks[:3]):
                options = []
                for user_id, display_name, team_name in chunk:
                    options.append(SelectOption(
                        label=display_name[:100],
                        value=str(user_id),
                        description=f"User ID: {user_id}"[:100]
                    ))
                
                if options:
                    # Create range label for dropdown
                    first_name = chunk[0][1][:1].upper()
                    last_name = chunk[-1][1][:1].upper()
                    range_label = f"{first_name}-{last_name}" if first_name != last_name else first_name
                    
                    select = Select(
                        placeholder=f"Add collaborator ({range_label})" if len(chunks) > 1 else "Select a teammate to add as collaborator",
                        options=options,
                        row=chunk_idx
                    )
                    select.callback = member_selected
                    view.add_item(select)
        
        # Button to type user ID manually (always available)
        async def type_id(interaction: discord.Interaction):
            await interaction.response.edit_message(
                content="Please type the user ID of your collaborator:",
                view=None
            )
            self.current_step = self.STEP_COLLAB_INPUT
        
        # Button to skip/done
        async def done_collabs(interaction: discord.Interaction):
            if self.data.collaborators:
                collab_mentions = [f"<@{c}>" for c in self.data.collaborators]
                await interaction.response.edit_message(
                    content=f"Collaborators: {', '.join(collab_mentions)}",
                    view=None
                )
            else:
                await interaction.response.edit_message(content="Solo submission", view=None)
            await self.show_confirmation()
        
        type_btn = Button(label="Type User ID", style=discord.ButtonStyle.primary, row=4)
        type_btn.callback = type_id
        done_btn = Button(label="Done Adding" if self.data.collaborators else "Skip", style=discord.ButtonStyle.secondary, row=4)
        done_btn.callback = done_collabs
        
        view.add_item(type_btn)
        view.add_item(done_btn)
        
        current_collabs = ""
        if self.data.collaborators:
            collab_mentions = [f"<@{c}>" for c in self.data.collaborators]
            current_collabs = f"\n\n**Current collaborators:** {', '.join(collab_mentions)}"
        
        # Show message - mention if there are more than 75 teammates (3 dropdowns worth)
        if len(available) > 75:
            await self.dm_channel.send(
                f"👥 **Select a collaborator from your team** (or type their user ID):\n"
                f"-# (Showing first 75 teammates alphabetically){current_collabs}",
                view=view
            )
        else:
            await self.dm_channel.send(
                f"👥 **Select a collaborator from your team** (or type their user ID):{current_collabs}",
                view=view
            )

    async def show_add_more_collaborators(self):
        """Ask if user wants to add more collaborators."""
        view = View(timeout=300)
        
        async def add_more(interaction: discord.Interaction):
            await interaction.response.edit_message(content="Adding more...", view=None)
            await self.show_collaborator_select()
        
        async def done(interaction: discord.Interaction):
            collab_mentions = [f"<@{c}>" for c in self.data.collaborators]
            await interaction.response.edit_message(
                content=f"Final collaborators: {', '.join(collab_mentions)}",
                view=None
            )
            # Collaborators done, go to confirmation
            await self.show_confirmation()
        
        add_btn = Button(label="Add Another", style=discord.ButtonStyle.primary)
        add_btn.callback = add_more
        done_btn = Button(label="Done Adding", style=discord.ButtonStyle.success)
        done_btn.callback = done
        
        view.add_item(add_btn)
        view.add_item(done_btn)
        
        collab_mentions = [f"<@{c}>" for c in self.data.collaborators]
        await self.dm_channel.send(
            f"**Current collaborators:** {', '.join(collab_mentions)}\n\nAdd more collaborators?",
            view=view
        )

    async def ask_for_image(self):
        """Ask for the image upload."""
        await self.dm_channel.send(
            "**Please upload the art you are submitting.**\n"
            "Send the image in this DM."
        )

    async def handle_message(self, message: discord.Message) -> bool:
        """
        Handle a message from the user during the flow.
        Returns True if the message was handled, False otherwise.
        """
        if message.author.id != self.submitter.id:
            return False
        
        if self.current_step == self.STEP_COLLAB_INPUT:
            # User is typing a user ID for collaborator
            try:
                user_id = int(message.content.strip().replace('<@', '').replace('>', '').replace('!', ''))
                
                # Validate the user
                if user_id == self.submitter.id:
                    await self.dm_channel.send("❌ You can't add yourself as a collaborator!")
                    return True
                
                # Check if on same team
                collab_team = get_user_team(self.artfight_repo, self.guild.id, user_id)
                if collab_team is None:
                    await self.dm_channel.send("❌ This user is not registered in artfight.")
                    return True
                
                if collab_team != self.submitter_team:
                    await self.dm_channel.send("❌ Cross-team collaborations are not allowed!")
                    return True
                
                if user_id in self.data.collaborators:
                    await self.dm_channel.send("❌ This user is already in your collaborator list!")
                    return True
                
                self.data.collaborators.append(user_id)
                await self.show_add_more_collaborators()
                return True
                
            except ValueError:
                await self.dm_channel.send("❌ Invalid user ID. Please enter a valid numeric user ID.")
                return True
        
        if self.current_step == self.STEP_CHAR_OWNER_INPUT:
            # User is typing a user ID for character owner
            try:
                user_id = int(message.content.strip().replace('<@', '').replace('>', '').replace('!', ''))
                
                # Validate the user is a participant
                owner_team = get_user_team(self.artfight_repo, self.guild.id, user_id)
                if owner_team is None:
                    await self.dm_channel.send("❌ This user is not registered in artfight.")
                    return True
                
                self.data.character_owners.append(user_id)
                await self.dm_channel.send(f"Character {self.current_character}: <@{user_id}>")
                
                self.current_character += 1
                if self.current_character <= self.character_count:
                    await self.ask_character_owner()
                else:
                    # After all characters, ask about collaborators
                    self.current_step = self.STEP_COLLABORATORS
                    await self.show_collaborator_question()
                return True
                
            except ValueError:
                await self.dm_channel.send("❌ Invalid user ID. Please enter a valid numeric user ID.")
                return True
        
        if self.current_step == self.STEP_IMAGE:
            # Check for image attachment
            if not message.attachments:
                await self.dm_channel.send("❌ No image attached. Please send an image.")
                return True
            
            attachment = message.attachments[0]
            if not attachment.content_type or not attachment.content_type.startswith('image/'):
                await self.dm_channel.send("❌ Please send an image file (PNG, JPG, etc.).")
                return True
            
            self.data.image_url = attachment.url
            self.current_step = self.STEP_TITLE
            await self.show_title_prompt()
            return True
        
        if self.current_step == self.STEP_TITLE:
            return await self.handle_title_response(message)
        
        if self.current_step == self.STEP_CHAR_COUNT:
            return await self.handle_character_count(message)
        
        return False

    async def show_title_prompt(self):
        """Ask for the title."""
        await self.dm_channel.send("**What is the title of this piece?**")
        self.current_step = self.STEP_TITLE

    async def handle_title_response(self, message: discord.Message) -> bool:
        """Handle the title response."""
        if self.current_step != self.STEP_TITLE:
            return False
        if message.author.id != self.submitter.id:
            return False
        
        self.data.title = message.content[:100]  # Limit to 100 chars
        self.current_step = self.STEP_TYPE
        await self.show_type_select()
        return True

    async def show_type_select(self):
        """Show the submission type dropdown."""
        view = View(timeout=300)
        select = SubmissionTypeSelect()
        view.add_item(select)
        
        # Override the select callback to use our flow
        async def new_callback(interaction: discord.Interaction):
            self.data.submission_type = select.values[0]
            self.current_step = self.STEP_SHADED
            await interaction.response.edit_message(
                content=f"Type: **{select.values[0].replace('_', ' ').title()}**",
                view=None
            )
            await self.show_shaded_buttons()
        select.callback = new_callback
        
        self.message = await self.dm_channel.send(
            "**What type of submission is this?**",
            view=view
        )

    async def show_shaded_buttons(self):
        """Show shaded yes/no buttons."""
        view = View(timeout=300)
        
        async def shaded_yes(interaction: discord.Interaction):
            self.data.is_shaded = True
            await interaction.response.edit_message(content="Shaded: **Yes**", view=None)
            self.current_step = self.STEP_BACKGROUND
            await self.show_background_buttons()
        
        async def shaded_no(interaction: discord.Interaction):
            self.data.is_shaded = False
            await interaction.response.edit_message(content="Shaded: **No**", view=None)
            self.current_step = self.STEP_BACKGROUND
            await self.show_background_buttons()
        
        yes_btn = Button(label="Yes, it's shaded", style=discord.ButtonStyle.success)
        yes_btn.callback = shaded_yes
        no_btn = Button(label="No shading", style=discord.ButtonStyle.secondary)
        no_btn.callback = shaded_no
        
        view.add_item(yes_btn)
        view.add_item(no_btn)
        
        await self.dm_channel.send("**Is this shaded?**", view=view)

    async def show_background_buttons(self):
        """Show background yes/no buttons."""
        view = View(timeout=300)
        
        async def bg_yes(interaction: discord.Interaction):
            self.data.has_background = True
            await interaction.response.edit_message(content="Background: **Yes**", view=None)
            self.current_step = self.STEP_CHAR_COUNT
            await self.ask_character_count()
        
        async def bg_no(interaction: discord.Interaction):
            self.data.has_background = False
            await interaction.response.edit_message(content="Background: **No**", view=None)
            self.current_step = self.STEP_CHAR_COUNT
            await self.ask_character_count()
        
        yes_btn = Button(label="Yes, has background", style=discord.ButtonStyle.success)
        yes_btn.callback = bg_yes
        no_btn = Button(label="No background", style=discord.ButtonStyle.secondary)
        no_btn.callback = bg_no
        
        view.add_item(yes_btn)
        view.add_item(no_btn)
        
        await self.dm_channel.send("**Is there a background?**", view=view)

    async def ask_character_count(self):
        """Ask for the number of characters."""
        await self.dm_channel.send(
            "👥 **How many characters are in your attack?**\n"
            "Please reply with a number."
        )

    async def handle_character_count(self, message: discord.Message) -> bool:
        """Handle the character count response."""
        if self.current_step != self.STEP_CHAR_COUNT:
            return False
        if message.author.id != self.submitter.id:
            return False
        
        try:
            count = int(message.content.strip())
            if count <= 0:
                await self.dm_channel.send("❌ Please enter a number greater than 0.")
                return True
            
            # First 9 days: max 5 characters
            if self.current_day <= 9 and count > 5:
                await self.dm_channel.send("❌ Maximum 5 characters allowed during the first 9 days of artfight.")
                return True
            
            self.character_count = count
            self.current_character = 1
            self.current_step = self.STEP_CHAR_OWNERS
            await self.ask_character_owner()
            return True
        except ValueError:
            await self.dm_channel.send("❌ Please enter a valid number.")
            return True

    async def ask_character_owner(self):
        """Ask who owns the current character using participant dropdown(s) or ID input."""
        view = View(timeout=300)
        
        # Callback for when an owner is selected from any dropdown
        async def owner_selected(interaction: discord.Interaction):
            selected_id = int(interaction.data['values'][0])
            self.data.character_owners.append(selected_id)
            await interaction.response.edit_message(
                content=f"Character {self.current_character}: <@{selected_id}>",
                view=None
            )
            
            self.current_character += 1
            if self.current_character <= self.character_count:
                await self.ask_character_owner()
            else:
                # After all characters, ask about collaborators
                self.current_step = self.STEP_COLLABORATORS
                await self.show_collaborator_question()
        
        # Use all participants (from any team) for character owners
        # Create multiple dropdowns if needed (max 25 per dropdown, max 5 dropdowns per view)
        if self._all_participants:
            # Sort by display name for better UX
            sorted_participants = sorted(self._all_participants, key=lambda p: p[1].lower())
            
            # Split into chunks of 25 (Discord limit per Select)
            chunks = [sorted_participants[i:i+25] for i in range(0, len(sorted_participants), 25)]
            
            # Add up to 4 dropdowns (leaving room for the Type ID button)
            for chunk_idx, chunk in enumerate(chunks[:4]):
                options = []
                for user_id, display_name, team_name in chunk:
                    options.append(SelectOption(
                        label=display_name[:100],
                        value=str(user_id),
                        description=f"{team_name} • ID: {user_id}"[:100]
                    ))
                
                if options:
                    # Create range label for dropdown (e.g., "A-M" or "N-Z")
                    first_name = chunk[0][1][:1].upper()
                    last_name = chunk[-1][1][:1].upper()
                    range_label = f"{first_name}-{last_name}" if first_name != last_name else first_name
                    
                    select = Select(
                        placeholder=f"Owner #{self.current_character} ({range_label})" if len(chunks) > 1 else f"Who owns character #{self.current_character}?",
                        options=options,
                        row=chunk_idx
                    )
                    select.callback = owner_selected
                    view.add_item(select)
        
        # Button to type user ID manually (always available)
        async def type_id(interaction: discord.Interaction):
            await interaction.response.edit_message(
                content=f"Please type the user ID of character #{self.current_character}'s owner:",
                view=None
            )
            self.current_step = self.STEP_CHAR_OWNER_INPUT
        
        type_btn = Button(label="Type User ID", style=discord.ButtonStyle.primary, row=4)
        type_btn.callback = type_id
        view.add_item(type_btn)
        
        # Show message - mention if there are more than 100 participants (4 dropdowns worth)
        if len(self._all_participants) > 100:
            await self.dm_channel.send(
                f"**Character #{self.current_character}**: Who owns this character?\n"
                f"Select from the dropdowns or type their user ID.\n"
                f"-# (Showing first 100 participants alphabetically)",
                view=view
            )
        else:
            await self.dm_channel.send(
                f"**Character #{self.current_character}**: Who owns this character?\n"
                f"Select from the dropdown or type their user ID.",
                view=view
            )

    async def show_confirmation(self):
        """Show the final confirmation with preview."""
        # Check if artfight is still active
        if not await self._check_artfight_active():
            return
        
        # Calculate score
        points_name = self.artfight_repo.get_points_name(self.guild.id)
        calculate_score(self.data, self.artfight_repo, self.current_day, self.is_within_grace_period)
        
        # Get team role for embed color
        teams = self.artfight_repo.get_teams(self.guild.id)
        team_role_id = teams.get(self.submitter_team)
        team_role = self.guild.get_role(team_role_id) if team_role_id else None
        
        # Get prompt text
        prompts = self.artfight_repo.get_prompts(self.guild.id) or {}
        self.data.prompt_text = prompts.get(str(self.data.prompt_day))
        
        # Build preview embed
        preview_embed = build_preview_embed(self.data, points_name, team_role)
        
        # Confirmation buttons
        view = View(timeout=300)
        
        async def confirm(interaction: discord.Interaction):
            await interaction.response.edit_message(content="Submitting...", embed=preview_embed, view=None)
            await self.finalize_submission(interaction)
        
        async def cancel(interaction: discord.Interaction):
            await interaction.response.edit_message(content="❌ Submission cancelled.", embed=None, view=None)
            self.stop()
        
        confirm_btn = Button(label="SUBMIT", style=discord.ButtonStyle.success)
        confirm_btn.callback = confirm
        cancel_btn = Button(label="CANCEL", style=discord.ButtonStyle.danger)
        cancel_btn.callback = cancel
        
        view.add_item(confirm_btn)
        view.add_item(cancel_btn)
        
        self.current_step = self.STEP_CONFIRM
        await self.dm_channel.send(
            "**Please review your submission:**",
            embed=preview_embed,
            view=view
        )

    async def finalize_submission(self, interaction: discord.Interaction):
        """Save the submission and post to the submissions channel."""
        # Final check - artfight must still be active
        if not await self._check_artfight_active():
            return
        
        try:
            # Get team role for embed color
            teams = self.artfight_repo.get_teams(self.guild.id)
            team_role_id = teams.get(self.data.submitter_team)
            team_role = self.guild.get_role(team_role_id) if team_role_id else None
            points_name = self.artfight_repo.get_points_name(self.guild.id)
            
            # Handle collab score splitting
            num_collaborators = 1 + len(self.data.collaborators)
            if num_collaborators > 1:
                shares = split_score_for_collab(self.data.final_score, num_collaborators)
                submitter_share = shares[0]
                collab_shares = shares[1:]
            else:
                submitter_share = self.data.final_score
                collab_shares = []
            
            # Save submission for submitter
            self.artfight_repo.add_team_member_submission(
                guild_id=self.guild.id,
                team_name=self.data.submitter_team,
                user_id=self.data.submitter_id,
                submission_url=self.data.image_url,
                points=submitter_share,
                title=self.data.title,
                prompt_day=self.data.prompt_day,
                victims=self.data.victims,
                collaborators=self.data.collaborators
            )
            
            # Save for each collaborator
            for i, collab_id in enumerate(self.data.collaborators):
                collab_share = collab_shares[i] if i < len(collab_shares) else 0
                self.artfight_repo.add_team_member_submission(
                    guild_id=self.guild.id,
                    team_name=self.data.submitter_team,  # Same team (cross-team collabs not allowed)
                    user_id=collab_id,
                    submission_url=self.data.image_url,
                    points=collab_share,
                    title=self.data.title,
                    prompt_day=self.data.prompt_day,
                    victims=self.data.victims,
                    collaborators=[self.data.submitter_id] + [c for c in self.data.collaborators if c != collab_id]
                )
            
            # Build and send the submission embed
            submission_embed = build_submission_embed(self.data, team_role, points_name, self.guild)
            await self.submissions_channel.send(embed=submission_embed)
            
            # Confirm to user (show total score, not individual share)
            await self.dm_channel.send(
                f"✅ **Submission complete!**\n"
                f"Your submission has been posted in {self.submissions_channel.mention}.\n"
                f"Your attack earned your team **{self.data.final_score}** {points_name}!"
            )
            
            if self.on_complete:
                await self.on_complete(self.data)
            
            self.stop()
            
        except Exception as e:
            await self.dm_channel.send(f"❌ Failed to save submission: {e}")
            raise

    async def advance_step(self, interaction: discord.Interaction):
        """Advance to the next step - placeholder for step-based navigation."""
        pass  # Steps are handled individually now

