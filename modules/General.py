import discord
import sys
import time

import main
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.hybrid_command()
    async def ping(self, ctx):
        """
        Returns how long it takes the bot to send a message
        Last docstring edit: -Autumn V4.0.0
        Last method edit: -Autumn V4.0.0
        :param ctx: message that called the quit command
        :return: None
        """
        start = time.time()
        x = await ctx.send('Pong!')
        ping = time.time() - start
        edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
        await x.edit(content=edit)

    @commands.hybrid_command()
    async def quit(self, ctx):
        """
        Quits the bot, and closes the program. Replys and updates the game status to alert users to it quitting.
        Last docstring edit: -Autumn V4.0.0
        Last method edit: -Autumn V4.0.0
        :param ctx: message that called the quit command
        :return: N/A. program closes
        """

        if ctx.author.id == main.eclipse_id or ctx.author.guild_permissions.administrator:
            await ctx.send('Goodbye :wave:')
            await ctx.bot.change_presence(activity=discord.Game('Going offline'))
            sys.exit()
        else:
            await ctx.send('You do not have permission to turn me off!')