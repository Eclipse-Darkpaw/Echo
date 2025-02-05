#!/usr/bin/python3
import discord
import random
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

from util import setup_logger, logging
from config import BotConfig

logger = setup_logger(log_file='logs/sunreek_info.log', console_log_level=logging.INFO, ignore_discord_logs=False)
bot_config = BotConfig(botname='pawbot')

# Modules
import modules.AntiScam as AntiScam
import modules.General
import modules.Moderation as Mod
import modules.ServerSettings as Settings
import modules.Verification as Verif
import modules.RefManagement as Ref

#Utils
from util.interactions import direct_message

# Keep imports in alphabetical order

VERSION = '4.3.0'

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
    if bot_config.start_notif:
        await direct_message(
            bot,
            f'Running, and active\n'
            '```yml\n'
            f'{'bot_version':<15}: {VERSION}\n'
            f'{'guardians':<15}: {', '.join(bot.get_user(int(guardian)).name for guardian in bot_config.guardians)}\n'
            f'{'prefix':<15}: \'{bot_config.prefix}\'\n'
            f'\n'
            f'{'system':<15}: {platform.system()}\n'
            f'{'version':<15}: {platform.version()}\n'
            f'{'python_version':<15}: {platform.python_version()}\n'
            '```',
            *bot_config.guardians
        )

    logger.info('loading cogs')
    await bot.add_cog(Mod.Moderation(bot))
    await bot.add_cog(modules.General.General(bot))
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

    if not (ctx.guild is None or content.find(AntiScam.BYPASS_CODE) != -1 or ctx.channel.id in scan_ignore):
        await AntiScam.scan_message(ctx)


@bot.event
async def on_member_update(before, after):
    if (before.guild.id == 1054121991365468281 and
            before.guild.get_role(1054160602349703188) not in before.roles and
            before.guild.get_role(1054160602349703188) in after.roles):
        welcome = [f"<@{after.id}> is our newest bean lover",
                   f"<@{after.id}> has stumbled into the bean sanctuary",
                   f"<@{after.id}> has arrived looking for beans"]

        await before.guild.get_channel(1054137434725691393).send(
            content=f"<@&1122978815744950352> {random.choice(welcome)}. Please "
                    f"remember to stop by <#1054672645527969802> for your roles.")

if __name__ == '__main__':
    bot.run(token=bot_config.token, log_handler=None)
