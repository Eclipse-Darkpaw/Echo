import discord
import datetime
import json

from modules.artfight_ui import (
    artfight_configuration_message,
    ConfigurationView   
)
from base_bot import EchoBot
from config import MAX_DISCORD_MESSAGE_LEN
from discord import app_commands
from discord.ext import commands
from random import randint
from repositories import ArtfightRepo
from util import (
    FilePaths,
    read_line
)

class Artfight(commands.GroupCog, name='artfight', description='All the commands for the annual artfight'):
    artfight_role = 1317026586226331678

    def __init__(self, bot: EchoBot):
        self.bot = bot
        self.artfight_repo = ArtfightRepo()

        self.bot.logger.info(f'✔ Artfight cog loaded')

    @commands.hybrid_command(name='configuration')
    @commands.guild_only()
    async def configuration(self, ctx: commands.Context):
        """
        Configure the artfight settings. At runtime alterations are possible, caution is advised!
        Note: These changes will persist immediately, if you wish to archive the current configuration before overwriting, use /artfight archive
        Last docstring edit: -FoxyHunter V4.3.0
        Last method edit: -FoxyHunter V4.3.0
        :param ctx: The context calling the command
        :return: None
        """
        view = ConfigurationView(self.bot, self.artfight_repo, ctx.guild.id)
        message = await ctx.reply(content='Loading configuration...')
        await message.edit(content=artfight_configuration_message(self.artfight_repo, ctx.guild.id), view=view)
        view.message = message

    @commands.hybrid_command(name='join')
    @commands.guild_only()
    async def join(self, ctx, team: discord.Role = None):
        """
        Joins a user to an Artfight team. assigns randomly if no team is chosen.
        Last docstring edit: -Autumna1Equin0x.pet V4.1.0
        Last method edit: -FoxyHunter V4.3.0
        :param ctx:
        :param team: Team to join
        :return:
        """
        team1 = self.artfight_repo.get_team_role(ctx.guild_id, 'team1')
        team2 = self.bot.repositories['artfight_repo'].get_team_role(ctx.guild_id, 'team2')

        # Ensure the artfight is going on.
        if not self.timecheck(startday=7):
            # If the time is wrong, stop users from using the command.
            await ctx.send("Artfight is not happening now.")
            return

        # Do not assign a team if a user is already on one
        if self.teamcheck(ctx):
            await ctx.send("You are already on a team")
            return

        # Do not assign a team if the roles are not set.
        if team1 is None or team2 is None:
            await ctx.send('Artfight roles not set. Unable to assign team.')
            return

        # If no team is picked, pick for the user. Pick the smaller team to keep teams balanced. otherwise do random
        team1size = len(ctx.guild.get_role(team1).members)
        team2size = len(ctx.guild.get_role(team2).members)
        if team is None and team1size > team2size:
            team = team2
        elif team is None and team2size > team1size:
            team = team1
        elif team is None and team1size == team2size:
            teams = [team1, team2]
            team = teams[randint(0, 1)]
        else:
            team = team.id

        # Team role assignment.

        if team == team1:
            await ctx.author.add_roles(ctx.guild.get_role(team1))
        elif team == team2:
            await ctx.author.add_roles(ctx.guild.get_role(team2))
        else:
            await ctx.reply(f"I have no idea what team you're trying to join. team <@&{team}> is not valid. Please try "
                            f"again")
            return

        with open(FilePaths.artfight_members) as file:
            data = json.load(file)

        try:
            data[str(ctx.guild.id)][ctx.author.id] = {'team': team, 'points': 0}
            self.bot.logger.debug('Saved 1')
        except KeyError:
            data[str(ctx.guild.id)] = {}
            data[str(ctx.guild.id)][ctx.author.id] = {'team': team, 'points': 0}
            self.bot.logger.debug('Saved 2')

        with open(FilePaths.artfight_members, 'w') as file:
            file.write(json.dumps(data, indent=4))

        await ctx.reply(f'You have been added to <@&{team}>')

    @commands.hybrid_command()
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
            await ctx.send('You must be on a team to use this command. <@749443249302929479>')
            return
        else:
            await ctx.send('Please check your dms to continue with your submission')

        with open(FilePaths.servers_settings, 'r') as file:
            data = json.load(file)

        startday = 12

        team1_score = data[str(ctx.guild.id)]['artfight']['scores']['team1']
        team2_score = data[str(ctx.guild.id)]['artfight']['scores']['team2']

        dm = await ctx.author.create_dm()
        artfight_day = int(datetime.datetime.now().strftime("%d")) - startday

        if artfight_day <= 0:
            await ctx.send('Artfight has not started yet.')
            return

        await dm.send(f'It is currently Artfight Day {artfight_day}. Please '
                      f'make sure you are following the prompt for today')
        responses = []
        artfight_questions = ['What type of submission is this?\n1:Black&White Sketch/Black and White Rough Sketch\n2:Color Sketch/Color Rough Sketch'
                              '\n3:Black&White Lineart\n4:Full colored\nPlease reply with the corresponding number',
                              'Please reply with the number of OCs/characters belonging to the **__other team__** in '
                              'your submission',
                              'Is this shaded? Respond "Y" if yes, anything else for no',
                              'Is there a background? Respond "Y" if yes, anything else for no',
                              f'Did you follow the prompt for day '
                              f'{artfight_day}? Respond "Y" if yes, '
                              f'anything else for no',
                              'What is the title of this piece?']
        # TODO: add a question about friendly fire OCS
        while True:
            try:
                image = await read_line(self.bot, dm, 'What image are you submitting? Only submit one image.',
                                        ctx.author,
                                        delete_prompt=False, delete_response=False)
                link = image.attachments[0].url
            except IndexError:
                await dm.send('No image attached. Please restart')
                return -1
            except discord.Forbidden:
                await ctx.reply('Unable to DM You, please change your privacy settings.')
                return -1

            for question in artfight_questions:
                question = f'<@!{ctx.author.id}> {question}'
                response = await read_line(self.bot, dm, question, ctx.author, delete_prompt=False,
                                           delete_response=False)
                responses.append(response)

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
                await dm.send(f'Unable to score your submission. Please try again. \n`Expected int 1-4, was given '
                              f'"{responses[0].content}"`')
                return -1

            # Score how many characters there are in a piece
            try:
                num_chars = int(responses[1].content)
            except ValueError:
                await dm.send(f'Unable to score your submission. Please try again. \n`Expected int, was given '
                              f'"{responses[1].content}"`')
                return -1

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
            response = await read_line(self.bot,
                                       dm,
                                       'Do you want to submit this?\n'
                                       '"Y" for yes, "C" to cancel, anything else to restart.',
                                       ctx.author,
                                       delete_prompt=False, delete_response=False)

            if response.content.lower() == 'y':
                if team_num == 1:
                    team1_score += score
                elif team_num == 2:
                    team2_score += score
            elif response.content.lower() == 'c':
                await dm.send('Submission cancelled.')
                return -1
            else:
                await dm.send('Submission not approved. Restarting')
                continue

            data[str(ctx.guild.id)]['artfight']['scores']['team1'] = team1_score
            data[str(ctx.guild.id)]['artfight']['scores']['team2'] = team2_score

            with open(FilePaths.servers_settings, 'w') as file:
                file.write(json.dumps(data, indent=4))

            with open(FilePaths.artfight_members) as file:
                data = json.load(file)

            # Save the score to the user data file for tracking and validation
            try:
                data[str(ctx.guild.id)][str(ctx.author.id)]['points'] += score
            except KeyError:
                try:
                    data[str(ctx.guild.id)][str(ctx.author.id)] = {}
                    data[str(ctx.guild.id)][str(ctx.author.id)]['points'] += score
                except KeyError:
                    await dm.send('Tell Autumn youre not on the list and something is seriously wrong. '
                                  'Also give them your points so they can put you on the list properly.')



            with open(FilePaths.servers_settings, 'w') as file:
                file.write(json.dumps(data, indent=4))

            await dm.send('Score counted!\n'
                          'Sending Submission')
            await ctx.guild.get_channel(self.channel).send(embed=embed)
            return

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
            pass

        try:
            self.team1 = self.bot.repositories['artfight_repo'].get_team_role(ctx.guild.id, 'team1')
            self.team2 = self.bot.repositories['artfight_repo'].get_team_role(ctx.guild.id, 'team1')
            self.team1_score = self.bot.repositories['artfight_repo'].get_team_score(ctx.guild.id, 'team1')
            self.team2_score = self.bot.repositories['artfight_repo'].get_team_score(ctx.guild.id, 'team2')
        except KeyError:
            team1 = None
            team2 = None
            team1_score = 0
            team2_score = 0

        if ctx.author.guild_permissions.manage_roles:
            score_embed = discord.Embed(title='Team scores')
            if team1_score == team2_score:
                if randint(0, 1):
                    msg = (f'__Team Scores__\n'
                           f' <@&{team1}> - `{team1_score}`\n'
                           f' <@&{team2}> - `{team2_score}`')
                    score_embed.color = ctx.guild.get_role(team2).color
                    score_embed.add_field(name=f'{ctx.guild.get_role(team1)} Score', value=str(team1_score))
                    score_embed.add_field(name=f'{ctx.guild.get_role(team2)} Score', value=str(team2_score))
                else:
                    msg = (f'__Team Scores__\n'
                           f' <@&{team2}> - `{team2_score}`\n'
                           f' <@&{team1}> - `{team1_score}`')
                    score_embed.color = ctx.guild.get_role(team1).color
                    score_embed.add_field(name=f'{ctx.guild.get_role(team2)} Score', value=str(team2_score))
                    score_embed.add_field(name=f'{ctx.guild.get_role(team1)} Score', value=str(team1_score))
                score_embed.set_footer(text='Points are tied!')
            elif team1_score > team2_score:
                msg = (f'__Team Scores__\n'
                       f'1. <@&{team1}> - `{team1_score}`\n'
                       f'2. <@&{team2}> - `{team2_score}`')
                score_embed.color = ctx.guild.get_role(team1).color
                score_embed.add_field(name=f'{ctx.guild.get_role(team1)} Score', value=str(team1_score))
                score_embed.add_field(name=f'{ctx.guild.get_role(team2)} Score', value=str(team2_score))
                score_embed.set_footer(text=f'{ctx.guild.get_role(team1)} is '
                                            f'{team1_score - team2_score} points ahead!')
            elif team1_score < team2_score:
                msg = (f'__Team Scores__\n'
                       f'1. <@&{team2}> - `{team2_score}`\n'
                       f'2. <@&{team1}> - `{team1_score}`')
                score_embed.color = ctx.guild.get_role(team2).color
                score_embed.add_field(name=f'{ctx.guild.get_role(team2)} Score', value=str(team2_score))
                score_embed.add_field(name=f'{ctx.guild.get_role(team1)} Score', value=str(team1_score))
                score_embed.set_footer(text=f'{ctx.guild.get_role(team2)} is '
                                            f'{team2_score - team1_score} points ahead!')

        await ctx.reply(content=msg, embed=score_embed)
        return

    @commands.hybrid_command(name='remove')
    @commands.guild_only()
    async def remove(self, ctx, team: discord.Role, score: int):
        """
        Takes score away from a team (1/2). Use negative numbers to add score. Mod only.
        Last docstring edit: -Autumna1Equin0x.pet V4.1.0
        Last method edit: -Autumna1Equin0x.pet V4.1.0
        :param ctx: Context
        :param team: Team to remove points from
        :param score: Score to remove
        :return:
        """
        # Do not take points if the roles are not set.
        try:
            self.team1 = self.bot.repositories['artfight_repo'].get_team_role(ctx.guild.id, 'team1')
            self.team2 = self.bot.repositories['artfight_repo'].get_team_role(ctx.guild.id, 'team1')
        except KeyError:
            team1 = None
            team2 = None
        
        if team1 is None or team2 is None:
            await ctx.send('Artfight roles not set. Unable to assign team.')
            return

        # Discord passes the full role object. We only need the ID for this to work.
        name = team.name
        team = team.id

        if ctx.author.guild_permissions.manage_roles:
            with open(FilePaths.servers_settings, 'r') as file:
                data = json.load(file)

            if team == team1:
                data[str(ctx.guild.id)]['artfight']['scores']['team1'] -= int(score)
            elif team == team2:
                data[str(ctx.guild.id)]['artfight']['scores']['team2'] -= int(score)
            else:
                await ctx.send(f"I have no idea what team you're trying to remove points from. team <@&{team}> is not "
                               f"valid. Please try again")
                return

            with open(FilePaths.servers_settings, 'w') as file:
                file.write(json.dumps(data, indent=4))
            await ctx.send(f'{score} ornaments removed from {name}. Data saved.')
        else:
            await ctx.send('Invalid argument')

    @commands.hybrid_command(name='players')
    @commands.guild_only()
    async def players(self, ctx: commands.Context):
        """
        Lists all the players, what team theyre on, and points contributed
        :param ctx:
        :return:
        """
        await ctx.send('This command currently doesn\'t work, apolagies')

        if ctx.message.author.guild_permissions.manage_roles:
            message = ''
            teams = self.bot.repositories['artfight_repo'].get_teams(ctx.guild.id)

            for team_name, role_id in teams.items():
                team_members = self.bot.repositories['artfight_repo'].get_team_members(ctx.guild.id, team_name)
                team_info_txt = f'## {team_name}\n- **Role:** <@&{role_id}>\n- **Members:** {len(team_members)}\n ### Members\n'

                if len(f'{message}{team_info_txt}') > MAX_DISCORD_MESSAGE_LEN:
                    await ctx.send(message)
                    message = team_info_txt
                else:
                    message += team_info_txt

                for member_id_str, member_data in team_members:
                    member_info_txt = f'<@{member_id_str}> - points: {member_data['points']}, submissions: {len(member_data['submissions'])}\n'

                    if len(f'{message}{member_info_txt}') > MAX_DISCORD_MESSAGE_LEN:
                        await ctx.send(message)
                        message = member_info_txt
                    else:
                        message += member_info_txt

            await ctx.send(message)
        else:
            await ctx.send('You do not have permission to use this.')

    @commands.hybrid_command(name="removemember")
    @commands.guild_only()
    async def remove_member(self, ctx, member: discord.Member):
        """
        Yeetus Deletus a member from artfight (purged from the botlist & gone with their roles)
        :param ctx: The command context.
        :param member: The Discord member to remove (mention or user object).
        """
        try:
            with open(FilePaths.artfight_members, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            await ctx.send("The data file is missing or corrupted!")
            return

        guild_data = data.get(str(ctx.guild.id))
        if not guild_data or str(member.id) not in guild_data:
            await ctx.send(f"User {member.mention} not found in the specified guild!")
            return

        user_profile = guild_data[str(member.id)]
        self.bot.logger.info(f'user removed: {user_profile}')

        # Confirmation embed
        embed = discord.Embed(title="Confirm User Removal", color=discord.Color.orange())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(
            name="Team",
            value=(ctx.guild.get_role(int(user_profile["team"])).mention if ctx.guild.get_role(int(user_profile["team"])) else "Unknown"),
            inline=True
        )

        embed.add_field(name="Points", value=str(user_profile["points"]), inline=True)
        embed.set_footer(text="Choose an action below")

        # very ahem (not) clean, inline class, because yes
        class InlineButtons(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.result = None

            @discord.ui.button(label="Purge", style=discord.ButtonStyle.danger)
            async def purge(self, interaction: discord.Interaction, button: discord.ui.Button):
                try:
                    # Remove the user from the file
                    del data[str(ctx.guild.id)][str(member.id)]

                    # Remove the guild if it is empty
                    if not data[str(ctx.guild.id)]:
                        del data[str(ctx.guild.id)]

                    # Save the updated data
                    with open(FilePaths.artfight_members, "w") as file:
                        json.dump(data, file, indent=4)

                    await interaction.response.send_message(f"Member {member.mention} has been removed.", ephemeral=False)

                    # Remove roles from member
                    team_role = ctx.guild.get_role(int(user_profile["team"]))
                    artfight_role = ctx.guild.get_role(Artfight.artfight_role)

                    try:
                        # Remove the team role from the member
                        await member.remove_roles(team_role)
                    except discord.Forbidden:
                        await interaction.followup.send(f"I don't have the permissions to remove: {team_role.mention}", ephemeral=False)
                    except discord.HTTPException:
                        await interaction.followup.send(f"Something when wrong when trying to remove: {team_role.mention}", ephemeral=False)

                    try:
                        # Remove the artfight role from the member
                        await member.remove_roles(artfight_role)
                    except discord.Forbidden:
                        await interaction.followup.send(f"I don't have the permissions to remove: {artfight_role.mention}", ephemeral=False)
                    except discord.HTTPException:
                        await interaction.followup.send(f"Something when wrong when trying to remove: {artfight_role.mention}", ephemeral=False)

                    await interaction.followup.send(f"Roles: {team_role.mention} & {artfight_role.mention} removed from member: {member.mention}")
                    self.result = "purge"
                except KeyError:
                    await interaction.response.send_message("Member not found in the file!", ephemeral=False)
                    self.result = "error"
                self.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_message("Action canceled.", ephemeral=False)
                self.result = "cancel"
                self.stop()

        # Send the embed with buttons
        view = InlineButtons()
        await ctx.send(embed=embed, view=view)
        await view.wait()

        if view.result == "purge":
            self.bot.logger.info(f"Member {member.id} removed from guild {ctx.guild.id}.")
        elif view.result == "cancel":
            self.bot.logger.info(f"Member {member.id} removal canceled.")
        elif view.result == "error":
            self.bot.logger.info(f"Failed to remove Member {member.id} from guild {ctx.guild.id}.")
