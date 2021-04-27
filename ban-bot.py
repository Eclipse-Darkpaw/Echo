import discord

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_member_join(member):
    await member.ban('Breaking rule 1')
    await member.send('You have been banned for breaking rule 1.\n'
                      '>  Do not join the server. This will result in an instant ban')

client.run('ODM0MTY4OTYwMjI4MjYxOTQx.YH8-Yg.yRIQMLqttJ_7cJ2xuDdm_za7Pjw')