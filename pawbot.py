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
async def version(ctx: discord.Interaction):
    """
    Displays the version of the bot being used
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V4.0.0
    :param message: Message calling the bot
    :return: None
    """
    await ctx.channel.send(f'I am currently running version {version_num}')


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


@client.event
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


def run_pawbot():
    """
    Function allows the host to pick whether to run the live bot, or run the test bot in a closed environment, without
    switching programs. This allows the live code to run parallel to the testing code and prevent constant restarts to
    test new features.
    Last docstring edit: -Autumn V1.16.3
    Last function edit: Unknown
    :return: None
    """
    global prefix

    if len(sys.argv) > 1:
        inp = int(sys.argv[1])
    else:
        inp = int(input('input token num\n'
                        '1. Pawbot\n'
                        '2. Testing Environment\n'))

    if inp == 1:
        # Main bot client. Do not use for tests

        client.run(os.environ.get('PAWBOT_TOKEN'))  # must say client.run(os.environ.get('SUNREEK_TOKEN'))

    elif inp == 2:
        # Test Bot client. Allows for tests to be run in a secure environment.

        client.run(os.environ.get('TESTBOT_TOKEN'))  # must say client.run(os.environ.get('TESTBOT_TOKEN')
    elif inp == 3:
        client.run(os.environ.get('PAWBOT_TEST'))


if __name__ == '__main__':
    run_pawbot()
