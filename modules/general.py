import discord
import time

from base_bot import EchoBot
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: EchoBot):
        self.bot = bot
        self.bot.logger.info(f'✔ General cog loaded')

    @commands.hybrid_command(brief="Get bot latency")
    async def ping(self, ctx: commands.Context):
        """
        Returns how long it takes the bot to send a message

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0

        :param ctx: Context object for the invoked command
        :return: None
        """
        start = time.time()
        x = await ctx.send('Pong!')
        ping = time.time() - start
        edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
        await x.edit(content=edit)

    @commands.hybrid_command(brief="Get bot uptime")
    async def uptime(self, ctx: commands.Context):
        """
        Displays the time the bot has been running for

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0

        :param ctx: Context object for the invoked command
        :return: None
        """
        formatted_uptime = f'{str(self.bot.uptime).split('.')[0].replace(':', 'h', 1).replace(':', 'm', 1)}s'
        await ctx.send(f'Online for {formatted_uptime}\n-# Started <t:{int(self.bot.start_time)}:R>')

    @commands.hybrid_command(brief="🔐 guardians | Sync server app cmd tree with global set")
    async def sync(self, ctx: commands.Context):
        """
        Copies global application commands to this guild and synchronizes them
        with Discord. Use after adding or changing hybrid/slash commands.

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0

        :param ctx: Context object for the invoked command
        :return: None
        """
        if str(ctx.author.id) in self.bot.config.guardians:
            await ctx.send('Syncing Tree', ephemeral=False)
            guild = discord.Object(id=ctx.guild.id)
            ctx.bot.tree.copy_global_to(guild=guild)
            await ctx.bot.tree.sync(guild=guild)
            await ctx.send("tree synced", ephemeral=True)

    @commands.hybrid_command(brief="🔐 guardians | Quits the active bot")
    async def quit(self, ctx: commands.Context):
        """
        🔐 guardians | Quits the active bot

        If the bot is run using an auto-start & lifecycle-managing
        system such as systemd, the bot may automatically be restarted
        by that system.

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0

        :param ctx: Context object for the invoked command
        :return: N/A. program closes
        """

        if str(ctx.author.id) in self.bot.config.guardians:
            self.bot.logger.info(f'{ctx.author.name} issued quit command')
            await ctx.reply('Goodbye :wave:')
            await ctx.bot.change_presence(activity=discord.Game('Going offline'))
            await ctx.bot.close()
        else:
            await ctx.reply('You do not have permission to turn me off!')

    @commands.hybrid_command(brief="Easter egg")
    async def huh(self, ctx: commands.Context):
        """
        Easter egg

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0

        :param ctx: Context object for the invoked command
        :return: None
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

    @commands.hybrid_command(brief="Get bot version")
    async def version(self, ctx: commands.Context):
        """
        Displays the version of the bot being used

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.4.0

        :param ctx: Context object for the invoked command
        :return: None
        """
        await ctx.reply(f'I am currently running version {self.bot.version_num}')