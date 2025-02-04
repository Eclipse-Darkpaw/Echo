import discord
import json

from discord.ext import commands

from util import read_line, FilePaths

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='set-channels')
    async def channel_setup(self, ctx,
                            application: discord.TextChannel = None,
                            questioning: discord.TextChannel = None,
                            mailbox: discord.TextChannel = None,
                            scam_log: discord.TextChannel = None,
                            warn_log: discord.TextChannel = None):
        """
        Designates important channels
        :param ctx: INteraction
        :param application: Where Membership applications go
        :param questioning: for quesitioning unverified applicants
        :param mailbox:
        :param scam_log: where to log scams
        :param warn_log: where to log warns
        :return:
        """
        with open(FilePaths.servers_settings) as file:
            data = json.load(file)

        server_data = {}

        channels = ['application', 'questioning', 'mailbox', 'log', 'warn log']
        if application is not None:
            server_data['application'] = application.id
        if questioning is not None:
            server_data['questioning'] = questioning.id
        if mailbox is not None:
            server_data['mailbox'] = mailbox.id
        if scam_log is not None:
            server_data['log'] = scam_log.id
        if warn_log is not None:
            server_data['warn_log'] = warn_log.id

        data[str(ctx.guild.id)]['channels'] = server_data
        with open(FilePaths.servers_settings, 'w') as file:
            file.write(json.dumps(data, indent=4))
            await ctx.reply('Channels set.')

    @commands.hybrid_command(name='set-roles')
    async def roles_setup(self, ctx,
                          member: discord.Role = None,
                          questioning: discord.Role = None,
                          unverified: discord.Role = None,
                          suspended: discord.Role = None,
                          mod: discord.Role = None):
        """
        Sets roles the bot uses
        :param ctx: Interaction calling the command
        :param member: Verified member role
        :param questioning: questioning unverified role
        :param unverified: Unverified member role
        :param suspended: Suspended member role
        :param mod: moderator role
        :return:
        """
        with open(FilePaths.servers_settings) as file:
            data = json.load(file)

        server_data = {}

        if member is not None:
            server_data['member'] = member.id
        if questioning is not None:
            server_data['questioning'] = questioning.id
        if unverified is not None:
            server_data['unverified'] = unverified.id
        if suspended is not None:
            server_data['suspended'] = suspended.id
        if mod is not None:
            server_data['mod'] = mod.id

        data[str(ctx.guild.id)]['roles'] = server_data
        with open(FilePaths.servers_settings, 'w') as file:
            file.write(json.dumps(data, indent=4))
            await ctx.reply('Roles set.')

    @commands.hybrid_command(name='set-code')
    async def codeword_setup(self, ctx, codeword):
        with open(FilePaths.servers_settings) as file:
            data = json.load(file)

        data[str(ctx.guild.id)]['codeword'] = codeword
        with open(FilePaths.servers_settings, 'w') as file:
            file.write(json.dumps(data, indent=4))
            await ctx.reply('Code set.')


async def setup(message, client):
    """
    sets up the bot for initial usage
    Last docstring edit: -Autumn V3.0.0
    Last method edit: -Autumn V3.2.0
    :param message: message calling the bot
    :param client: bot client
    :return: None
    """
    progress = await message.channel.send("**__Assignments__**")
    responses = []

    async def update_progress():
        msg = "**__Assignments__**"
        for i in range(len(responses)):
            if str(responses[i][1]).lower() == 'none':
                msg += f'\n**{responses[i][0]}:** {responses[i][1]}'
            elif 0 <= i < 5:
                msg += f'\n**{responses[i][0]}:** <#{responses[i][1]}>'
            elif 5 <= i < 10:
                msg += f'\n**{responses[i][0]}:** <@&{responses[i][1]}>'
            else:
                msg += f'\n**{responses[i][0]}:** {responses[i][1]}'
        await progress.edit(content=msg)

    channels = ['application', 'questioning', 'mailbox', 'log', 'warn log']
    channelIDs = {}
    for channel in channels:
        while True:
            response = await read_line(client,
                                       message.channel,
                                       f'Please tag the {channel} channel, or "None" if it doesnt exist',
                                       target=message.author,
                                       delete_prompt=True,
                                       delete_response=True)
            if response.content.lower() == 'none':

                responses.append((channel, "none"))
                await update_progress()
                break
            try:
                channelIDs[channel] = response.channel_mentions[0].id
                responses.append((channel, response.channel_mentions[0].id))
                await update_progress()
                break
            except IndexError:
                await message.reply('No channels were mentioned')

    roles = ['member', 'unverified', 'questioning', 'suspended', 'mod']
    roleIDs = {}
    for role in roles:
        while True:
            response = await read_line(client,
                                       message.channel,
                                       f'Please tag the {role} role, or "None" if it doesnt exist',
                                       target=message.author,
                                       delete_prompt=True,
                                       delete_response=True)
            if response.content.lower() == 'none':
                responses.append((role, 'none'))
                await update_progress()
                break

            try:
                roleIDs[role] = response.role_mentions[0].id
                responses.append((role, response.role_mentions[0].id))
                await update_progress()
                break
            except IndexError:
                await message.reply('No channels were mentioned')

    codeword = -1
    while codeword == -1:
        response = await read_line(client,
                                   message.channel,
                                   f'What is the server codeword/password? Input "None" if there isnt one',
                                   target=message.author,
                                   delete_prompt=True,
                                   delete_response=True)

        responses.append((channel, response.content))
        await update_progress()
        if response.content.lower() == 'none':
            codeword = None
            break
        else:
            codeword = response.content

    server_data = {"name": message.guild.name,
                   "codeword": codeword,
                   "channels": channelIDs,
                   "roles": roleIDs}



    await message.reply('Setup complete')
