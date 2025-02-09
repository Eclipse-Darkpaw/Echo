#!/usr/bin/python3
import discord
import logging
import random
import platform

from base_bot import EchoBot
from dotenv import load_dotenv

load_dotenv()
"""
Without a specified path, load_dotenv() loads environment variables in the following order:
1. System environment variables (highest priority, unless overwritten).
2. .env file in the working directory (only for unset variables).
Note: Shell config files (e.g., ~/.bashrc) are not read by load_dotenv() 
but can influence the environment before Python runs.
"""

from modules import (
    General,
    Moderation as Mod,
    ServerSettings as Settings,
    Verification as Verif,
    RefManagement as Ref
)

from repositories import (
    ServersSettingsRepo
)

from util import (
    scan_message,
    BYPASS_CODE,
    direct_message
)

# Keep imports in alphabetical order

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = EchoBot(
    name='luana',
    version_num='4.3.0',
    console_logging=True,
    file_logging=True,
    intents=intents
)

bot.add_repository(ServersSettingsRepo())

game = discord.Game(f'{bot.config.prefix}help for commands')

@bot.event
async def on_ready():
    """
    Method called when the bot boots and is fully online
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -FoxyHunter V4.3.0
    :return: None
    """

    bot.logger.info(f'We have logged in as {bot.user}')

    await bot.change_presence(activity=game)
    if bot.config.start_notif:
        await direct_message(
            bot,
            f'Running, and active\n'
            '```yml\n'
            f'{'bot_version':<15}: {bot.version_num}\n'
            f'{'guardians':<15}: {', '.join(bot.get_user(int(guardian)).name for guardian in bot.config.guardians)}\n'
            f'{'prefix':<15}: \'{bot.config.prefix}\'\n'
            f'\n'
            f'{'system':<15}: {platform.system()}\n'
            f'{'version':<15}: {platform.version()}\n'
            f'{'python_version':<15}: {platform.python_version()}\n'
            '```',
            *bot.config.guardians
        )

    bot.logger.info('loading cogs')
    await bot.add_cog(Mod.Moderation(bot))
    await bot.add_cog(General.General(bot))
    await bot.add_cog(Settings.Settings(bot))
    await bot.add_cog(Ref.RefManagement(bot))
    await bot.add_cog(Verif.Verification(bot))
    bot.logger.info('Cogs loaded')


scan_ignore = [1054172309147095130]

@bot.event
async def on_message(msg: discord.Message):
    """
    Calls methods for every message.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V4.0.0
    :param ctx: The interaction calling the function
    """
    await bot.process_commands(msg)

    if msg.author.bot:
        return

    content = msg.content.lower()

    if not (msg.guild is None or content.find(BYPASS_CODE) != -1 or msg.channel.id in scan_ignore):
        await scan_message.scan_message(
            msg,
            bot.repositories['servers_settings_repo'].get_guild_channel(msg.guild.id, 'log')
        )

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
    bot.run(token=bot.config.token, log_handler=None)
