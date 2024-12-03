import discord
import json
# import sunreek
import datetime

from discord.ext import commands

from difflib import SequenceMatcher
from fileManagement import server_settings_path, resource_file_path
from main import read_line
from random import randint


class Team:
    def __init__(self, id: int = 0, name: str = '', points: int = 0):
        self.id = id
        self.name = name
        self.points = points


class Artfight(commands.GroupCog, name="artfight", description="All the commands for the annual artfight"):
    def __init__(self, bot):
        self.bot = bot
        self.team1 = None
        self.team2 = None
        self.team1_score = None
        self.team2_score = None
        self.channel = None

    def timecheck(self, startday: int = 10, endday: int =17) -> bool:
        """
        returns True if between December 10 - 17. Ensures commands are run at the right time
        Last docstring edit: -Autumna1Equin0x.pet V4.1.0
        Last method edit: -Autumna1Equin0x.pet V4.1.0
        :return:
        """
        month = int(datetime.datetime.now().strftime("%m"))
        day = int(datetime.datetime.now().strftime("%d"))

        # Ensure the artfight is going on.
        return month == 12 and startday <= day < endday

    def teamcheck(self, ctx) -> int:
        # return 1 for team 1, 2 for team2 and 0 for no team.
        if ctx.guild.get_role(self.team1) in ctx.author.roles:
            return 1
        elif ctx.guild.get_role(self.team2) in ctx.author.roles:
            return 2
        else:
            return 0

    @commands.hybrid_command(name='load')
    @commands.guild_only()
    async def load(self, ctx):
        """
        Attempts to load data from saved files.
        Last docstring edit: -Autumna1Equin0x.pet V4.1.0
        Last method edit: -Autumna1Equin0x.pet V4.1.0
        :param ctx:
        :return:
        """
        with open(resource_file_path + 'servers.json') as file:
            data = json.load(file)
        try:
            self.team1 = data[str(ctx.guild.id)]['artfight']['roles']['team1']
            self.team2 = data[str(ctx.guild.id)]['artfight']['roles']['team2']
            self.team1_score = data[str(ctx.guild.id)]['artfight']['scores']['team1']
            self.team2_score = data[str(ctx.guild.id)]['artfight']['scores']['team2']
            self.channel = data[str(ctx.guild.id)]['artfight']['channel']
            await ctx.send("Data loaded successfully")
        except KeyError:
            self.team1 = None
            self.team2 = None
            self.team1_score = 0
            self.team2_score = 0
            self.channel = None
            await ctx.send("Error loading data. No data loaded.")

    @commands.hybrid_command(name='setup')
    @commands.guild_only()
    async def setup(self, ctx,
                    team1: discord.Role = None,
                    team2: discord.Role = None,
                    channel: discord.TextChannel = None):
        """
        Sets up the server for Artfight. Overwrites existing save data.
        Last docstring edit: -Autumna1Equin0x.pet V4.1.0
        Last method edit: -Autumna1Equin0x.pet V4.1.0
        :param ctx: The context calling the command
        :param team1: Team 1 role
        :param team2: Team 2 Role
        :param channel: Artfight channel
        :return: None
        """
        progress = None

        async def update_progress(progress=None) -> discord.Message:
            msg = "**__Assignments__**"
            for i in range(len(responses)):
                if str(responses[i][1]).lower() == 'none':
                    msg += f'\n**{responses[i][0]}:** {responses[i][1]}'
                elif 2 <= i < 3:
                    msg += f'\n**{responses[i][0]}:** <#{responses[i][1]}>'
                elif 0 <= i < 2:
                    msg += f'\n**{responses[i][0]}:** <@&{responses[i][1]}>'
                else:
                    msg += f'\n**{responses[i][0]}:** {responses[i][1]}'
            if progress is None:
                progress = await ctx.send(msg)
            else:
                await progress.edit(content=msg)
            return progress

        roleIDs = {}
        responses = []

        if team1 is None:
            while True:
                response = await read_line(self.bot,
                                           ctx.channel,
                                           f'Please tag the team 1 role.',
                                           target=ctx.author,
                                           delete_prompt=True,
                                           delete_response=True)
                try:
                    roleIDs['team1'] = response.role_mentions[0].id
                    responses.append((f'Team 1 Role:', response.role_mentions[0].id))
                    progress = await update_progress(progress)
                    break
                except IndexError:
                    await ctx.reply('No roles were mentioned')
        else:
            team1 = team1.id
        self.team1 = team1
        roleIDs['team1'] = team1

        if team2 is None:
            while True:
                response = await read_line(self.bot,
                                           ctx.channel,
                                           f'Please tag the team 2 role.',
                                           target=ctx.author,
                                           delete_prompt=True,
                                           delete_response=True)
                try:
                    roleIDs['team2'] = response.role_mentions[0].id
                    responses.append((f'Team 2 Role:', response.role_mentions[0].id))
                    progress = await update_progress(progress)
                    break
                except IndexError:
                    await ctx.reply('No roles were mentioned')
        else:
            team2 = team2.id
        self.team2 = team2
        roleIDs['team2'] = team2

        if channel is None:
            while True:
                response = await read_line(self.bot,
                                           ctx.channel,
                                           f'Please tag the artfight channel.',
                                           target=ctx.author,
                                           delete_prompt=True,
                                           delete_response=True)
                try:
                    artfight_channel = response.channel_mentions[0].id
                    responses.append(("channel", response.channel_mentions[0].id))
                    progress = await update_progress(progress)
                    break
                except IndexError:
                    await ctx.reply('No channels were mentioned')
        else:
            channel = channel.id
        self.channel = channel

        artfight_data = {"roles": roleIDs, "channel": channel, "scores": {'team1': 0, 'team2': 0}}

        with open(server_settings_path) as file:
            data = json.load(file)

        data[str(ctx.guild.id)]['artfight'] = artfight_data

        with open(server_settings_path, 'w') as file:
            file.write(json.dumps(data, indent=4))

        await ctx.reply('Data saved')

    @commands.hybrid_command(name='join')
    @commands.guild_only()
    async def join(self, ctx, team: discord.Role = None):
        """
        Joins a user to an Artfight team. assigns randomly if no team is chosen.
        Last docstring edit: -Autumna1Equin0x.pet V4.1.0
        Last method edit: -Autumna1Equin0x.pet V4.1.0
        :param ctx:
        :param team: Team to join
        :return:
        """
        month = int(datetime.datetime.now().strftime("%m"))
        day = int(datetime.datetime.now().strftime("%d"))

        # Ensure the artfight is going on.
        if not self.timecheck():
            # If the time is wrong, stop users from using the command.
            await ctx.send("Artfight is not happening now.")
            return

        # Do not assign a team if a user is already on one
        if self.teamcheck():
            await ctx.send("You are already on a team")
            return

        # Do not assign a team if the roles are not set.
        if self.team1 is None or self.team2 is None:
            await ctx.send('Artfight roles not set. Unable to assign team.')
            return

        # If no team is picked, assign a random one.
        if team is None:
            teams = [self.team1, self.team2]
            team = teams[randint(0, 1)]
        else:
            team = team.id

        # Team role assignment.

        if team == self.team1:
            await ctx.author.add_roles(ctx.guild.get_role(self.team1))
        elif team == self.team2:
            await ctx.author.add_roles(ctx.guild.get_role(self.team2))
        else:
            await ctx.reply(f"I have no idea what team you're trying to join. team <@&{team}> is not valid. Please try "
                            f"again")
            return
        await ctx.reply(f'You have been added to <@&{team}>')

    @commands.hybrid_command(name='submit')
    @commands.guild_only()
    async def submit(self, ctx) -> int:
        """
        Submits an image to artfight
        Last docstring edit: -Autumna1Equin0x.pet V4.1.0
        Last method edit: -Autumna1Equin0x.pet V4.1.0
        :param ctx:
        :return: error code
        """
        team_num = self.teamcheck(ctx)

        # Return if user is not on a team. Users need a team to participate
        if not team_num:
            await ctx.send('You must be on a team to use this command')
            return

        with open(server_settings_path) as file:
            data = json.load(file)

        startday = 11

        self.team1_score = data[str(ctx.guild.id)]['artfight']['scores']['team1']
        self.team2_score = data[str(ctx.guild.id)]['artfight']['scores']['team2']

        dm = await ctx.author.create_dm()
        artfight_day = int(datetime.datetime.now().strftime("%d")) - startday

        if artfight_day <= 0:
            await ctx.send('Artfight has not started yet.')
            return

        await dm.send(f'It is currently Artfight Day {artfight_day}. Please '
                              f'make sure you are following the prompt for today')
        while True:
            responses = []
            try:
                artfight_questions = ['What type of submission is this?\n1:Black&White Sketch\n2:Color Sketch'
                                      '\n3:Black&White Lineart\n4:Full colored\nPlease reply with the corresponding number',
                                      'Please reply with the number of OCs/characters belonging to the other team in your '
                                      'submission',
                                      'Is this shaded? Respond "Y" if yes, anything else for no',
                                      'Is there a background? Respond "Y" if yes, anything else for no',
                                      f'Did you follow the prompt for day '
                                      f'{artfight_day}? Respond "Y" if yes, '
                                      f'anything else for no',
                                      'What is the title of this piece?']
                image = await read_line(self.bot, dm, 'What image are you submitting? Only submit one image.',
                                        ctx.author,
                                        delete_prompt=False, delete_response=False)
                link = image.attachments[0].url

                for question in artfight_questions:
                    question = f'<@!{ctx.author.id}> {question}'
                    response = await read_line(self.bot, dm, question, ctx.author, delete_prompt=False,
                                               delete_response=False)
                    responses.append(response)
            except discord.Forbidden:
                await ctx.reply('Unable to DM You, please change your privacy settings.')
                return -1

            # What type of art is it?
            if responses[0].content[0] == '1':
                base = 5
            elif responses[0].content[0] == '2':
                base = 10
            elif responses[0].content[0] == '3':
                base = 20
            elif responses[0].content[0] == '4':
                base = 30
            else:
                await dm.send(f'Unable to score your submission. \n`Expected int 1-4, was given "{responses[0].content}"`')
                return -2

            # Score how many characters there are in a piece
            try:
                num_chars = int(responses[1].content)
            except ValueError:
                await dm.send(f'Unable to score your submission. \n`Expected int, was given "{responses[1].content}"`')
                return -2

            # is the piece shaded
            if responses[2].content[0].lower() == 'y':
                shaded = 10
            else:
                shaded = 0

            # is there a background
            if responses[3].content[0].lower() == 'y':
                bg = 20
            else:
                bg = 0

            # Did they follow the prompt?
            if responses[4].content[0].lower() == 'y':
                prompt = 1
            else:
                prompt = 0

            # calculate day multiplier
            if artfight_day % 4 == 0:
                day_multiplier = 2
                await dm.send(f'Because today is day {artfight_day}, points are doubled!')
            else:
                day_multiplier = 1

            score = (prompt * ((base + shaded) * num_chars + bg)) * day_multiplier

            embed = discord.Embed(title=responses[5].content, description=f'A Submission from <@{ctx.author.id}>')
            embed.add_field(name='Score', value=str(score)+' ornaments', inline=False)
            embed.set_image(url=link)
            embed.color = ctx.author.color

            await dm.send(embed=embed)
            response = await read_line(self.bot, dm, 'Do you want to submit this? "Y" for yes.', ctx.author,
                                       delete_prompt=False, delete_response=False)

            if response.content.lower() == 'y':

                if team_num == 1:
                    self.team1_score += score
                elif team_num == 2:
                    self.team2_score += score

                data[str(ctx.guild.id)]['artfight']['scores']['team1'] = self.team1_score
                data[str(ctx.guild.id)]['artfight']['scores']['team2'] = self.team2_score

                with open(server_settings_path, 'w') as file:
                    file.write(json.dumps(data, indent=4))
                await dm.send('Score counted!\n'
                              'Sending Submission')
                await ctx.guild.get_channel(self.channel).send(embed=embed)

            else:
                await dm.send('Submission cancelled. Restarting the grading.')

    """@commands.hybrid_command()
    @commands.guild_only()
    async def artfight(self, ctx, message, month, day):
        print(f'{month}-{day}')
        with open(server_settings_path) as file:
            data = json.load(file)
        try:
            artfight_team1_score = data[str(message.guild.id)]['artfight']['scores']['team1']
            artfight_team2_score = data[str(message.guild.id)]['artfight']['scores']['team2']
        except KeyError:
            artfight_team1_score, artfight_team2_score = 0, 0

        try:
            team1 = message.guild.get_role(data[str(message.guild.id)]['artfight']['roles']['team1'])
            team2 = message.guild.get_role(data[str(message.guild.id)]['artfight']['roles']['team2'])
        except KeyError:
            self.team1, self.team2 = None, None
        artfight_channel = None

        command = message.content[1:].split(' ', 3)

        artfight_embed = discord.Embed(title='Artfight Command List',
                                       description='This is the commands for the annual Art Fight',
                                       color=0x45FFFF)
        artfight_embed.add_field(name='join',
                                 value='Assigns a user to a team ',
                                 inline=False)
        artfight_embed.add_field(name='scores',
                                 value='shows the team scores',
                                 inline=False)
        artfight_embed.add_field(name='submit',
                                 value='This is how you submit art. See <#787316128614973491> for scoring.',
                                 inline=False)
        artfight_embed.add_field(name='remove [1/2] [score to remove]',
                                 value='Takes score away from a team (1/2). Use negative numbers to add '
                                       'score.\nMod only.',
                                 inline=False)
        await message.channel.send(embed=artfight_embed)"""

    @commands.hybrid_command(name='score')
    @commands.guild_only()
    async def scores(self, ctx):
        """
        Shows the scores for the teams
        Last docstring edit: -Autumna1Equin0x.pet V4.1.0
        Last method edit: -Autumna1Equin0x.pet V4.1.0
        :param ctx:
        :return:
        """
        if self.timecheck():

        if ctx.author.guild_permissions.manage_roles:
            score_embed = discord.Embed(title='Team scores')
            choice = 0
            if self.team1_score == self.team2_score:
                if randint(0, 1):
                    msg = (f'__Team Scores__\n'
                           f' <@&{self.team1}> - `{self.team1_score}`\n'
                           f' <@&{self.team2}> - `{self.team2_score}`')
                    score_embed.color = ctx.guild.get_role(self.team2).color
                    score_embed.add_field(name=f'{ctx.guild.get_role(self.team1)} Score', value=str(self.team1_score))
                    score_embed.add_field(name=f'{ctx.guild.get_role(self.team2)} Score', value=str(self.team2_score))
                else:
                    msg = (f'__Team Scores__\n'
                           f' <@&{self.team2}> - `{self.team2_score}`\n'
                           f' <@&{self.team1}> - `{self.team1_score}`')
                    score_embed.color = ctx.guild.get_role(self.team1).color
                    score_embed.add_field(name=f'{ctx.guild.get_role(self.team2)} Score', value=str(self.team2_score))
                    score_embed.add_field(name=f'{ctx.guild.get_role(self.team1)} Score', value=str(self.team1_score))
                score_embed.set_footer(text='Points are tied!')
            elif self.team1_score > self.team2_score:
                msg = (f'__Team Scores__\n'
                       f'1. <@&{self.team1}> - `{self.team1_score}`\n'
                       f'2. <@&{self.team2}> - `{self.team2_score}`')
                score_embed.color = ctx.guild.get_role(self.team1).color
                score_embed.add_field(name=f'{ctx.guild.get_role(self.team1)} Score', value=str(self.team1_score))
                score_embed.add_field(name=f'{ctx.guild.get_role(self.team2)} Score', value=str(self.team2_score))
                score_embed.set_footer(text=f'{ctx.guild.get_role(self.team1)} is '
                                            f'{ self.team1_score - self.team2_score} points ahead!')
            elif self.team1_score < self.team2_score:
                msg = (f'__Team Scores__\n'
                       f'1. <@&{self.team2}> - `{self.team2_score}`\n'
                       f'2. <@&{self.team1}> - `{self.team1_score}`')
                score_embed.color = ctx.guild.get_role(self.team2).color
                score_embed.add_field(name=f'{ctx.guild.get_role(self.team2)} Score', value=str(self.team2_score))
                score_embed.add_field(name=f'{ctx.guild.get_role(self.team1)} Score', value=str(self.team1_score))
                score_embed.set_footer(text=f'{ctx.guild.get_role(self.team2)} is '
                                            f'{ self.team2_score - self.team1_score} points ahead!')

        await ctx.reply(content=msg, embed=score_embed)
        return



    @commands.hybrid_command(name='remove')
    @commands.guild_only()
    async def remove(self, ctx, team, score):
        """
        Takes score away from a team (1/2). Use negative numbers to add score. Mod only.
        Last docstring edit: -Autumna1Equin0x.pet V4.1.0
        Last method edit: -Autumna1Equin0x.pet V4.1.0
        :param ctx: Context
        :param team: Team to remove points from
        :param score: Score to remove
        :return:
        """
        if ctx.author.guild_permissions.manage_roles:
            with open(server_settings_path) as file:
                data = json.load(file)

            if team == '1':
                data[str(ctx.guild.id)]['artfight']['scores']['team1'] -= int(score)
                await ctx.reply(f'{score} ornaments removed from {self.team1.name}')
            elif team == '2':
                data[str(ctx.guild.id)]['artfight']['scores']['team2'] -= int(score)
                await ctx.reply(f'{score} ornaments removed from {self.team2.name}')

            with open(server_settings_path, 'w') as file:
                file.write(json.dumps(data, indent=4))
            await ctx.reply('Data saved')
        else:
            await ctx.reply('Invalid argument')
