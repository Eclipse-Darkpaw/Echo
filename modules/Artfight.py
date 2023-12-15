import discord
import json
import sunreek
import datetime

from difflib import SequenceMatcher
from fileManagement import server_settings_path
from main import read_line
from random import randint

async def setup(message, client):
    """
    Sets up the server for artfight
    :param message:
    :return:
    """
    progress = await message.channel.send('__**Assignment**__')
    
    async def update_progress():
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
        await progress.edit(content=msg)
    
    roleIDs = {}
    responses = []
    
    for i in range(1, 3):
        while True:
            response = await read_line(client,
                                       message.channel,
                                       f'Please tag the team {i} role.',
                                       target=message.author,
                                       delete_prompt=True,
                                       delete_response=True)
            try:
                roleIDs[f'team{i}'] = response.role_mentions[0].id
                responses.append((f'Team {i} Role', response.role_mentions[0].id))
                await update_progress()
                break
            except IndexError:
                await message.reply('No roles were mentioned')
    
    while True:
        response = await read_line(client,
                                   message.channel,
                                   f'Please tag the artfight channel, or "None" if it doesnt exist',
                                   target=message.author,
                                   delete_prompt=True,
                                   delete_response=True)
        try:
            artfight_channel = response.channel_mentions[0].id
            responses.append(("channel", response.channel_mentions[0].id))
            await update_progress()
            break
        except IndexError:
            await message.reply('No channels were mentioned')
    artfight_data = {"roles": roleIDs, "channel": artfight_channel, "scores": {'team1': 0, 'team2': 0}}
    
    with open(server_settings_path) as file:
        data = json.load(file)
    
    data[str(message.guild.id)]['artfight'] = artfight_data
    
    with open(server_settings_path, 'w') as file:
        file.write(json.dumps(data, indent=4))
    
    await message.reply('Data saved')


async def artfight_submit(message, team_num, client):
    with open(server_settings_path) as file:
        data = json.load(file)
        
    startday = 11
    
    artfight_team1_score = data[str(message.guild.id)]['artfight']['scores']['team1']
    artfight_team2_score = data[str(message.guild.id)]['artfight']['scores']['team2']

    dm = await message.author.create_dm()
    artfight_day = int(datetime.datetime.now().strftime("%d")) - startday
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
            image = await read_line(client, dm, 'What image are you submitting? Only submit one image.', message.author,
                                    delete_prompt=False, delete_response=False)
            link = image.attachments[0].url
        
            for question in artfight_questions:
                question = f'<@!{message.author.id}> {question}'
                response = await read_line(client, dm, question, message.author, delete_prompt=False, delete_response=False)
                responses.append(response)
        except discord.Forbidden:
            await message.reply('Unable to DM You, please change your privacy settings.')
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
    
        embed = discord.Embed(title=responses[5].content, description=f'A Submission from <@{message.author.id}>')
        embed.add_field(name='Score', value=str(score)+' ornaments', inline=False)
        embed.set_image(url=link)
        embed.color = message.author.color
    
        await dm.send(embed=embed)
        response = await read_line(client, dm, 'Do you want to submit this? "Y" for yes.', message.author,
                                   delete_prompt=False, delete_response=False)
    
        if response.content.lower() == 'y':
    
            if team_num == 1:
                artfight_team1_score += score
                pass
            elif team_num == 2:
                artfight_team2_score += score
                pass
            
            data[str(message.guild.id)]['artfight']['scores']['team1'] = artfight_team1_score
            data[str(message.guild.id)]['artfight']['scores']['team2'] = artfight_team2_score
            
            with open(server_settings_path, 'w') as file:
                file.write(json.dumps(data, indent=4))
            await dm.send('Score counted!\n'
                          'Sending Submission')
            return embed
            
        else:
            await dm.send('Submission cancelled. Restarting the grading.')


