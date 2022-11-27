import discord
import json

from discord.ext import commands
from main import read_line
from difflib import SequenceMatcher
from fileManagement import resource_file_path
"""
Handles all tasks related to member verification.
Last Docstring edit: -Autumn V3.0.0
Last File edit: -Autumn V3.0.0
"""

file_path = resource_file_path + 'servers.json'

counter = 0
active_forms = 0
incomplete_forms = 0
submitted_forms = 0
application_questions = ['Server Password?\n**NOT YOUR DISCORD PASSWORD**\n(you have 3 attempts to fill the form)',
                         'What is your nickname?',
                         'How old are you?',
                         'Where did you get the link from? Please be specific. If it was a user, please use the full '
                         'name and numbers(e.g. Echo#0109)',
                         'Why do you want to join?']
client = None


class Application:
    def __init__(self, applicant, channel, applicant_guild,):
        global counter
        global active_forms
        global incomplete_forms
        
        counter += 1
        active_forms += 1
        incomplete_forms += 1
        
        
        self.applicant = applicant
        self.channel = channel
        self.applicant_guild = applicant_guild
        self.count = counter
        self.responses = []
        self.passguesses = []

    async def question(self):
        """
        Questions the applicant
        Last docstring edit: -Autumn V3.0.0
        Last method edit: -Autumn V3.2.0
        :return:
        """
        global application_questions
        global client
        
        # Done: change to false for live deployment
        debug = False
        
        with open(file_path) as file:
            data = json.load(file)
        
        code = data[str(self.applicant_guild.id)]['codeword']
        dm = await self.applicant.create_dm()
        for question in application_questions:
            if question == application_questions[0]:
                if code is None:
                    pass
                else:
                    guesses = 3
                    for guess in range(guesses):
                        response = await read_line(client,
                                                   dm,
                                                   question,
                                                   self.applicant,
                                                   delete_prompt=False,
                                                   delete_response=False)
                        similarity = SequenceMatcher(None, code, response.content).ratio()
                        if debug:
                            print(similarity)
                        if similarity >= 0.4:
                            break
                        guesses -= 1
                        question = 'Incorrect password ' + str(guesses) + ' attempts remaining'
                        self.passguesses.append(response.content)
                        
                        if guesses <= 0:
                            await dm.send('No guesses remain.')
                            return -1, self.passguesses
                        else:
                            continue
            else:
                response = await read_line(client,
                                           dm,
                                           question,
                                           self.applicant,
                                           delete_prompt=False,
                                           delete_response=False)
            self.responses.append(response.content)
        await dm.send('Please wait while your application is reviewed. I will need to DM you when your application is '
                      'fully processed.')
        return 1, self.passguesses

    def gen_embed(self):
        """
        generates the embed for the application.
        Last docstring edit: -Autumn V3.0.0
        Last method edit: -Autumn V3.0.0
        :return:
        """
        global application_questions

        embed = discord.Embed(title='Application #' + str(self.count))
        try:
            icon_url = self.applicant.guild_avatar.url
        except AttributeError:
            icon_url = self.applicant.avatar.url
        embed.set_author(name=self.applicant.name, icon_url=icon_url)
        
        for i in range(len(application_questions)):
            embed.add_field(name=application_questions[i], value=self.responses[i])

        embed.add_field(name='User ID', value=str(self.applicant.id), inline=False)

        return embed
        
    def __str__(self):
        return 'Application for ' + str(self.applicant) + '\nWhere did you get the link from?'


