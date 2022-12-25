import discord
import json

from fileManagement import resource_file_path

blacklist = ['@everyone', 'https://', 'gift', 'nitro', 'steam', '@here', 'free', 'who is first? :)', "who's first? :)",
             'btc', 'eth', 'airdrop', 'crypto', 'nft', 'dm me via', 't.me/DavidMurray']
code = 'plsdontban'


async def scan_message(message):
    """
    The primary anti-scam method. This method is given a message, counts the number of flags in a given message, then
    does nothing if no flags, flags the message as a possible scam if 1-3, or flags and deletes the message at 3+ flags.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.14.5
    :param message: the message sent
    :return: None
    """
    with open(resource_file_path + 'servers.json') as file:
        log_channel = json.load(file)[str(message.guild.id)]['channels']['log']

    flags = 0
    content = message.content.lower()
    
    for word in blacklist:
        index = content.find(word)
        if index != -1:
            flags += 1

    if flags < 2:
        return
    else:
        if flags >= 3:
            await message.delete()

        content = message.content.replace('@', '@ ')

        channel = message.guild.get_channel(log_channel)

        embed = discord.Embed(title='Possible Scam in #' + str(message.channel.name), color=0xFF0000)
        embed.set_author(name='@' + str(message.author.name), icon_url=message.author.avatar.url)
        embed.add_field(name='message', value=content, inline=False)
        embed.add_field(name='Flags', value=str(flags), inline=False)
        embed.add_field(name='Sender ID', value=message.author.id)
        embed.add_field(name='Channel ID', value=message.channel.id)
        embed.add_field(name='Message ID', value=message.id)

        if flags < 3:
            embed.add_field(name='URL', value=message.jump_url, inline=False)
        await channel.send(embed=embed)