import discord
import json

from main import read_line
from difflib import SequenceMatcher
from fileManagement import resource_file_path
"""
Handles all tasks related to member verification.
Last Docstring edit: -Autumn V3.0.0
Last File edit: -Autumn V3.4.0
"""

file_path = resource_file_path + 'servers.json'

counter = 0
active_forms = 0
incomplete_forms = 0
submitted_forms = 0
questions = ['Server Password?\n**NOT YOUR DISCORD PASSWORD**\n(you have 3 attempts to fill the form)',
                         'What is your nickname?',
                         'How old are you?',
                         'Where did you get the link from? Please be specific. If it was a user, please use the full '
                         'name and numbers(e.g. Echo#0109)',
                         'Why do you want to join?']
client = None


class Application:
    def __init__(self, applicant, channel, applicant_guild):
        """
        Stores user membership application data
        Last docstring edit: -Autumn V3.4.0
        Last method edit: -Autumn V3.4.0
        :param applicant: user applying
        :param channel: application channel
        :param applicant_guild: Guild applied from
        """
        global counter
        global file_path
        global questions
        
        counter += 1
        
        self.applicant = applicant
        self.channel = channel
        self.applicant_guild = applicant_guild
        self.count = counter
        self.responses = []
        self.passguesses = []
        self.attempts = 1
        try:
            with open(file_path) as file:
                data = json.load(file)
                self.application_questions = data[str(applicant_guild.id)]["questions"]
        except KeyError:
            print("exception!")
            self.application_questions = application_questions
        
        try:
            with open(file_path) as file:
                data = json.load(file)
                self.application_questions_display = data[str(applicant_guild.id)]["questions_display"]
        except KeyError:
            print("exception!")
            self.application_questions = application_questions
            

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
        
        # find the server code word if there is one.
        code = data[str(self.applicant_guild.id)]['codeword']
        
        # dm the applicant and ask them questions
        dm = await self.applicant.create_dm()
        
        for question in self.application_questions:
            if question == self.application_questions[0]:
                # server password checker
                # only ask for code if the code is not None and no guesses have been made
                if code is None:
                    pass
                elif len(self.passguesses) != 0:
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
                        self.passguesses.append(response.content)
                        similarity = SequenceMatcher(None, code, response.content).ratio()
                        if debug:
                            print(similarity)
                        if response.content[1:7] == 'verify':
                            pass
                        # compares user input to the real password. above a certain threshold gets
                        elif similarity >= 0.5:
                            self.responses.append(self.passguesses)
                            break
                        guesses -= 1
                        question = 'Incorrect password ' + str(guesses) + ' attempts remaining'
                        
                        if guesses <= 0:
                            await dm.send('No guesses remain. You have been removed from the server.')
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

        embed = discord.Embed(title=f'Application #{self.count}, Attempt #{self.attempts}')
        try:
            try:
                icon_url = self.applicant.guild_avatar.url
            except AttributeError:
                icon_url = self.applicant.avatar.url
        except AttributeError:
            icon_url = "https://media.discordapp.net/attachments/842662532808179734/1054686812410482729" \
                       "/frowning-face-with-open-mouth_1f626.png"
        embed.set_author(name=self.applicant.name, icon_url=icon_url)
        
        confirm_msg = await self.applicant.send(content="Is this information accurate? React with ✅ if yes or 🚫 if not",
                                    embed=self.gen_embed(1))
        
        emojis = ['✅', '🚫']

        for emoji in emojis:
            await confirm_msg.add_reaction(emoji)

        def check(reaction, user):
            """
            Checks for reactions on a message.
            :param reaction:
            :param user:
            :return: boolean
            """
            return (user != client.user)

        reaction, user = await client.wait_for('reaction_add', check=check)
        if str(reaction.emoji) == '✅':
            await confirm_msg.add_reaction('🆗')
            await dm.send(
                'Please wait while your application is reviewed. I will need to DM you when your application is '
                'fully processed.')
            return 1, self.passguesses
            
        elif str(reaction.emoji) == '🚫':
            await confirm_msg.add_reaction('🆗')
            application_channel = self.applicant_guild.get_channel(data[str(self.applicant_guild.id)]['channels'][
                                                                       'application'])
            await application_channel.send(content=f'<@{self.applicant.id}>', embed=self.gen_embed())
            await dm.send("Please restart")
            self.responses = [self.passguesses]
            self.attempts += 1

            return -2, self.passguesses
   

    def gen_embed(self, type=0):
        """
        generates the embed for the application.
        Last docstring edit: -Autumn V3.4.0
        Last method edit: -Autumn V3.4.0
        :param type: Type of embed to generate. 0 = for mods, 1 = for users
        :return:
        """

        embed = discord.Embed(title=f'Application #{self.count}, Attempt #{self.attempts}')
        try:
            try:
                icon_url = self.applicant.guild_avatar.url
            except AttributeError:
                icon_url = self.applicant.avatar.url
        except AttributeError:
            icon_url = "https://media.discordapp.net/attachments/842662532808179734/1054686812410482729/frowning-face-with-open-mouth_1f626.png"
        embed.set_author(name=self.applicant.name, icon_url=icon_url)
        
        for i in range(len(self.application_questions_display)):
            if type == 0:
                embed.add_field(name=self.application_questions_display[i], value=self.responses[i])
            elif type == 1:
                embed.add_field(name=self.application_questions[i], value=self.responses[i])

        embed.add_field(name='User ID', value=str(self.applicant.id), inline=False)

        return embed
        
    def __str__(self):
        return 'Application for ' + str(self.applicant) + '\nWhere did you get the link from?'


