import discord
import json
import modules.AntiScam as AntiScam
import modules.General as General
import modules.Moderation as Mod
import modules.ServerSettings as Settings
import modules.Verification as Verif
import modules.refManagement as Ref
import random
import os
import sys
import time

from discord.ext import commands
from fileManagement import server_settings_path
from main import eclipse_id

# Keep imports in alphabetical order

start_time = time.time()

prefix = '>'
version_num = '4.0.0'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

game = discord.Game(f'{prefix}help for commands')
client = bot


@bot.hybrid_command()
async def uptime(ctx: discord.Interaction):
    """
    Displays the time the bot has been running for.
    Last docstring edit: -Autumn V3.3.4
    Last method edit: -Autumn V4.0.0
    :param message: message calling the bot
    :return: None
    """
    days = int(time.strftime('%j', time.gmtime(time.time() - start_time)))
    await ctx.send(time.strftime(f'Online for {days - 1} days %H:%M:%S\n Started <t:{int(start_time)}:R>',
                                      time.gmtime(time.time() - start_time)))




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
    Last method edit: -Autumn V4.0.0
    :return: None
    """

    print('We have logged in as {0.user}'.format(client))

    await client.change_presence(activity=game)
    await client.get_user(eclipse_id).send('Running, and active')

    print('loading cogs')
    await bot.add_cog(Mod.Moderation(bot))
    await bot.add_cog(General.General(bot))
    await bot.add_cog(Settings.Settings(bot))
    await bot.add_cog(Ref.RefManagement(bot))
    await bot.add_cog(Verif.Verification(bot))
    print('Cogs loaded')


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
