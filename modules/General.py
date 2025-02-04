import discord
import logging
import os
import time

from discord.ext import commands

from config import BotConfig

VERSION_NUM = '4.3.0'
START_TIME = time.time()
GUARDIANS = BotConfig._retrieve_guardians()
_Logger = logging.getLogger('modules')

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def ping(self, ctx: discord.Interaction):
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
    async def uptime(self, ctx: discord.Interaction):
        """
        Displays the time the bot has been running for.
        Last docstring edit: -Autumn V3.3.4
        Last method edit: -FoxyHunter V4.3.0
        :param message: message calling the bot
        :return: None
        """
        days = int(time.strftime('%j', time.gmtime(time.time() - START_TIME)))
        await ctx.send(time.strftime(f'Online for {days - 1} days %H:%M:%S\nStarted <t:{int(START_TIME)}:R>',
                                          time.gmtime(time.time() - START_TIME)))

    @commands.hybrid_command()
    async def sync(self, ctx: discord.Interaction):
        await ctx.send('Syncing Tree', ephemeral=False)
        guild = discord.Object(id=ctx.guild.id)
        ctx.bot.tree.copy_global_to(guild=guild)
        await ctx.bot.tree.sync(guild=guild)
        await ctx.send("tree synced", ephemeral=True)

    @commands.hybrid_command()
    async def quit(self, ctx: discord.Interaction):
        """
        Quits the active bot. Admin only.
        Last docstring edit: -Autumn V4.0.0
        Last method edit: -FoxyHunter V4.3.0
        :param ctx: message that called the quit command
        :return: N/A. program closes
        """

        if str(ctx.author.id) in GUARDIANS or ctx.author.guild_permissions.administrator:
            _Logger.info(f'{ctx.author.name} issued quit command')
            await ctx.reply('Goodbye :wave:')
            await ctx.bot.change_presence(activity=discord.Game('Going offline'))
            await ctx.bot.close()
        else:
            await ctx.reply('You do not have permission to turn me off!')

    @commands.hybrid_command(name='huh')
    async def huh(self, ctx: discord.Interaction):
        """
        Easter egg
        Last docstring edit: -Autumn V1.14.4
        Last method edit: -Autumn V 4.0.0
        :param ctx: Message calling the command
        """
        await ctx.reply("We're no Strangers to love\n"
                               "You know the rules and so do I!~\n"
                               "A full commitments what I'm thinkin' of\n"
                               "You wouldn't get this from, Any other guy.\n"
                               "\n"
                               "I just wanna tell you how I'm feeling\n"
                               "gotta make you, understand!\n"
                               "\n"
                               "Never gonna give you up, Never gonna let you down\n"
                               "Never gonna run around, and desert you\n"
                               "Never gonna make you cry, Never gonna say goodbye\n"
                               "Never gonna tell a lie, and hurt you")

    @commands.hybrid_command()
    async def version(self, ctx: discord.Interaction):
        """
        Displays the version of the bot being used
        Last docstring edit: -Autumn V4.0.1
        Last method edit: -FoxyHunter V4.3.0
        :param ctx: Message calling the bot
        :return: None
        """
        await ctx.reply(f'I am currently running version {VERSION_NUM}')