async def verify(message, client_in):
    """
    The method that primarily handles member verification. All members must verify from this method. Sends DM to user,
    asks user questions, then sends answers to the moderators in a designated chat
    Last docstring edit: -Autumn V3.1.0
    Last method edit: -Autumn V3.4.1.0
    :param message: Discord message calling the method
    :param client_in: Bot client handling IO functions
    :return: NoneType
    """
    if message.guild is None:
        await message.reply("You must use this in a server")
        return
    
    global active_forms
    global incomplete_forms
    global submitted_forms
    global client
    
    client = client_in
    msg_guild = message.guild
    
    # Check if member is verified
    with open(file_path) as file:
        data = json.load(file)
    
    try:
        application_channel = int(data[str(message.guild.id)]['channels']['application'])
    except KeyError:
        await message.reply("Unable to begin verification. Please inform the moderators about this issue.\n"
                            "Error code -1")
    
    try:
        verified_role_id = int(data[str(message.guild.id)]['roles']['member'])
    except KeyError:
        await message.reply("Unable to begin verification. Roles crucial roles are unassigned")
        
    try:
        questioning_role_id = int(data[str(message.guild.id)]['roles']['questioning'])
    except KeyError:
        questioning_role_id = None
        
    try:
        unverified_role_id = int(data[str(message.guild.id)]['roles']['unverified'])
    except KeyError:
        unverified_role_id = None
    
    if verified_role_id in message.guild.get_member(message.author.id).roles:   # what the fuck?
        await message.channel.send('You are already verified')
        return

    applicant = message.author
    application = Application(applicant, message.channel, message.guild)
    
    channel = message.guild.get_channel(application_channel)
    
    try:
        questioning_error_code, guesses = await application.question()
    except discord.errors.Forbidden:
        await message.channel.send(f'<@!{message.author.id}> I cannot send you a message. Change your privacy '
                                   f'settings in User Settings->Privacy & Safety')
        return
    
    while questioning_error_code == -2:
        questioning_error_code, guesses = await application.question()

    if questioning_error_code == -1:    # Got password wrong too many times
        
        try:                            # kicks the user and sends a message.
            # TODO: change to application channel
            await message.guild.get_channel(application_channel).send(f'<@!{message.author.id}> kicked for excessive'
                                                                      f' password guesses.\n{guesses}')
            await message.guild.kick(message.author, reason='Too many failed password attempts')
        except discord.Forbidden:       # User cannot be kicked
            
            # TODO: change to application channel
            await message.channel.send("Unable to complete task. Please verify my permissions are correct\n"
                                       "```Error 403\n"
                                       "Verification.py Line 148:13\n"
                                       "await message.guild.kick(message.author, reason='Too many failed password "
                                       "attempts')```")

    applied = await channel.send(content=f'<@{message.author.id}>', embed=application.gen_embed())
    emojis = ['✅', '❓', '🚫', '❗']
    for emoji in emojis:
        if questioning_role_id is None and emoji == emojis[1]:
            continue
        await applied.add_reaction(emoji)

    def check(reaction, user):
        """
        Checks for reactions on a message.
        :param reaction:
        :param user:
        :return: boolean
        """
        try:
            out = (user != client.user and
                    user.guild is not None and
                    user.guild_permissions.manage_roles and
                    str(reaction.emoji) in emojis and
                    reaction.message == applied)
        except AttributeError:
            print(str(user.id))

    while True:
        try:
            reaction, user = await client.wait_for('reaction_add', check=check)
            if str(reaction.emoji) == '✅':
                try:
                    await application.applicant.add_roles(message.guild.get_role(verified_role_id))
                except discord.Forbidden:
                    await channel.send('Unable to give role. Please check my permissions.')
                    continue
    
                try:
                    await message.author.send('You have been approved.')
                except discord.Forbidden:
                    await channel.send(f'Unable to DM <@!{message.author.id}>')
    
                await application.applicant.remove_roles(msg_guild.get_role(questioning_role_id))
                await application.applicant.remove_roles(msg_guild.get_role(unverified_role_id))
                await channel.send(f'<@!{message.author.id}> approved')
                
                await applied.add_reaction('🆗')
                break
            elif str(reaction.emoji) == '❓':
                await application.applicant.add_roles(msg_guild.get_role(questioning_role_id))
                
                questioning_room = message.guild.get_channel(int(data[str(message.guild.id)]['channels']['questioning']))
                thread_name = f'{message.author.name} Questioning'
                try:
                    thread = await questioning_room.create_thread(name=thread_name, auto_archive_duration=1440)
                    await thread.send(f'<@{message.author.id}>, You have been pulled into questioning by <@{user.id}>.')
                    await message.author.send(f'You have been pulled into questioning in <#{thread.id}>.')
                    await channel.send(f'<@!{message.author.id}> is being questioned in <#{thread.id}>')
                except discord.errors.Forbidden:
                    await channel.send(f'<@!{message.author.id}> is being questioned')
                    await message.author.send('You have been pulled into questioning.')
                    await message.guild.get_channel(application_channel).send('```Error 403: Forbidden.\nUnable to create '
                                                                              'thread. Please check my permissions. ```')
            elif str(reaction.emoji) == '🚫':
                # add a confirm feature
                
                reason = await read_line(client,
                                         msg_guild.get_channel(application_channel),
                                         f'Why was <@!{message.author.id}> denied? Write `cancel` to cancel.',
                                         user,
                                         delete_prompt=False,
                                         delete_response=False)
    
                if reason.content.lower() == 'cancel':
                    await channel.send('Action cancelled')
                    await reaction.remove(user)
                    continue
                else:
                    await message.author.send('Your application was denied for:\n> ' + reason.content)
                    await channel.send(f'<@!{message.author.id}> was denied for:\n> '+reason.content)
                    await applied.add_reaction('🆗')
                    break
            elif str(reaction.emoji) == '❗':
                reason = await read_line(client,
                                         msg_guild.get_channel(application_channel),
                                         f'Why was <@!{message.author.id}> banned? write `cancel` to cancel.',
                                         user,
                                         delete_prompt=False,
                                         delete_response=False)
                
                reason = reason.content
                
                if reason.lower() == 'cancel':
                    await channel.send('Ban cancelled')
                    await reaction.remove(user)
                else:
                    try:
                        await message.guild.ban(user=application.applicant, reason=reason)
                        await channel.send(f'<@{message.author.id}> banned for\n> {reason}')
                        await applied.add_reaction('🆗')
                        break
                    except discord.Forbidden:
                        await channel.send('Error 403: Forbidden. Insufficient permissions.')
                    except discord.HTTPException:
                        await channel.send('Ban failed. Please try again, by reacting to the message again.')
        except discord.errors.NotFound:
            await channel.send(f'Unable to perform action. <@{message.author.id}> cannot be found')
            await applied.add_reaction('🆗')
            break
            

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
    