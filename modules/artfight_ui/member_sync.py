import discord

from repositories import ArtfightRepo
from typing import Callable, Awaitable


def build_unregistered_members_embed(
    guild: discord.Guild,
    unregistered_members: dict[str, list[discord.Member]]
) -> discord.Embed:
    """
    Builds an embed warning about members who have artfight team roles
    but are not registered in the bot's artfight data.
    
    Last docstring edit: -FoxyHunter V4.3.0
    Last method edit: -FoxyHunter V4.3.0
    
    :param guild: The Discord guild
    :param unregistered_members: Dict mapping team_name -> list of unregistered members
    :return: The warning embed
    """
    total_unregistered = sum(len(members) for members in unregistered_members.values())
    
    embed = discord.Embed(
        title="⚠️ Artfight Member Discrepancy Detected",
        description=(
            f"Found **{total_unregistered}** member(s) with artfight team roles "
            f"who are not registered in the bot's artfight data."
        ),
        color=discord.Color.orange()
    )

    for team_name, members in unregistered_members.items():
        if members:
            member_mentions = "\n".join(f"• {member.mention}" for member in members[:10])
            if len(members) > 10:
                member_mentions += f"\n... and {len(members) - 10} more"
            
            embed.add_field(
                name=f"Team: {team_name} ({len(members)} unregistered)",
                value=member_mentions,
                inline=False
            )

    embed.set_footer(text="Use the buttons below to resolve this discrepancy.")
    
    return embed


class UnregisteredMembersView(discord.ui.View):
    """
    View with buttons to handle unregistered artfight members.
    Allows moderators to either remove roles or register them in the bot.
    
    Last docstring edit: -FoxyHunter V4.3.0
    Last method edit: -FoxyHunter V4.3.0
    """
    
    def __init__(
        self,
        artfight_repo: ArtfightRepo,
        guild: discord.Guild,
        unregistered_members: dict[str, list[discord.Member]],
        on_action_complete: Callable[[], Awaitable[None]] | None = None,
        timeout: float = 3600  # 1 hour timeout
    ):
        super().__init__(timeout=timeout)
        self.artfight_repo = artfight_repo
        self.guild = guild
        self.unregistered_members = unregistered_members
        self.on_action_complete = on_action_complete
        self.message: discord.Message | None = None

    async def on_timeout(self):
        """Disable buttons when the view times out."""
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    @discord.ui.button(label="Register All in Bot", style=discord.ButtonStyle.success, emoji="✅")
    async def register_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Register all unregistered members in the artfight data."""
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You need the 'Manage Roles' permission to do this.",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        registered_count = 0
        failed_count = 0

        for team_name, members in self.unregistered_members.items():
            for member in members:
                try:
                    self.artfight_repo.add_team_member(
                        self.guild.id,
                        team_name,
                        member.id
                    )
                    registered_count += 1
                except Exception:
                    failed_count += 1

        # Disable buttons after action
        for item in self.children:
            item.disabled = True

        result_embed = discord.Embed(
            title="✅ Members Registered",
            description=f"Successfully registered **{registered_count}** member(s) in the artfight data.",
            color=discord.Color.green()
        )
        if failed_count > 0:
            result_embed.add_field(
                name="⚠️ Failures",
                value=f"Failed to register {failed_count} member(s).",
                inline=False
            )

        await interaction.followup.send(embed=result_embed)
        await interaction.message.edit(view=self)

        if self.on_action_complete:
            await self.on_action_complete()

    @discord.ui.button(label="Remove Roles from All", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def remove_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Remove artfight team roles from all unregistered members."""
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You need the 'Manage Roles' permission to do this.",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        removed_count = 0
        failed_count = 0

        teams = self.artfight_repo.get_teams(self.guild.id)

        for team_name, members in self.unregistered_members.items():
            role_id = teams.get(team_name)
            if role_id is None:
                failed_count += len(members)
                continue

            role = self.guild.get_role(role_id)
            if role is None:
                failed_count += len(members)
                continue

            for member in members:
                try:
                    await member.remove_roles(role, reason="Artfight: Member not registered in bot data")
                    removed_count += 1
                except discord.HTTPException:
                    failed_count += 1

        # Disable buttons after action
        for item in self.children:
            item.disabled = True

        result_embed = discord.Embed(
            title="🗑️ Roles Removed",
            description=f"Successfully removed team roles from **{removed_count}** member(s).",
            color=discord.Color.green()
        )
        if failed_count > 0:
            result_embed.add_field(
                name="⚠️ Failures",
                value=f"Failed to remove roles from {failed_count} member(s).",
                inline=False
            )

        await interaction.followup.send(embed=result_embed)
        await interaction.message.edit(view=self)

        if self.on_action_complete:
            await self.on_action_complete()

    @discord.ui.button(label="Dismiss", style=discord.ButtonStyle.secondary, emoji="❌")
    async def dismiss(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Dismiss the warning without taking action."""
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "You need the 'Manage Roles' permission to do this.",
                ephemeral=True
            )
            return

        # Disable buttons
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(view=self)
        await interaction.followup.send("Warning dismissed. No action taken.", ephemeral=True)
