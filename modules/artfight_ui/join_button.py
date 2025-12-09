import discord
import datetime

from discord.ui import View, Button
from random import randint
from repositories import ArtfightRepo


def build_join_embed(
    custom_message: str,
    artfight_over: bool = False
) -> discord.Embed:
    """
    Builds the embed for the join artfight message.
    
    :param custom_message: The custom message set by the server admin
    :param artfight_over: Whether artfight has ended
    :return: The embed
    """
    embed = discord.Embed(
        description=custom_message,
        color=discord.Color.green()
    )
    
    if artfight_over:
        embed.add_field(
            name="",
            value="**Artfight has ended!** Thank you for participating! 🎉",
            inline=False
        )
        embed.color = discord.Color.greyple()
    
    return embed


class TeamChoiceView(View):
    """
    Ephemeral view that lets users pick their team before artfight starts.
    """
    def __init__(
        self,
        artfight_repo: ArtfightRepo,
        guild: discord.Guild,
        user_id: int
    ):
        super().__init__(timeout=60)
        self.artfight_repo = artfight_repo
        self.guild = guild
        self.user_id = user_id
        
        # Dynamically add buttons for each team
        teams = artfight_repo.get_teams(guild.id)
        for team_name, role_id in teams.items():
            role = guild.get_role(role_id)
            if role:
                button = Button(
                    label=role.name,
                    style=discord.ButtonStyle.primary,
                    custom_id=f"team_choice_{team_name}"
                )
                button.callback = self._make_callback(team_name, role)
                self.add_item(button)

    def _make_callback(self, team_name: str, role: discord.Role):
        async def callback(interaction: discord.Interaction):
            await self._handle_team_choice(interaction, team_name, role)
        return callback

    async def _handle_team_choice(
        self,
        interaction: discord.Interaction,
        team_name: str,
        role: discord.Role
    ):
        """Handle the team choice button click."""
        # Double-check they haven't joined in the meantime
        teams = self.artfight_repo.get_teams(self.guild.id)
        for tn in teams.keys():
            if self.artfight_repo.get_team_member(self.guild.id, tn, self.user_id) is not None:
                await interaction.response.edit_message(
                    content="❌ You have already joined a team!",
                    view=None
                )
                return

        # Get artfight role
        artfight_role_id = self.artfight_repo.get_artfight_role(self.guild.id)
        artfight_role = self.guild.get_role(artfight_role_id) if artfight_role_id else None

        # Register in repo first
        try:
            self.artfight_repo.add_team_member(self.guild.id, team_name, self.user_id)
        except Exception as e:
            await interaction.response.edit_message(
                content=f"❌ Failed to register you: {e}",
                view=None
            )
            return

        # Assign roles
        member = interaction.user
        roles_to_add = [role]
        if artfight_role:
            roles_to_add.append(artfight_role)

        try:
            await member.add_roles(*roles_to_add)
        except discord.Forbidden:
            # Rollback
            try:
                self.artfight_repo.remove_team_member(self.guild.id, team_name, self.user_id)
            except Exception:
                pass
            await interaction.response.edit_message(
                content="❌ I don't have permission to assign roles.",
                view=None
            )
            return
        except discord.HTTPException as e:
            # Rollback
            try:
                self.artfight_repo.remove_team_member(self.guild.id, team_name, self.user_id)
            except Exception:
                pass
            await interaction.response.edit_message(
                content=f"❌ Failed to assign role: {e}",
                view=None
            )
            return

        await interaction.response.edit_message(
            content=f"✅ You have joined **{role.name}**!",
            view=None
        )


