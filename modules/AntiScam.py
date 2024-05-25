"""
Anti-scam module.

This code is designed to protect servers from users who attempt to scam an entire server at the same time.
"""
import discord
import json

from fileManagement import resource_file_path, scam_log_path

version = "1.17.0"

# list of legitimate messages, that commonly get flagged. These should be ignored.
whitelist = ['https://discord.gift/',  # legitimate nitro gifting
             # common domains that get flagged falsely
             'https://tenor.com', 'https://store.steampowered.com/app/', 'https://twitter.com',
             # not common, but aren't scams
             'https://www.nzwe.com/', 'https://tinyurl.com/3vznrzkr', 'https://youtu.be/dQw4w9WgXcQ']

# these are potential scams. It's probably a false positive if only 2 are hit, but a true positive if 3 are hit.
blacklist = ['@everyone', '@here',  # attempting to ping the server
             'https://', 'gift', 'nitro', 'steam', 'free', 'https://discord.gg'
             # miscellaneous messages included in real scam messages
                                                           'who is first? :)', "who's first? :)", 'teen porn',
             # crypto related terms
             'airdrop', 'crypto', 'nft', 'dm me via', ' btc', 'btc ', '/btc/', '\\btc\\', ' eth', 'eth ', '/eth/',
             '\\eth\\', 'bitcoin', 'etherium',
             # intentional misspellings
             'dlsscord', 'dlscord', 'glfts', 'disords', 'stean'
             # random character strings found in scam links
                                                        'yn2gdpaajhagd3km26rfgvtp', '4uowwt7enombq0b', 'bferdhabecvcw',
             'x0kd211hpmjf',
             # NSFW ADVERTISEMENTS
             'Best nsfw content', 'onlyfans leaks']

# these immediately are flagged and removed. These are part of confirmed scams and should be handled immediately.
banlist = ['discorx.gift', 'disords.gift', 'dlsscord-gift.com/', 'discordnitro.fun', 'disordgifts.com',
           'dlscord-app.info', 'dlscord.co.uk', 'discordgg.ga', 'discordn.gift', 'discord-niltro.com', 'vlootgift.site',
           'ethlegit.com', 't.me/davidmurray', 'discorgs.icu/login/nitro', 'steancomiunitly.com/glfts',
           'discerdapp.com', 'discorgs.icu'
           # server invites
                             "https://discord.gg/anastasyxxx", "https://discord.gg/t9eKqS8gnG",
           "https://discord.gg/sexybabe", "https://discord.gg/sexgirls",
           "https://discord.gg/xxxpornx",
           # confirmed scam messages and fragments
           '@everyone who will catch this gift?)', 'join the best 18+ server with only free stuff',
           "best nsfw content + give away nitro", "onlyfans leaks here", 'gifts for the new year, nitro for 1 month',
           # miscellaneous
           'discord free nitro from steam', 'wow join and check it! @everyone',
           "take nitro faster, it's already running out", "yo i accidentally got 2 nitros and dont need the other one",
           # spam links
           "temu.com",
           # ZWSP
           '​',
           # Standard EICARS test string
           'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*']
code = 'plsdontban'

counter = 0


async def scan_message(message):
    global counter
    """
    The primary anti-scam method. This method is given a message, counts the number of flags in a given message, then
    does nothing if no flags, flags the message as a possible scam if 1-3, or flags and deletes the message at 3+ flags.
    Last docstring edit: -Autumn V1.14.4
    Last method edit: -Autumn V1.14.5
    :param message: the message sent
    :return: None
    """
    with open(resource_file_path + 'servers.json') as file:
        try:
            log_channel = json.load(file)[str(message.guild.id)]['channels']['log']
        except KeyError:
            if counter % 50 == 0:
                await message.channel.send("Anti-scam scanning is currently offline.")
            counter += 1
            return
    words = []
    flags = 0
    bans = 0
    content = message.content.lower()
    
    # scan the banned word list first. if any appear, delete immediately.
    for word in banlist:
        index = content.find(word)
        if index != -1:
            bans += 1
            if word == '​':
                words.append('Zero Width Space')
            else:
                words.append(word)
    
    # scan the plain blacklist next, count the number of blacklisted words
    for word in blacklist:
        index = content.find(word)
        if index != -1:
            flags += 1
            words.append(word)
    
    # if a word in the white list appears, remove a flag.
    for word in whitelist:
        index = content.find(word)
        if index != -1:
            flags -= 1
    
    if flags < 2 and bans == 0:
        return  # skips messages with less than 2 flags and no bans
    else:
        if flags >= 3 or bans > 0:
            await message.delete()
            await message.channel.send('Your message has been deleted. If this was an error, please send the code '
                                       '`plsdontban` somewhere in your message to get around our filters.')
        
        content = message.content.replace('@', '@ ')
        
        channel = message.guild.get_channel(log_channel)
        
        embed = discord.Embed(title='Possible Scam in #' + str(message.channel.name), color=0xFF0000)
        embed.set_author(name='@' + str(message.author.name), icon_url=message.author.avatar.url)
        embed.add_field(name='message', value=content, inline=False)
        embed.add_field(name='Flags', value=str(flags))
        embed.add_field(name='Banned Strings', value=str(bans))
        embed.add_field(name='Words Flagged', value=words, inline=False)
        embed.add_field(name='Sender ID', value=message.author.id)
        embed.add_field(name='Channel ID', value=message.channel.id)
        embed.add_field(name='Message ID', value=message.id)
        lst = str(words)
        lst.replace('​','Zero Width Space Character')
        if flags < 3 and bans == 0:
            embed.add_field(name='URL', value=message.jump_url, inline=False)
        await channel.send(embed=embed)
        with open(scam_log_path(), 'a') as log:
            # Message ID,Datetime,Guild,Sender ID,Channel ID,Flags,Banned strs
            log.write(f'{message.id},{message.created_at},{message.guild.id},{message.author.id},'
                      f'{message.channel.id},{flags},{bans},{lst.replace(","," - ")},"{message.content}\n"')
