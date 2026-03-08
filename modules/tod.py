import discord
import secrets
import time

from base_bot import EchoBot
from collections import deque
from datetime import datetime
from discord.ext import commands, tasks
from discord.ui import View
from util import SemanticSimilarityChecker

class TruthOrDare(commands.Cog):
    def __init__(self, bot: EchoBot):
        self.bot = bot
        self.tod_repo = bot.repositories['truth_or_dare_repo']

        self.last_dares_sent: dict[int, int] = {}
        """Unix timestamps of the last time a dare was sent (per guild)"""
        self.sent_dares_indexes: dict[int, deque] = {}
        """Deques of the last sent dare indexes (LIFO) (per guild)"""

        for guild_id in self.tod_repo.get_guilds():
            dares_count = self.tod_repo.get_dares_count(int(guild_id))
            self.sent_dares_indexes[int(guild_id)] = deque(maxlen=dares_count - int((dares_count * 0.3)))
        
        self.similarity_checker = SemanticSimilarityChecker()

        self.bot.logger.info(f'✔ TruthOrDare cog loaded')


    @tasks.loop(hours=3)
    async def clear_dequeues(self):
        """Clear the dare dequeues after 24h of inactivity (per guild)"""
        for guild_id, timestamp in self.last_dares_sent:
            if int(time.time()) - timestamp >= 86400:
                self.sent_dares_indexes[guild_id].clear()
    
    @commands.hybrid_command(brief='Get a random dare')
    @commands.guild_only()
    async def dare(self, ctx: commands.Context):
        """
        Returns a random dare from the server configured dares.
        The method tries to avoid sending the same dare twice in
        a short time.

        Last docstring edit: -FoxyHunter v5.0.0
        Last method edit: -FoxyHunter v5.0.0

        :param ctx: Context object for the invoked command
        :return: None
        """
        await ctx.defer()
        dares_count = self.tod_repo.get_dares_count(ctx.guild.id)
        if dares_count <= 0:
            await ctx.send('Give me some dares first 🫵')
            return

        dare_index = secrets.randbelow(dares_count)

        while dare_index in self.sent_dares_indexes[ctx.guild.id]:
            dare_index = secrets.randbelow(dares_count)
        
        self.sent_dares_indexes[ctx.guild.id].append(dare_index)
        self.last_dares_sent[ctx.guild.id] = int(time.time())

        dare = self.tod_repo.get_dare(ctx.guild.id, dare_index)
        dare_added_by_user = ctx.guild.get_member(dare['user_id'])

        await ctx.send(embed=discord.Embed(
            description=dare['dare_str'],
            color=discord.Color.teal(),
            timestamp=datetime.fromtimestamp(dare['unix_time'])
        ).set_author(
            name=f'Added by: {dare_added_by_user.name}',
            icon_url=dare_added_by_user.avatar.url
        ).set_footer(
            text=f'Current index: {dare_index} | Added on:'
        ))

    @commands.hybrid_command(brief='Add a new dare')
    @commands.guild_only()
    async def add_dare(self, ctx: commands.Context, dare: str):
        """
        Add a new dare to the list of this guild.

        Your new dare is checked against existing ones
        on similarity, you will be asked to confirm if
        similar dares are found.

        Last docstring edit: -FoxyHunter v5.0.0
        Last method edit: -FoxyHunter v5.0.0

        :param ctx: Context object for the invoked command
        :param dare: The dare to add
        :return: None
        """
        await ctx.defer()
        ephemeral = ctx.interaction is not None

        dares = self.tod_repo.get_dares(ctx.guild.id)
        if dares is not None:
            similar_dares: set[str] = self.similarity_checker.find_similar(
                input_str=dare,
                compare_str_list=[
                    dare['dare_str'] for dare in dares
                ]
            )

        save_dare = True

        if dares is not None and len(similar_dares) > 0:
            similar_msg_part = '\n'.join(f'- {similar_dare}' for similar_dare in similar_dares)
            msg = (
                '🫷 **Hold on a moment**\n'
                'This dare might already be added before,\n'
                'I found these dares that look similar to what you\'re adding:\n'
                f'{similar_msg_part}\n'
                'Are you sure you want to add:\n'
                f'`{dare}` ?'
            )

            view = self.DareAddConfirmView()
            await ctx.send(msg, view=view, ephemeral=ephemeral)
            await view.wait()
            
            if view.confirmed is None:
                await ctx.send('Timed out', ephemeral=ephemeral)
                return
            save_dare = view.confirmed
        
        if save_dare:
            self.tod_repo.set_dare(
                guild_id=ctx.guild.id,
                user_id=ctx.author.id,
                dare_str=dare
            )

            if ctx.guild.id not in self.sent_dares_indexes:
                dares_count = self.tod_repo.get_dares_count(ctx.guild.id)
                self.sent_dares_indexes[ctx.guild.id] = deque(maxlen=dares_count - int((dares_count * 0.3)))

            await ctx.send(f'Dare added\n-# {dare}', ephemeral=ephemeral)
        else:
            await ctx.send('Cancelled', ephemeral=ephemeral)
    
    @commands.hybrid_command(brief='Remove a dare')
    @commands.guild_only()
    async def remove_dare(self, ctx: commands.Context, index: int):
        """
        Remove a dare by its index

        Removing a dare shifts indexes and clears

        Last docstring edit: -FoxyHunter v5.0.0
        Last method edit: -FoxyHunter v5.0.0

        :param ctx: Context object for the invoked command
        :param index: The index of the dare to remove
        :return: None
        """
        await ctx.defer()
        removed_dare = self.tod_repo.remove_dare(
            guild_id=ctx.guild.id,
            index=index
        )
        if removed_dare is None:
            await ctx.send(f'No dare with index: {index} found\nNone deleted.')
            return
        await ctx.send(f'---\n{removed_dare}\n---\nRemoved')
        self.sent_dares_indexes[ctx.guild.id].clear()
        await ctx.send((
            'Reminder that the indexes of the dares have now shifted\n'
            'The buffer of recently sent dares has now been cleared'
            ))
    
    class DareAddConfirmView(View):
        def __init__(self):
            super().__init__(timeout=180)
            self.confirmed: bool | None = None

        @discord.ui.button(label='Cancel', style=discord.ButtonStyle.danger)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            self.confirmed = False
            self.stop()
        
        @discord.ui.button(label='Yes I\'m sure', style=discord.ButtonStyle.green)
        async def keep(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            self.confirmed = True
            self.stop()