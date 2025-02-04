#!/usr/bin/python3
import discord
import os
import platform

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
"""
Without a specified path, load_dotenv() loads environment variables in the following order:
1. System environment variables (highest priority, unless overwritten).
2. .env file in the working directory (only for unset variables).
Note: Shell config files (e.g., ~/.bashrc) are not read by load_dotenv() 
but can influence the environment before Python runs.
"""

# Modules
import modules.AntiScam as AntiScam
import modules.General as General
import modules.Moderation as Mod
import modules.ServerSettings as Settings
import modules.Verification as Verif
import modules.refManagement as Ref

# Utils
from util.interactions import direct_message
from util.logger import setup_logger

# Keep imports in alphabetical order

VERSION_NUM = '4.3.0'

GUARDIANS = (env := os.getenv('GUARDIANS', '')) and env.split(',') or []
LOGGER = setup_logger(log_file='logs/cyberforcebot_info.log')

prefix = '>'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

game = discord.Game(f'{prefix}help for commands')
client = bot

@bot.hybrid_command()
async def mama(ctx):
    await ctx.send('Drink some water, have a snack, take your meds, and remember Mama Bruise loves you!')


@bot.hybrid_command()
async def microwave(ctx):
    """
    Microwave Gemini
    :param ctx:
    :return:
    """
    await ctx.send('You put Gemini in the microwave for 2 minutes. She comes out nice and warm when you hug '
                           'her')
    await ctx.send('https://i.imgur.com/eOPKEV4.gif')


@bot.hybrid_command()
async def hug(ctx):
    """
    Hug Gemini
    :param ctx:
    :return:
    """
    await ctx.reply('You give Gemini a hug. You can smell a faint citrus scent when you do.')
# ADD NEW METHODS HERE!

@bot.command()
async def sync(interaction: discord.Interaction):
    await interaction.send('Syncing Tree', ephemeral=False)
    guild = discord.Object(id=interaction.guild.id)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    await interaction.send("tree synced", ephemeral=True)


@bot.event
async def on_ready():
    """
    Method called when the bot boots and is fully online
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -FoxyHunter V4.3.0
    :return: None
    """

    LOGGER.info(f'We have logged in as {bot.user}')

    await client.change_presence(activity=game)
    await direct_message(
        bot,
        f'Running, and active\n'
        '```yml\n'
        f'system: {platform.system()}\n'
        f'version: {platform.version()}\n'
        f'python_version: {platform.python_version()}\n'
        '```',
        *GUARDIANS
    )

    LOGGER.info('loading cogs')
    await bot.add_cog(Mod.Moderation(bot))
    await bot.add_cog(General.General(bot))
    await bot.add_cog(Settings.Settings(bot))
    await bot.add_cog(Ref.RefManagement(bot))
    await bot.add_cog(Verif.Verification(bot))
    LOGGER.info('Cogs loaded')


scan_ignore = [1054172309147095130]


@bot.event
async def on_message(ctx: discord.Interaction):
    """
    Calls methods for every message.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V4.0.0
    :param ctx: The interaction calling the function
    """
    await bot.process_commands(ctx)

    if ctx.author.bot:
        return

    content = ctx.content.lower()

    if not (ctx.guild is None or content.find(AntiScam.code) != -1 or ctx.channel.id in scan_ignore):
        await AntiScam.scan_message(ctx)


client.run(os.getenv('CYBERFORCE_BOT_TOKEN'))
