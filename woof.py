#!/usr/bin/python3
import discord
import difflib
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
    TruthOrDare,
)
from repositories import (
    TruthOrDareRepo
)
from util import (
    direct_message
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = EchoBot(
    name='woof',
    version_num='5.0.0',
    console_logging=True,
    file_logging=False,
    intents=intents
)

bot.add_repository(TruthOrDareRepo())
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
    if bot.config.start_notif and not getattr(bot, '_start_notif_sent', False):
        bot._start_notif_sent = True
        await direct_message(
            bot,
            f'Running, and active\n'
            '```yml\n'
            f'{'bot_version':<15}: {bot.version_num}\n'
            f'{'guardians':<15}: ' + 
            ', '.join(
                (u.name if (u := bot.get_user(int(guardian))) else f"{guardian}")
                for guardian in bot.config.guardians
            ) + "\n"
            f'{'prefix':<15}: \'{bot.config.prefix}\'\n'
            f'\n'
            f'{'system':<15}: {platform.system()}\n'
            f'{'release':<15}: {platform.release()}\n'
            f'{'python_version':<15}: {platform.python_version()}\n'
            '```',
            *bot.config.guardians
        )

    bot.logger.info('loading cogs')
    await bot.add_cog(General(bot))
    await bot.add_cog(TruthOrDare(bot))
    bot.logger.info('Cogs loaded')

@bot.event
async def on_message(msg: discord.Message):
    await bot.process_commands(msg)

    if msg.author.bot:
        return
    
    if len(msg.content) >= 10 and difflib.SequenceMatcher(
        None,
        'do you remember',
        msg.content.lower()
    ).ratio() >= 0.8:
        await msg.channel.send('No')

if __name__ == '__main__':
    bot.run(token=bot.config.token, log_handler=None)