async def verify(message, client_in):
    """
    The method that primarily handles member verification. All members must verify from this method. Sends DM to user,
    asks user questions, then sends answers to the moderators in a designated chat
    Last docstring edit: -Autumn V3.1.0
    Last method edit: -Autumn V3.1.1
    :param message: Discord message calling the method
    :param client_in: Bot client handling IO functions
    :return: NoneType
    """
    global active_forms
    global incomplete_forms
    global submitted_forms
    global client
    
    client = client_in
    msg_guild = message.guild

    # Check if member is verified
    with open(file_path) as file:
        data = json.load(file)
    
    application_channel = int(data[str(message.guild.id)]['channels']['application'])
    verified_role_id = int(data[str(message.guild.id)]['roles']['member'])
    questioning_role_id = int(data[str(message.guild.id)]['roles']['questioning'])
    unverified_role_id = int(data[str(message.guild.id)]['roles']['unverified'])
    
    if verified_role_id in message.guild.get_member(message.author.id).roles:
        await message.channel.send('You are already verified', client_in)
        return

    applicant = message.author
    application = Application(applicant, message.channel, message.guild)
    
    channel = message.guild.get_channel(application_channel)

    try:
        questioning_error_code, guesses = await application.question()
    except discord.errors.Forbidden:
        await message.channel.send('<@!'+str(message.author.id)+'> I cannot send you a message. Change your privacy '
                                                                'settings in User Settings->Privacy & Safety')
        active_forms -= 1
        incomplete_forms -= 1
        return

    if questioning_error_code == -1:    # Got password wrong too many times
        
        try:                            # kicks the user and sends a message.
            # TODO: change to application channel
            await message.channel.send('<@!'+str(message.author.id)+'> kicked for excessive password guesses.\n' + str(guesses))
            await message.guild.kick(message.author, reason='Too many failed password attempts')
        except discord.Forbidden:       # User cannot be kicked
            
            # TODO: change to application channel
            await message.channel.send("Unable to complete task. Please verify my permissions are correct\n"
                                       "```Error 403\n"
                                       "Verification.py Line 148:13\n"
                                       "await message.guild.kick(message.author, reason='Too many failed password "
                                       "attempts')```")

    applied = await channel.send(embed=application.gen_embed())
    emojis = ['✅', '❓', '🚫', '❗']
    for emoji in emojis:
        await applied.add_reaction(emoji)

    def check(reaction, user):
        """
        Checks for reactions on a message.
        :param reaction:
        :param user:
        :return: boolean
        """
        return user != client.user and user.guild_permissions.manage_roles and str(reaction.emoji) in emojis and\
               reaction.message == applied

    incomplete_forms -= 1
    submitted_forms += 1
    while True:
        reaction, user = await client.wait_for('reaction_add', check=check)
        if str(reaction.emoji) == '✅':
            
            await application.applicant.add_roles(message.guild.get_role(verified_role_id))

            try:
                await message.author.send('You have been approved.')
            except discord.Forbidden:
                await channel.send('Unable to DM <@!'+str(message.author.id)+'>')

            await application.applicant.remove_roles(msg_guild.get_role(questioning_role_id))
            await application.applicant.remove_roles(msg_guild.get_role(unverified_role_id))
            await channel.send('<@!'+str(message.author.id)+'> approved')

            active_forms -= 1
            submitted_forms -= 1

            await applied.add_reaction('🆗')
            break
        elif str(reaction.emoji) == '❓':
            await application.applicant.add_roles(msg_guild.get_role(questioning_role_id))
            await channel.send('<@!'+str(message.author.id)+'>  is being questioned')
            await message.author.send('You have been pulled into questioning.')
            
            questioning_room = message.guild.get_channel(int(data[str(message.guild.id)]['channels']['questioning']))
            thread_name = f'{message.author.name} Questioning'
            thread = await questioning_room.create_thread(name=thread_name, auto_archive_duration=1440)
            await thread.send(f'<@{message.author.id}>, You have been pulled into questioning by <@{user.id}>')
        elif str(reaction.emoji) == '🚫':
            # add a confirm feature
            
            reason = await read_line(client,
                                     msg_guild.get_channel(application_channel),
                                     'Why was <@!' + str(message.author.id) + '> denied? Write `cancel` to cancel.',
                                     user,
                                     delete_prompt=False, delete_response=False)

            if reason.content == 'cancel':
                await channel.send('Action cancelled')
                continue
            else:
                await message.author.send('Your application was denied for:\n> ' + reason.content)
                await channel.send('<@!'+str(message.author.id)+'> was denied for:\n> '+reason.content)
                active_forms -= 1
                submitted_forms -= 1
                await applied.add_reaction('🆗')
                break
        elif str(reaction.emoji) == '❗':
            reason = await read_line(client, msg_guild.get_channel(application_channel), 'Why was <@!' +
                                     str(message.author.id) + '> banned? write `cancel` to cancel.', user,
                                     delete_prompt=False, delete_response=False)
            reason = reason.content
            if reason == 'cancel':
                await channel.send('Ban cancelled')

            else:
                try:
                    await message.guild.ban(user=application.applicant, reason=reason)
                    await channel.send('<@{}> banned for\n> {}'.format(message.author.id, reason))
                    active_forms -= 1
                    submitted_forms -= 1
                    await applied.add_reaction('🆗')
                    break
                except discord.Forbidden:
                    await channel.send('Error 403: Forbidden. Insufficient permissions.')
                except discord.HTTPException:
                    await channel.send('Ban failed. Please try again, by reacting to the message again.')


async def setcode(message, codeword):
    """
    Changes the code word
    Last docstring edit: -Autumn V3.1.2
    Last method edit: -Autumn V3.1.2
    :param message: discord message calling the function
    :type codeword: String
    :param codeword: The codeword to be set to
    :return: None
    """
    with open(file_path) as file:
        data = json.load(file)
    
    data[str(message.guild.id)]['codeword'] = codeword
    
    with open(file_path, 'w') as file:
        file.write(json.dumps(data, indent=4))
    
    await message.reply(f'Code word changed to {codeword}')
    