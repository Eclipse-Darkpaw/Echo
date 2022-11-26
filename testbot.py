import discord
import os
import sys


intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


prefix = '>'

async def quit(interaction):
    await interaction.response.send_message("Goodbye")
    sys.exit()
    

async def first_command(message):
    await message.reply("Hello!")


async def react(message):
    await message.reply('Very cool message!')


@client.event
async def on_ready():
    print("All systems are go. Proceed with testing.")



switcher = {'first': first_command, 'react': react}


@client.event
async def on_mesage(message):
    if message.author.bot:
        return
    if message.content[0] == prefix:
        command = message.content.split()
        try:
            switcher[command[1]](message)
        except KeyError:
            pass


def run_test():
    client.run(os.environ.get('TESTBOT_TOKEN'))
    

if __name__ == "__main__":
    run_test()