async def artfight(message, client, month, day):
    with open(server_settings_path) as file:
        data = json.load(file)
    try:
        artfight_team1_score = data[str(message.guild.id)]['artfight']['scores']['team1']
        artfight_team2_score = data[str(message.guild.id)]['artfight']['scores']['team2']
    except KeyError:
        artfight_team1_score, artfight_team2_score = 0, 0
    
    try:
        artfight_team1 = message.guild.get_role(data[str(message.guild.id)]['artfight']['roles']['team1'])
        artfight_team2 = message.guild.get_role(data[str(message.guild.id)]['artfight']['roles']['team2'])
    except KeyError:
        artfight_team1, artfight_team2 = None, None
    artfight_channel = None
    
    command = message.content[1:].split(' ', 3)

    if len(command) == 1:
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
        await message.channel.send(embed=artfight_embed)
    elif command[1] == 'join' and month == 12 and 10 <= day < 18:
        if artfight_team1 in message.author.roles or artfight_team2 in message.author.roles:
            await message.reply("You are already on a team")
            return
        else:
            if len(command) == 2:
                command.append(str(randint(1, 2)))
                
            if command[2] == '1':
                await message.author.add_roles(artfight_team1)
                await message.reply(f'You have been added to {artfight_team1.name}')
            elif command[2] == '2':
                await message.author.add_roles(artfight_team2)
                await message.reply(f'You have been added to {artfight_team2.name}')
            else:
                if (SequenceMatcher(None, artfight_team1.name, command[2]).ratio() >= 0.5 and
                        SequenceMatcher(None, artfight_team1.name, command[2]).ratio() >
                        SequenceMatcher(None, artfight_team2.name, command[2]).ratio()):
                    await message.author.add_roles(artfight_team1)
                    await message.reply(f'You have been added to {artfight_team1.name}')
                elif (SequenceMatcher(None, artfight_team2.name, command[2]).ratio() >= 0.5 and
                      SequenceMatcher(None, artfight_team2.name, command[2]).ratio() >
                      SequenceMatcher(None, artfight_team1.name, command[2]).ratio()):
                    await message.author.add_roles(artfight_team2)
                    await message.reply(f'You have been added to {artfight_team2.name}')
                else:
                    await message.reply("I have no idea what team you're trying to join. Please try again")
    elif (command[1] == 'scores' or command[1] == 'score') and message.author.guild_permissions.manage_roles:
        score_embed = discord.Embed(title='Team scores')
        score_embed.add_field(name=f'{artfight_team1.name} Score', value=str(artfight_team1_score))
        score_embed.add_field(name=f'{artfight_team2.name} Score', value=str(artfight_team2_score))
        await message.reply(embed=score_embed)
        return
    elif command[1] == 'submit' and month == 12 and 11 < day < 25:
        roles = message.author.roles
        role_ids = []

        for role in roles:
            role_ids.append(role.id)

        if message.channel.id == data[str(message.guild.id)]['artfight']['channel']:
            if artfight_team1 in message.author.roles:
                embed = await artfight_submit(message, 1, client)
            elif artfight_team2 in message.author.roles:
                embed = await artfight_submit(message, 2, client)
            else:
                await message.reply('You are not on an artfight team!')
                return
            if type(embed) is int:
                if embed == -1:
                    return
                elif embed == -2:
                    await message.reply('Unable to score submission. Given bad values. Please retry')
                    return
                else:
                    await message.reply('An unknown error occurred, please retry your submission.')
            else:
                await message.reply(embed=embed)
                dm = await message.author.create_dm()
                await dm.send('Submitted')
        else:
            await message.reply(f'You can only use this in <#{artfight_channel}>!')
    elif command[1] == 'remove' and message.author.guild_permissions.manage_roles:
        with open(server_settings_path) as file:
            data = json.load(file)
    
        if command[2] == '1':
            data[str(message.guild.id)]['artfight']['scores']['team1'] -= int(command[3])
            await message.reply(f'{command[3]} ornaments removed from {artfight_team1.name}')
        elif command[2] == '2':
            data[str(message.guild.id)]['artfight']['scores']['team2'] -= int(command[3])
            await message.reply(f'{command[3]} ornaments removed from {artfight_team2.name}')
        
        with open(server_settings_path, 'w') as file:
            file.write(json.dumps(data, indent=4))
        await message.reply('Data saved')
    elif command[1] == 'setup' and message.author.guild_permissions.manage_roles:
        await setup(message, client)
    else:
        await message.reply('Invalid argument')
