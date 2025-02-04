#!/usr/bin/python3
import discord
import json
import platform

from datetime import datetime, timezone
from discord.ext import commands, tasks
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
import modules.Artfight as Artfight

# Config
from config import BotConfig

# Utils
from util.fileManagement import resource_file_path
from util.interactions import direct_message
from util.logger import setup_logger, logging

# Keep imports in alphabetical order

VERSION = '4.3.0'

logger = setup_logger(log_file='logs/sunreek_info.log')
bot_config = BotConfig(botname='sunreek')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=bot_config.prefix, intents=intents)
game = discord.Game(f'{bot_config.prefix}help for commands')

with open(resource_file_path + 'servers.json') as file:
    DATA = json.load(file)

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
    #await bot.add_cog(Artfight.Artfight(bot))
    logger.info('Cogs loaded')


scan_ignore = [688611557508513854]

@bot.event
async def on_message(ctx: discord.Interaction):
    """
    Calls methods for every message.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -FoxyHunter V4.3.0
    :param ctx: The interaction calling the function
    """

    from modules.Artfight import Artfight as af
    await bot.process_commands(ctx)
    if ctx.author.bot:
        return

    content = ctx.content.lower()

    if not (ctx.guild is None or content.find(AntiScam.code) != -1 or ctx.channel.id in scan_ignore):
        await AntiScam.scan_message(ctx)
    
# ---
# Commands
# ---

cursed_keys_running = False
blessed_keys_running = False
crsd_keys = []
blsd_keys = []
player_role_id = 863630913686077450

async def cursed_keys(message):
    """
    Handles all crsdky game functions and methods.
    Last docstring edit: -Autumn V1.14.5
    Last method edit: -Autumn V3.5.2
    :param message:
    :return:
    """
    global cursed_keys_running
    global crsd_keys

    command = message.content[1:].split(' ', 2)
    if len(command) == 1 or command[1] == 'help':
        overview = discord.Embed(title='Crsd Ky Overview',
                                 description='Welcome, to a brutal game called "CRSD KY" (Idea by Reek and Isybel)\n\n'
                                             ' The main of the game is to avoid a certain key/letter on your keyboard '
                                             '(mostly vowels), But still try to make sure everyone understands what you'
                                             ' are trying to say. The last survivor standing wins and will be given a '
                                             'custom role',
                                 color=0x45ffff)
        overview.add_field(name='RULES',
                           value="-You can't the leave the game until you lose and the bot will remove your roles to "
                                 "get rid of the curse"
                                 "\n-Once you make a mistake, you will be instantly disqualified"
                                 "\n-This challenge will apply to every chat on this server, so be careful"
                                 "\n-you have to use an alt word to describe what you want to say rather censor that "
                                 "word"
                                 "\n-Abusing rule loop hole is not allowed"
                                 "\n-Using emoji contain that key also not allowed"
                                 "\n-If you don't talk in general, you'll also lose (we check)",
                           inline=False)
        await message.reply(embed=overview)
        overview.add_field(name='QnA', value='', inline=False)
        overview.add_field(name='Q: What does "crsd ky" mean?',
                           value='A: It\'s "Cursed Key" but get rid of the vowels cause they are cursed.')
        overview.add_field(name='Q: What made you come up with this game?',
                           value='A: Isybel is upset she can\'t curse in my server, so she cursed me by removing my '
                                 'ability to use the letter "a" and I took it as a challenge xD (But I lost rip) ')
        overview.add_field(name='Q: What do I do if i got removed but dont think I should\'ve been?',
                           value='A: contact a moderator, and we\'ll look into your case and determine if you should '
                                 'still be in the game or not')
    elif command[1] == 'list':
        if len(crsd_keys) == 0:
            await message.reply('there are no cursed keys')
        else:
            await message.reply('cursed keys are: '+str(crsd_keys))
    elif command[1] == 'join':
        if not cursed_keys_running:
            if message.guild.get_role(player_role_id) in message.author.roles:
                await message.reply('You are already a part of this game!')
            else:
                await message.author.add_roles(message.guild.get_role(player_role_id))
                await message.reply('Joined the game!')
        else:
            await message.reply("Unable to join. a game is already running")
    elif command[1] == 'leave':
        await message.author.remove_roles(message.guild.get_role(player_role_id))
        await message.reply('You have been removed from the game')
    elif command[1] == 'set':
        chars = command[2].split(' ')
        keys = []
        for char in chars:
            if len(char) > 1:
                pass
            else:
                keys.append(char.lower())
                crsd_keys = keys
        await message.reply('Cursed Keys set: ' + str(crsd_keys))
    elif command[1] == 'start':
        if message.author.guild_permissions.manage_roles:
            cursed_keys_running = True
            if len(crsd_keys) == 0:
                await message.reply('Unable to start game! No Cursed Keys set!')
            else:
                await message.reply('<@&863630913686077450> The game is starting! Cursed Keys are ' + str(crsd_keys))
        else:
            await message.reply('Invalid permissions')
    elif command[1] == 'resetPlayers':
        if message.author.guild_permissions.manage_roles:
            for member in message.guild.get_role(player_role_id).members:
                await member.remove_roles(message.guild.get_role(player_role_id))
        await message.reply('Players reset')
    elif command[1] == 'stop':
        if message.author.guild_permissions.manage_roles:
            cursed_keys_running = False
            await message.reply('Game Stopped')
        else:
            await message.reply('Invalid Permissions')
    elif command[1] == 'numleft':
        await message.reply(str(len(message.guild.get_role(player_role_id).members)))


