import discord
import sys
import time

import main
from discord.ext import commands

version_num = '4.0.1'

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
    async def quit(self, ctx: discord.Interaction):
        """
        Quits the active bot. Admin only.
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

    @commands.hybrid_command(name='huh')
    async def huh(self, ctx: discord.Interaction):
        """
        Easter egg
        Last docstring edit: -Autumn V1.14.4
        Last method edit: -Autumn V 4.0.0
        :param ctx: Message calling the command
        """
        await ctx.channel.send("We're no Strangers to love\n"
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
        Last method edit: -Autumn V4.0.0
        :param ctx: Message calling the bot
        :return: None
        """
        await ctx.channel.send(f'I am currently running version {version_num}')