import discord

from discord.ui import View
from repositories import ServersSettingsRepo


def build_survive_embed() -> discord.Embed:
    """
    Builds the embed for the survive purge message.

    :return: The embed
    """
    embed = discord.Embed(
        title="Nuke is comin 💥",
        description=(
            "If you're active in the server or a patreon you're safe 😎\n"
            "For anyone who isn't active, press this button to protect yourself, or get 🦶"
        ),
        color=discord.Color.blue()
    )

    return embed


class SurvivePurgeView(View):
    """
    Persistent view with the 'Survive Purge' button.
    Survives bot restarts via custom_id.
    """
    def __init__(self, servers_repo: ServersSettingsRepo = None):
        super().__init__(timeout=None)
        self.servers_repo = servers_repo

    def set_repo(self, servers_repo: ServersSettingsRepo):
        """Set the repository after initialization (for persistent view registration)."""
        self.servers_repo = servers_repo

    @discord.ui.button(
        label="Keep me safe",
        style=discord.ButtonStyle.primary,
        custom_id="purge_survive_button",
    )
    async def survive_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle the survive button click."""
        if self.servers_repo is None:
            await interaction.response.send_message(
                "Uh- I'm sleepy, gimma a sec 🥱",
                ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)
        user_id = interaction.user.id

        # Check if user is already on the list
        survivors = self.servers_repo.get_purge_survivors(guild_id) or []

        if user_id in survivors:
            await interaction.response.send_message(
                "U already pressed it before 🫷",
                ephemeral=True
            )
            return

        # Add user to survivors list
        self.servers_repo.add_purge_survivor(guild_id, user_id)

        await interaction.response.send_message(
            "You're safe now 🤝",
            ephemeral=True
        )
