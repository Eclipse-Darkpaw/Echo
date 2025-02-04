#!/usr/bin/python3
import discord
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

# Config
from config import BotConfig

# Utils
from util.interactions import direct_message
from util.logger import setup_logger

# Keep imports in alphabetical order

VERSION = '4.3.0'

logger = setup_logger(log_file='logs/furbot_info.log')
bot_config = BotConfig(botname='furbot')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=bot_config.prefix, intents=intents)
game = discord.Game(f'{bot_config.prefix}help for commands')

@bot.event
async def on_ready():
    """
    Method called when the bot boots and is fully online
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -FoxyHunter V4.3.0
    :return: None
    """

    logger.info(f'We have logged in as {bot.user}')

    await bot.change_presence(activity=game)
    await direct_message(
        bot,
        f'Running, and active\n'
        '```yml\n'
        f'system: {platform.system()}\n'
        f'version: {platform.version()}\n'
        f'python_version: {platform.python_version()}\n'
        '```',
        *bot_config.guardians
    )

    logger.info('loading cogs')
    await bot.add_cog(Mod.Moderation(bot))
    await bot.add_cog(General.General(bot))
    await bot.add_cog(Settings.Settings(bot))
    await bot.add_cog(Ref.RefManagement(bot))
    await bot.add_cog(Verif.Verification(bot))
    logger.info('Cogs loaded')


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

if __name__ == '__main__':
    bot.run(token=bot_config.token, log_handler=None)
