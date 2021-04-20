import discord
import os
import sys
from dotenv import load_dotenv
load_dotenv()

game = discord.Game('down for maintainence')
client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == '>quit':
        sys.exit()
    if message.content.startswith('>'):
        await message.channel.send('Echo is currently offline for repairs')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(status=discord.Status.idle, activity=game)

print('Starting Bot')
client.run(os.getenv('TOKEN'))