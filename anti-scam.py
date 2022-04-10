import discord
import sys
import time

from main import read_line

version_num = '2.1.0'

prefix = '>'

application_channel = 813991832593367051
log_channel = 933539437357432892     # channel ID of the channel where logs go

unverified_role_id = 813996107126276127
verified_role_id = 758487413257011271

counter = 0
active_forms = 0
incomplete_forms = 0
submitted_forms = 0
application_questions = ['Server Password?\n**NOT YOUR DISCORD PASSWORD**',
                         'What is your nickname?',
                         'How old are you?',
                         'Where did you get the link from? Please be specific. If it was a user, please use the full '
                         'name and numbers(e.g. Echo#0109)',
                         'Why do you want to join?']

game = discord.Game('Scanning for pings')
client = discord.Client()


class Application:
    """
    The class containing membership applications
    Last docstring edit: -Autumn V2.1.0
    Last class edit: -Autumn V2.1.0
    """

    def __init__(self, applicant, channel, applicant_guild):
        global counter
        global active_forms
        global incomplete_forms
        counter += 1
        active_forms += 1
        incomplete_forms += 1
        self.applicant = applicant
        self.channel = channel
        self.guild = applicant_guild
        self.count = counter
        self.responses = []

    async def question(self):
        """
        Controls the questions the bot asks to the user.
        Last docstring edit: -Autumn V2.1.0
        Last class edit: -Autumn V2.1.0
        :return: NoneType
        """
        global application_questions
        global client

        dm = await self.applicant.create_dm()

        for question in application_questions:  # For every question in the list
            # Take user input and save it as a variable
            response = await read_line(client, dm, question, self.applicant, delete_prompt=False, delete_response=False)

            if question == application_questions[0]:  # This code only runs when checking the server password
                guesses = 0
                guess_list = '"'
                incorrect = True

                while incorrect:  # While the password is wrong:

                    if response.content.lower() == 'orange':  # if password is correct:
                        guess_list.append('orange"')
                        incorrect = False
                    else:  # if the password is wrong
                        question = 'Incorrect password. Please read the rules for the correct password.'
                        guesses += 1

                        # add the incorrect guesses to the list of responses
                        guess_list = guess_list + response.content + '", "'

                        # and re-ask for the password
                        response = await read_line(client,
                                                   dm,
                                                   question,
                                                   self.applicant,
                                                   delete_prompt=False,
                                                   delete_response=False)
            else:  # otherwise
                self.responses.append(response.content)  # Add user input to the list of responses
        await dm.send('Please wait while your application is reviewed. I will need to DM you when your application is '
                      'fully processed.')

    def gen_embed(self):
        """
        Generates an embed object to send in the application channel
        Last docstring edit: -Autumn V2.1.0
        Last class edit: -Autumn V2.1.0
        :return:
        """
        global application_questions

        embed = discord.Embed(title='Application #' + str(self.count))
        embed.set_author(name=self.applicant.name, icon_url=self.applicant.avatar_url)

        for i in range(len(application_questions)):
            if i == 0:
                embed.add_field(name='Password Guesses', value=self.responses[i])
            else:
                embed.add_field(name=application_questions[i], value=self.responses[i])

        embed.add_field(name='User ID', value=str(self.applicant.id), inline=False)

        return embed