async def blessed_keys(message):
    """
        Handles all Blessed Key game functions and methods.
        Last docstring edit: -Autumn V3.5.0
        Last method edit: -Autumn V3.5.2
        :param message:
        :return:
    """
    global cursed_keys_running
    global blessed_keys_running
    global blsd_keys

    command = message.content[1:].split(' ', 2)
    if len(command) == 1 or command[1] == 'help':
        overview = discord.Embed(title='Blessed Ky Overview',
                                 description='Welcome, to a brutal game called "Blessed Key" (Idea by Reek)\n\n'
                                             'The main of the game is to use a certain key/letter on your keyboard '
                                             'in every message you send, but still try to make sure everyone '
                                             'understands what you are trying to say. The last survivor standing wins '
                                             'and will be given a custom role',
                                 color=0x45ffff)
        overview.add_field(name='RULES',
                           value="-You can't the leave the game until you lose and the bot will remove your roles to "
                                 "get rid of the curse"
                                 "\n-Once you make a mistake, you will be instantly disqualified"
                                 "\n-This challenge will apply to every chat on this server, so be careful"
                                 "\n-you have to use a letter in every single sentence"
                                 "\n-Abusing rule loop hole is not allowed"
                                 "\n-Using emoji contain that key also not permitted"
                                 "\n-If you don't talk in general, you'll also lose (we check)",
                           inline=False)
        await message.reply(embed=overview)
        overview.add_field(name='QnA', value='', inline=False)
        overview.add_field(name='Q: What does "crsd ky" mean?',
                           value='A: It\'s "Cursed Key" but get rid of the vowels cause they are cursed.')
        overview.add_field(name='Q: What made you come up with this game?',
                           value='A: Isybel is upset she can\'t curse in my server, so she cursed me by removing my '
                                 'ability to use the letter "a" and I took it as a challenge xD (But I lost rip) ')
        overview.add_field(name='Q: What do I do if i got removed but dont think I should\'ve been?',
                           value='A: contact a moderator, and we\'ll look into your case and determine if you should '
                                 'still be in the game or not')
    elif command[1] == 'list':
        if len(blsd_keys) == 0:
            await message.reply('there are no blessed keys')
        else:
            await message.reply('blessed keys are: ' + str(blsd_keys))
    elif command[1] == 'join':
        if not blessed_keys_running:
            if message.guild.get_role(player_role_id) in message.author.roles:
                await message.reply('You are already a part of this game!')
            else:
                await message.author.add_roles(message.guild.get_role(player_role_id))
                await message.reply('Joined the game!')
        else:
            await message.reply("Unable to join. a game is already running")
    elif command[1] == 'leave':
        await message.author.remove_roles(message.guild.get_role(player_role_id))
        await message.reply('You have been removed from the game')
    elif command[1] == 'set':
        chars = command[2].split(' ')
        keys = []
        for char in chars:
            if len(char) > 1:
                pass
            else:
                keys.append(char.lower())
                blsd_keys = keys
        await message.reply('Blessed Keys set: ' + str(blsd_keys))
    elif command[1] == 'start':
        if message.author.guild_permissions.manage_roles:
            cursed_keys_running = True
            if len(blsd_keys) == 0:
                await message.reply('Unable to start game! No Cursed Keys set!')
            else:
                await message.reply(f'<@&863630913686077450> The game is starting! blessed Keys are ' + str(
                        blsd_keys))
        else:
            await message.reply('Invalid permissions')
    elif command[1] == 'resetPlayers':
        if message.author.guild_permissions.manage_roles:
            for member in message.guild.get_role(player_role_id).members:
                await member.remove_roles(message.guild.get_role(player_role_id))
        await message.reply('Players reset')
    elif command[1] == 'stop':
        if message.author.guild_permissions.manage_roles:
            blessed_keys_running = False
            await message.reply('Game Stopped')
        else:
            await message.reply('Invalid Permissions')
    elif command[1] == 'numleft':
        await message.reply(str(len(message.guild.get_role(player_role_id).members)))


