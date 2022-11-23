import discord
import os
import sys

from discord import app_commands


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="quit", description="quits the bot", guild=discord.Object(id=791392423704133653))
async def quit(interaction):
    await interaction.response.send_message("Goodbye")
    sys.exit()
    


@tree.command(name="commandname", description="My first application Command", guild=discord.Object(id=791392423704133653))
async def first_command(interaction):
    await interaction.response.send_message("Hello!")


@app_commands.context_menu()
async def react(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message('Very cool message!', ephemeral=True)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=791392423704133653))

client.run(os.environ.get('TESTBOT_TOKEN'))