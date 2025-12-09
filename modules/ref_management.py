import discord
from discord.ext import commands

from base_bot import EchoBot
from config import Paths

class RefManagement(commands.Cog):
    def __init__(self, bot: EchoBot):
        self.bot = bot
        self.bot.logger.info(f'✔ RefManagement cog loaded')

    @commands.hybrid_command(brief="Set your refs")
    async def set_ref(self, ctx: commands.Context):
        """
        Sets a user's ref
        Overwrites existing ref, use add_ref.

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.3.0

        :param ctx: Context object for the invoked command
        :return: None
        """
        try:
            trim = ctx.message.content[8:]
            command = trim.split('\n')

            if ctx.channel.nsfw:
                path = Paths.get_nsfw_ref_path(ctx.author.id)
            else:
                path = Paths.get_ref_path(ctx.author.id)

            with open(path, 'w') as refs:
                for line in command:
                    try:
                        refs.write(line + '\n')
                    except UnicodeEncodeError:
                        await ctx.send('Line failed to save. Please use ASCII characters\n> ' + line)
                for ref in ctx.message.attachments:
                    refs.write(ref.url + '\n')
            await ctx.reply(content='Refs set! Do not delete that message or the refs wont appear!')
        except IndexError:
            await ctx.send('No ref_sheet attached!')

    @commands.hybrid_command(brief="Add a ref to your refs")
    async def add_ref(self, ctx: commands.Context):
        """
        Adds refs to a user.

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.3.0

        :param ctx: Context object for the invoked command
        :return: None
        """
        try:

            if ctx.channel.nsfw:
                path = Paths.get_nsfw_ref_path(ctx.author.id)
            else:
                path = Paths.get_ref_path(ctx.author.id)

            with open(path, 'a') as refs:
                for line in ctx.message.content:
                    try:
                        refs.write(line + '\n')
                    except UnicodeEncodeError:
                        for char in line:
                            try:
                                refs.write(char)
                            except UnicodeEncodeError:
                                await ctx.send('Line failed to save. Please use ASCII characters\n> ' + char)
                for ref_sheet in ctx.message.attachments:
                    refs.write(ref_sheet.url + '\n')
            await ctx.reply(content='Refs added!')
        except IndexError:
            await ctx.send('No ref attached!')

    @commands.hybrid_command(brief="Get someone's refs")
    async def ref(self, ctx: commands.Context, user: discord.User = None):
        """
        Retrieves a users refs

        Last docstring edit: -FoxyHunter V4.4.0
        Last method edit: -FoxyHunter V4.3.0

        :param ctx: Context object for the invoked command
        :param user: User to search for
        :return: None
        """
        if user is None:
            target = ctx.author.id
        else:
            target = user.id

        msg = await ctx.send('Finding ref, please wait')
        try:

            if ctx.channel.nsfw:
                path = Paths.get_nsfw_ref_path(target)
            else:
                path = Paths.get_ref_path(target)
            ref_sheet = open(path)
            await msg.edit(content='Ref Found! Uploading, Please wait!')
            await ctx.reply(content=ref_sheet.read())
        except FileNotFoundError:
            if ctx.channel.nsfw:
                await msg.edit(content='User has not set NSFW ref. Retrieving SFW ref')
                path = Paths.get_ref_path(target)
                ref_sheet = open(path)
                await msg.edit(content='Ref Found! Uploading, Please wait!')
                await msg.edit(content=ref_sheet.read())
            else:
                await msg.edit(content='User has not set their SFW ref.')
