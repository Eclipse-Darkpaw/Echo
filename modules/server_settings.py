import discord

from discord.ext import commands

from base_bot import EchoBot

class Settings(commands.Cog):
    def __init__(self, bot: EchoBot):
        self.bot = bot
        self.servers_settings_repo = bot.repositories['servers_settings_repo']

        self.bot.logger.info(f'✔ Settings cog loaded')

    @commands.hybrid_command(brief="🔐 manage_guild | Set channels the bot uses")
    @commands.has_permissions(manage_guild=True)
    async def channel_setup(self, ctx: commands.Context,
        application: discord.TextChannel = None,
        questioning: discord.TextChannel = None,
        mailbox: discord.TextChannel = None,
        scam_log: discord.TextChannel = None,
        warn_log: discord.TextChannel = None
    ):
        """
        🔐 manage_guild | Sets the channels the bot uses

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.3.0

        :param ctx: Context object for the invoked command
        :param application: Where Membership applications go
        :param questioning: fFor quesitioning unverified applicants
        :param mailbox:
        :param scam_log: Where to log scams
        :param warn_log: Where to log warns
        :return: None
        """
        await ctx.send('⏳ Setting channels...')

        channels = {}
        if application is not None:
            channels['application'] = application.id
        if questioning is not None:
            channels['questioning'] = questioning.id
        if mailbox is not None:
            channels['mailbox'] = mailbox.id
        if scam_log is not None:
            channels['log'] = scam_log.id
        if warn_log is not None:
            channels['warn_log'] = warn_log.id

        self.servers_settings_repo.set_guild_channels(guild_id=str(ctx.guild.id), channels=channels)
        await ctx.send('✅ Channels set.')

    @commands.hybrid_command(brief="🔐 manage_guild | Set roles the bot uses")
    @commands.has_permissions(manage_guild=True)
    async def roles_setup(self, ctx: commands.Context,
        member: discord.Role = None,
        questioning: discord.Role = None,
        unverified: discord.Role = None,
        suspended: discord.Role = None,
        mod: discord.Role = None
    ):
        """
        🔐 manage_guild | Sets the roles the bot uses

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.3.0

        :param ctx: Interaction calling the command
        :param member: Verified member role
        :param questioning: Questioning unverified role
        :param unverified: Unverified member role
        :param suspended: Suspended member role
        :param mod: Moderator role
        :return: None
        """
        await ctx.send('⏳ Setting roles...')

        roles = {}
        if member is not None:
            roles['member'] = member.id
        if questioning is not None:
            roles['questioning'] = questioning.id
        if unverified is not None:
            roles['unverified'] = unverified.id
        if suspended is not None:
            roles['suspended'] = suspended.id
        if mod is not None:
            roles['mod'] = mod.id
        
        self.servers_settings_repo.set_guild_roles(guild_id=str(ctx.guild.id), roles=roles)
        await ctx.send('✅ Roles set.')

    @commands.hybrid_command(brief="🔐 manage_guild | Set guild verification codeword")
    @commands.has_permissions(manage_guild=True)
    async def codeword_setup(self, ctx: commands.Context, 
        codeword: str
    ):
        """
        🔐 manage_guild | Set the guild verification codeword

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.3.0

        :param ctx: Interaction calling the command
        :param codeword: The codeword to be set
        :return: None
        """
        await ctx.send('⏳ Setting code word...')
        self.servers_settings_repo.set_guild_code_word(guild_id=str(ctx.guild.id), code_word=codeword)
        await ctx.send('✅ Code word set.')