class JoinArtfightView(View):
    """
    Persistent view with the 'Join Artfight!' button.
    Survives bot restarts via custom_id.
    """
    def __init__(self, artfight_repo: ArtfightRepo = None):
        super().__init__(timeout=None)
        self.artfight_repo = artfight_repo

    def set_repo(self, artfight_repo: ArtfightRepo):
        """Set the repository after initialization (for persistent view registration)."""
        self.artfight_repo = artfight_repo

    @discord.ui.button(
        label="Join Artfight!",
        style=discord.ButtonStyle.success,
        custom_id="artfight_join_button",
    )
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle the join button click."""
        if self.artfight_repo is None:
            await interaction.response.send_message(
                "❌ Bot is still initializing, please try again in a moment.",
                ephemeral=True
            )
            return

        guild = interaction.guild
        user_id = interaction.user.id

        # Check if artfight is configured
        start_date = self.artfight_repo.get_start_date(guild.id)
        end_date = self.artfight_repo.get_end_date(guild.id)
        
        if start_date is None or end_date is None:
            await interaction.response.send_message(
                "❌ Artfight is not configured for this server.",
                ephemeral=True
            )
            return

        current_date_utc = datetime.datetime.now(datetime.timezone.utc).date()

        # Check if artfight is over
        if current_date_utc > end_date:
            await interaction.response.send_message(
                "❌ Artfight has ended! Thanks for your interest, but registrations are closed.",
                ephemeral=True
            )
            return

        # Check if user is already on a team
        teams = self.artfight_repo.get_teams(guild.id)
        if not teams:
            await interaction.response.send_message(
                "❌ No teams are configured for this artfight.",
                ephemeral=True
            )
            return

        # Check if user is already registered in internal data
        registered_team_name = None
        for team_name in teams.keys():
            if self.artfight_repo.get_team_member(guild.id, team_name, user_id) is not None:
                registered_team_name = team_name
                break

        if registered_team_name is not None:
            # User is registered - check if roles are correct and fix if needed
            await self._verify_and_fix_roles(interaction, guild, registered_team_name, teams)
            return

        # Check if artfight has actually started (after prompt hour on day 1)
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        prompt_hour = self.artfight_repo.get_next_prompt_hour(guild.id)
        
        if prompt_hour is None:
            # No prompt hour configured, fall back to date-only check
            artfight_started = start_date <= current_date_utc
        else:
            # Artfight starts after the prompt hour on day 1
            if current_date_utc < start_date:
                artfight_started = False
            elif current_date_utc > start_date:
                artfight_started = True
            else:
                # It's the start date - check if we're past prompt hour
                artfight_started = now_utc.time() >= prompt_hour

        if not artfight_started:
            # Let them choose their team
            view = TeamChoiceView(self.artfight_repo, guild, user_id)
            await interaction.response.send_message(
                "**Choose a team!**\nSelect the team you want to fight for:",
                view=view,
                ephemeral=True
            )
        else:
            # Auto-assign to balanced team (same logic as join command)
            await self._auto_assign_team(interaction, guild, user_id, teams)

    async def _verify_and_fix_roles(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        registered_team_name: str,
        teams: dict[str, int]
    ):
        """
        Verify the user has the correct roles based on internal data.
        If roles are missing, add them. Internal data is the source of truth.
        """
        member = interaction.user
        user_id = member.id
        
        # Get the expected roles
        team_role_id = teams.get(registered_team_name)
        team_role = guild.get_role(team_role_id) if team_role_id else None
        
        artfight_role_id = self.artfight_repo.get_artfight_role(guild.id)
        artfight_role = guild.get_role(artfight_role_id) if artfight_role_id else None

        # Check what's missing
        roles_to_add = []
        missing_roles = []

        if team_role and team_role not in member.roles:
            roles_to_add.append(team_role)
            missing_roles.append(team_role.name)

        if artfight_role and artfight_role not in member.roles:
            roles_to_add.append(artfight_role)
            missing_roles.append(artfight_role.name)

        if not roles_to_add:
            # All roles are correct
            await interaction.response.send_message(
                f"✅ You're already registered on **{team_role.name if team_role else registered_team_name}**!",
                ephemeral=True
            )
            return

        # Fix the missing roles silently
        try:
            await member.add_roles(*roles_to_add)
            # Don't mention the fix to the user
            await interaction.response.send_message(
                f"✅ You're registered on **{team_role.name if team_role else registered_team_name}**!",
                ephemeral=True
            )
        except (discord.Forbidden, discord.HTTPException):
            # Still don't mention the issue - just confirm registration
            await interaction.response.send_message(
                f"✅ You're registered on **{team_role.name if team_role else registered_team_name}**!",
                ephemeral=True
            )

    async def _auto_assign_team(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        user_id: int,
        teams: dict[str, int]
    ):
        """Auto-assign user to the most balanced team."""
        # Build team data
        team_data = []
        for team_name, role_id in teams.items():
            role = guild.get_role(role_id)
            if role is None:
                continue
            
            team_members = self.artfight_repo.get_team_members(guild.id, team_name) or {}
            member_count = len(team_members)
            team_data.append({
                'name': team_name,
                'role': role,
                'member_count': member_count
            })

        if not team_data:
            await interaction.response.send_message(
                "❌ Could not find any valid team roles. Please contact a moderator.",
                ephemeral=True
            )
            return

        # Sort by member count
        team_data.sort(key=lambda t: t['member_count'])
        min_member_count = team_data[0]['member_count']
        all_teams_tied = all(t['member_count'] == min_member_count for t in team_data)

        if not all_teams_tied:
            selected_team = team_data[0]
        else:
            # Fallback to scores
            for team in team_data:
                team['score'] = self.artfight_repo.get_team_score(guild.id, team['name']) or 0
            
            team_data.sort(key=lambda t: t['score'])
            min_score = team_data[0]['score']
            all_scores_tied = all(t['score'] == min_score for t in team_data)
            
            if not all_scores_tied:
                selected_team = team_data[0]
            else:
                # Random
                selected_team = team_data[randint(0, len(team_data) - 1)]

        # Get artfight role
        artfight_role_id = self.artfight_repo.get_artfight_role(guild.id)
        artfight_role = guild.get_role(artfight_role_id) if artfight_role_id else None

        # Register in repo first
        try:
            self.artfight_repo.add_team_member(guild.id, selected_team['name'], user_id)
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to register you: {e}",
                ephemeral=True
            )
            return

        # Assign roles
        member = interaction.user
        roles_to_add = [selected_team['role']]
        if artfight_role:
            roles_to_add.append(artfight_role)

        try:
            await member.add_roles(*roles_to_add)
        except discord.Forbidden:
            # Rollback
            try:
                self.artfight_repo.remove_team_member(guild.id, selected_team['name'], user_id)
            except Exception:
                pass
            await interaction.response.send_message(
                "❌ I don't have permission to assign roles.",
                ephemeral=True
            )
            return
        except discord.HTTPException as e:
            # Rollback
            try:
                self.artfight_repo.remove_team_member(guild.id, selected_team['name'], user_id)
            except Exception:
                pass
            await interaction.response.send_message(
                f"❌ Failed to assign role: {e}",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"✅ Welcome to the fight! You have been assigned to **{selected_team['role'].name}**!\n"
            f"*(Team selection is only available before artfight starts - you were auto-assigned to balance the teams)*",
            ephemeral=True
        )


class JoinArtfightDisabledView(View):
    """
    View with a disabled button shown when artfight is over.
    """
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Artfight Ended",
        style=discord.ButtonStyle.secondary,
        custom_id="artfight_join_button_disabled",
        disabled=True
    )
    async def disabled_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass  # Button is disabled, this won't be called


async def update_join_message_for_end(
    artfight_repo: ArtfightRepo,
    guild: discord.Guild,
    custom_message: str = None
) -> bool:
    """
    Updates the join message to show that artfight has ended.
    
    :param artfight_repo: The artfight repository
    :param guild: The Discord guild
    :param custom_message: Optional custom message to preserve in the embed
    :return: True if message was updated, False if message was not found (data cleared)
    """
    join_message_data = artfight_repo.get_join_message(guild.id)
    if join_message_data is None:
        return False
    
    channel_id, message_id = join_message_data
    channel = guild.get_channel(channel_id)
    if channel is None:
        # Channel was deleted, clear the stored data
        artfight_repo.clear_join_message(guild.id)
        return False

    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        # Message was deleted, clear the stored data
        artfight_repo.clear_join_message(guild.id)
        return False
    except (discord.Forbidden, discord.HTTPException):
        # Permission issue or other error - don't clear data, might be temporary
        return False

    # Get original description from embed if we don't have custom_message
    if custom_message is None and message.embeds:
        custom_message = message.embeds[0].description or ""

    embed = build_join_embed(custom_message, artfight_over=True)
    
    try:
        await message.edit(embed=embed, view=JoinArtfightDisabledView())
        return True
    except discord.NotFound:
        # Message was deleted between fetch and edit
        artfight_repo.clear_join_message(guild.id)
        return False
    except discord.HTTPException:
        return False
