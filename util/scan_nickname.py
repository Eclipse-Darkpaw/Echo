import discord

substrings = ['#']

async def scan_nickname(
        usr: discord.Member,
        log_channel_id: int,
        forbidden_names: str,
        replacement='changeme'
    ):
    """
    Scans a users nickname for restricted characters and strings. If restricted strings are found, we can either remove
    the name, Set it to a designated string, or kick the user entirely
    Last docstring edit: -Autumnn V4.2.0
    Last method edit: -Autumn V4.2.0
    :param: Discord Member who changed username or joined the server.
    :return: None
    """
    channel = usr.guild.get_channel(log_channel_id)

    if usr.nick in forbidden_names:
        oldname = usr.nick
        changed =False
        try:
            await usr.edit(nick=replacement)
            changed = True
        except discord.Forbidden:
            await channel.send(f"Unable to change <@{usr.id}>'s name.")

        try:
            dm = await usr.create_dm()
            if changed:
                await dm.send(f'Your nickname in the server has been changed to `{replacement}` for being `{oldname}`')
            else:
                await dm.send('You have changed your name to a banned string. Please change your name back. This '
                                  'incident has been logged.')
        except discord.Forbidden:
            await channel.send('Unable to notify user')
        await channel.send(f'<@{usr.id}> (`{usr.id}`) attempted to change their name to `{oldname}`')
        return

    for string in substrings:
        if string in usr.nick:
            changed = False
            try:
                await usr.edit(nick=replacement)
                changed = True
            except discord.Forbidden:
                await channel.send(f"Unable to change <@{usr.id}>'s name.")

            try:
                dm = await usr.create_dm()
                if changed:
                    await dm.send(f'Your nickname in the server has been changed to `{replacement}` for containing `{string}`.')
                else:
                    await dm.send('You have changed your name to a banned string. Please change your name back. This '
                                  'incident has been logged.')
            except discord.Forbidden:
                await channel.send('Unable to notify user')
            await channel.send(f'<@{usr.id}> (`{usr.id}`) attempted to change their name to `{usr.nick}`')