# Todo: look over and verify the purge code will work
@bot.hybrid_command()
async def purge(ctx: discord.Interaction, kick: bool):
    """
    method removes all members with the unverified role from Rikoland
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -FoxyHunter V4.3.0
    :param message: Message that called the bot
    :return: None
    """
    unverified_role_id = DATA[str(ctx.guild.id)]["roles"]['unverified']

    if ctx.author.guild_permissions.manage_roles:
        await ctx.channel.send('├ FILTERING MEMBER LIST')
        unverified_ppl = ctx.guild.get_role(unverified_role_id).members
        await ctx.channel.send('├ BEGINNING PURGE\n├┐')
        num_kicked = 0
        msg = ''
        for member in unverified_ppl:
            if kick:
                try:
                    await member.kick(reason='Server purge.')
                    num_kicked += 1
                    add = F'│├ <@{member.id}> KICKED\n'
                except discord.Forbidden:
                    add = F'│├ <@{member.id}> FORBIDDEN\n'
            else:
                num_kicked += 1
                add = F'│├ <@{member.id}> FOUND\n'

            if len(msg) + len(add) >= 2000:
                await ctx.channel.send(msg)
                msg = add
            else:
                msg += add
        await ctx.channel.send(msg)
        await ctx.reply(str(len(unverified_ppl)) + ' members purged from Rikoland')
        if kick:
            logger.debug(f'├ {num_kicked} MEMBERS KICKED')
        else:
            logger.debug(f'├ {num_kicked} MEMBERS TO BE KICKED')
    else:
        await ctx.reply('Error 403: Forbidden\nInsufficient Permissions')

@bot.hybrid_command()
async def prune(message):
    """
    Removes inactive members from the server
    Does this do its job? V3.5.2
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -FoxyHunter V4.3.0
    :param message:
    :return: NoneType
    """
    await direct_message(bot, '`STARTING PURGE`', *bot_config.guardians)
    if message.author.guild is not None and message.author.guild_permissions.kick_members:
        # only run if in a guild and the user could do this manually.
        members = message.guild.members
        ignore_roles = [612554353764597760, 612939346479153172, 655755488100745247, 1078607646199926844,
                        1199610730899578960, 1069839195553669192]
        num_kicked = 0
        forbidden = 0
        logger.debug('├ GETTING MEMBER LIST')
        logger.debug('├ PURGING SERVER')
        logger.debug('├┐')
        for member in members:
            kicked = False
            if member.id == 815418445192888321:
                continue
            for role in member.roles:
                if kicked:
                    break
                if role.id in ignore_roles:
                    logger.debug(f'│├ {member.id} SAFE')
                    kicked = True
                    break
                else:
                    try:
                        # await member.kick(reason="*T H E   P U R G E*")
                        logger.debug(f'│├ <@{member.id}> PURGED')
                        kicked = True
                        num_kicked += 1
                        break
                    except discord.errors.Forbidden:
                        logger.debug(f'│├ {member.id} UNABLE TO PURGE')
                        kicked = True
                        forbidden += 1
                        break

        await direct_message(bot, f'Purge complete. {num_kicked} purged.', *bot_config.guardians)
    else:
        await message.reply('Unable to comply. You either are attempting to use this in a DM, lack permission, '
                            'or both.')

if __name__ == '__main__':
    bot.run(token=bot_config.token, log_handler=None)