async def verify(message):
    """
    The method that primarily handles member verification. All members must verify from this method. Sends DM to user,
    asks user questions, then sends answers to the moderators in a designated chat
    Last docstring edit: -Autumn V2.1.0
    Last class edit: -Autumn V2.1.0
    :param message: Discord message calling the method
    :return: NoneType
    """
    global active_forms
    global incomplete_forms
    global submitted_forms
    msg_guild = message.guild

    if verified_role_id in message.guild.get_member(message.author.id).roles:
        await message.channel.send('You are already verified')
        return

    applicant = message.author
    application = Application(applicant, message.channel, message.guild)

    channel = message.channel

    try:
        await application.question()
    except discord.errors.Forbidden:
        await message.channel.send('<@!'+str(message.author.id)+'> I cannot send you a message. Change your privacy '
                                                                'settings in User Settings->Privacy & Safety')
        active_forms -= 1
        incomplete_forms -= 1
        return

    applied = await channel.send(embed=application.gen_embed())
    emojis = ['✅', '🔁', '🚫']
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
        # Approved
        if str(reaction.emoji) == '✅':
            await application.applicant.add_roles(msg_guild.get_role(verified_role_id))

            try:
                await message.author.send('You have been approved.')
            except discord.Forbidden:
                await channel.send('Unable to DM <@!'+str(message.author.id)+'>')

            # await application.applicant.remove_roles(msg_guild.get_role(questioning_role_id))
            await application.applicant.remove_roles(msg_guild.get_role(unverified_role_id))
            await channel.send('<@!'+str(message.author.id)+'> approved')

            active_forms -= 1
            submitted_forms -= 1

            await applied.add_reaction('🆗')
            break
        # Redo-form
        elif str(reaction.emoji) == '🔁':
            reason = await read_line(client, msg_guild.get_channel(application_channel),
                                     'Why was <@!' + str(message.author.id) + '> denied?', user,
                                     delete_prompt=False, delete_response=False)

            if reason == 'cancel':
                await channel.send('Action cancelled')
                continue
            else:
                await message.author.send('Please redo your form. Your application denied for:\n> ' + reason.content)
                await channel.send('<@!'+str(message.author.id)+'> was denied for:\n> '+reason.content)

                active_forms -= 1
                submitted_forms -= 1

                await applied.add_reaction('🆗')
                break
        # Ban user
        elif str(reaction.emoji) == '🚫':
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


async def ping(message):
    """
    Returns how long it takes the bot to send a message
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :param message: message that called the quit command
    :return: None
    """
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message):
    """
    Returns the current version of the bot
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :param message: message that called the command
    :return: None
    """
    await message.channel.send('I am currently running version ' + version_num)


async def quit(message):
    """
    Quits the bot, and closes the program. Replys and updates the game status to alert users to it quitting.
    :param message: message that called the quit command
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :return: N/A. program closes
    """
    global game
    if message.author.guild_permissions.administrator:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def scan_message(message, is_flagged=False):
    """
    The primary anti-scam method. This method is given a message, counts the number of flags in a given message, then
    does nothing if no flags, flags the message as a possible scam if 1-3, or flags and deletes the message at 3+ flags.
    Last docstring edit: -Autumn V1.2.2
    Last method edit: -Autumn V1.2.3
    :param message: the message sent
    :param is_flagged: if the message is flagged for deletion
    :return: None
    """
    flags = 0
    content = message.content.lower()

    for word in blacklist:
        index = content.find(word)
        if index != -1:
            flags += 1

    if flags < 2:
        return
    else:
        if flags >= 3 and is_flagged is False:
            await message.delete()

        content = message.content.replace('@', '@ ')

        channel = message.guild.get_channel(log_channel)

        embed = discord.Embed(title='Possible Scam in #' + str(message.channel.name), color=0xFF0000)
        embed.set_author(name='@' + str(message.author.name), icon_url=message.author.avatar_url)
        embed.add_field(name='message', value=content, inline=False)
        embed.add_field(name='Flags', value=str(flags), inline=False)
        embed.add_field(name='Sender ID', value=message.author.id)
        embed.add_field(name='Channel ID', value=message.channel.id)
        embed.add_field(name='Message ID', value=message.id)

        if flags < 3:
            embed.add_field(name='URL', value=message.jump_url, inline=False)
        await channel.send(embed=embed)


@client.event
async def on_ready():
    """
    Confirms the bot is online, and has started
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :return: N/A
    """
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=game)


switcher = {'ping': ping, 'version': version, 'quit': quit}
blacklist = ['@everyone', 'https://', 'gift', 'nitro', 'steam', '@here', 'free', 'who is first? :)', "who's first? :)"]
code = 'plsdontban'     # flag escape code


@client.event
async def on_message(message):
    """
    When a message happens, it scans the message for
    Last docstring edit: -Autumn V1.2.2
    Last method edit: Unknown
    :param message: the message sent
    :return: n/a
    """
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        if not message.author.guild_permissions.mention_everyone:
            await scan_message(message, True)
            await message.delete()
    content = message.content.lower()
    if content.find(code) != -1 or message.author.guild_permissions.administrator:
        pass
    else:
        await scan_message(message)

    if message.content.startswith(prefix):
        command = message.content[1:].lower().split(' ', 1)
        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            pass
        if command[0] == 'print':
            print(message.content)


def run_antiscam():
    inp = int(input('Input a bot num\n1. Anti-scam\n'))
    if inp == 1:
        client.run(token)


if __name__ == '__main__':
    run_antiscam()
