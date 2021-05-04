import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    await message.author.ban()

@client.event
async def on_member_join(member):
    await member.ban()

client.run('ODM0MTY4OTYwMjI4MjYxOTQx.YH8-Yg.yRIQMLqttJ_7cJ2xuDdm_za7Pjw')