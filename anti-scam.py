import discord

version = '1.1.0'

log_channel = 933539437357432892     #channel ID of the channel where logs go
token = 'OTMzNTQwOTg1NjY3OTkzNjcx.YejByw.dISKG7JJOBC2L3BAIPmqEpHHJMQ'          # put the bot token in the quotes

game = discord.Game('Scanning for pings')
client = discord.Client()


@client.event
async def on_message(message):
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        if message.author.guild_permissions.mention_everyone:
            pass
        else:
            await message.delete()
            content = message.content.replace('@', '@ ')

            channel = message.guild.get_channel(log_channel)

            embed = discord.Embed(title='Attempted ping in <#' + str(message.channel.id) + '>')
            embed.set_author(name='<@' + str(message.author.id) + '>', icon_url=message.author.avatar_url)
            embed.add_field(name=message, value=content)
            await channel.send(embed=embed)
    else:
        pass


client.run(token)
