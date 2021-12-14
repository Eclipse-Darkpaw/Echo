import time
import discord
import os
import sys
from dotenv import load_dotenv
from profile import display_profile, set_bio
from fileManagement import profile_path
from refManagement import ref, set_ref, add_ref, oc
from main import read_line

load_dotenv()
start_time = time.time()
# todo: add uptime feature
# todo: add a master prefix only applicable to you as a back door

prefix = '}'
version_num = '1.12.17'

eclipse_id = 440232487738671124

intents = discord.Intents.default()
intents.members = True

game = discord.Game(prefix + "help for commands")
client = discord.Client(intents=intents)

guild = None
application_channel = 819223217281302598   # channel where finished applications go
unverified = 612958044132737025
verified_role = 811522721824374834         # role to assign members who verify successfully
questioning_role = 819238442931716137      # Role to assign when users
mail_inbox = 840753555609878528            # modmail inbox channel

counter = 666
active_forms=0
incomplete_forms=0
submitted_forms=0
questions = ['Server Password?\n**NOT YOUR DISCORD PASSWORD**\n(you have 3 attempts to fill the form)', 'What is your nickname?', 'How old are you?', 'Where did you get the link from? Please be specific. If it was a user, please use the full name and numbers(e.g. Echo#0109)', 'Why do you want to join?']


artfight_enabled = True

class Application:
    def __init__(self, applicant, channel, guild):
        global counter
        global active_forms
        global incomplete_forms
        counter += 1
        active_forms += 1
        incomplete_forms += 1
        self.applicant = applicant
        self.channel = channel
        self.guild = guild
        self.count = counter
        self.responses = []

    async def question(self):
        global questions
        global client
        dm = await self.applicant.create_dm()
        for question in questions:
            question = '<@!' + str(self.applicant.id) + '> ' + question
            response = await read_line(client, dm, question, self.applicant, delete_prompt=False, delete_response=False)
            self.responses.append(response.content)
        await dm.send('Please wait while your application is reviewed. I will need to DM you when your application is fully processed.')

    def gen_embed(self):
        global questions

        embed = discord.Embed(title='Application #' + str(self.count))
        embed.set_author(name=self.applicant.name, icon_url=self.applicant.avatar_url)
        for i in range(len(questions)):
            embed.add_field(name=questions[i], value=self.responses[i])
        embed.add_field(name='User ID', value=str(self.applicant.id), inline=False)

        return embed

    def __str__(self):
        return 'Application for ' + str(self.applicant) + '\nWhere did you get the link from?'


class Message:
    def __init__(self, content, channel):
        self.content = content
        self.channel = channel

    def reply(self):
        return -1


async def verify(message):
    global active_forms
    global incomplete_forms
    global submitted_forms
    guild = message.guild

    if verified_role in message.guild.get_member(message.author.id).roles:
        await message.channel.send('You are already verified')
        return

    applicant = guild.get_member(message.author.id)
    application = Application(applicant, message.channel, message.guild)
    channel = guild.get_channel(application_channel)

    try:
        await application.question()

    except discord.errors.Forbidden:
        await message.channel.send('<@!'+str(message.author.id)+'> I cannot send you a message. Change your privacy settings in User Settings->Privacy & Safety')
        active_forms -= 1
        incomplete_forms -= 1
        return

    applied = await channel.send(embed=application.gen_embed())
    emojis = ['✅', '❓', '🚫', '❗']
    for emoji in emojis:
        await applied.add_reaction(emoji)

    def check(reaction, user):
        return user != client.user and user.guild_permissions.manage_roles and str(reaction.emoji) in emojis and reaction.message == applied

    incomplete_forms -= 1
    submitted_forms += 1
    while True:
        reaction, user = await client.wait_for('reaction_add', check=check)
        # TODO: allow multiple mods to react at once
        if str(reaction.emoji) == '✅':
            await application.applicant.add_roles(guild.get_role(verified_role))
            try:
                await message.author.send('You have been approved.')
            except discord.Forbidden:
                await channel.send('Unable to DM <@!'+str(message.author.id)+'>')
            await application.applicant.remove_roles(guild.get_role(questioning_role))
            await application.applicant.remove_roles(guild.get_role(unverified))
            await channel.send('<@!'+str(message.author.id)+'> approved')
            active_forms -= 1
            submitted_forms -= 1
            break
        elif str(reaction.emoji) == '❓':
            await application.applicant.add_roles(guild.get_role(questioning_role))
            await channel.send('<@!'+str(message.author.id)+'>  is being questioned')
            await message.author.send('You have been pulled into questioning.')
        elif str(reaction.emoji) == '🚫':
            reason = await read_line(client, guild.get_channel(application_channel), 'Why was <@!'+str(message.author.id)+'> denied?', user,
                                     delete_prompt=False, delete_response=False)

            if reason == 'cancel':
                await channel.send('Action cancelled')
                continue
            else:
                await message.author.send('Your application denied for:\n> ' + reason.content)
                await channel.send('<@!'+str(message.author.id)+'> was denied for:\n> '+reason.content)
                active_forms -= 1
                submitted_forms -= 1
                break
        elif str(reaction.emoji) == '❗':
            reason = await read_line(client, guild.get_channel(application_channel), 'Why was <@!'+str(message.author.id)+'> banned? write `cancel` to cancel.', user,
                                     delete_prompt=False, delete_response=False)
            reason = reason.content
            if reason == 'cancel':
                await channel.send('Ban cancelled')

            else:
                try:
                    await message.guild.ban(user=application.applicant,reason=reason)
                    await channel.send('<@{}> banned for\n> {}'.format(message.author.id, reason))
                    active_forms -= 1
                    submitted_forms -= 1
                    break
                except discord.HTTPException:
                    await channel.send('Ban failed. Please try again, by reacting to the message again.')
                except discord.Forbidden:
                    await channel.send('Error 403: Forbidden. Insufficient permissions.')


async def ping(message):
    # log(message)
    start = time.time()
    x = await message.channel.send('Pong!')
    ping = time.time() - start
    edit = x.content + ' ' + str(int(ping * 1000)) + 'ms'
    await x.edit(content=edit)


async def version(message):
    # log(message)
    await message.channel.send('I am currently running version ' + version_num)


async def quit(message):
    global game
    # log(message)
    # await save(message)
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        await message.channel.send('Goodbye :wave:')
        await client.change_presence(activity=discord.Game('Going offline'))
        sys.exit()
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def restart(message):
    # log(message)
    # await save(message)
    if message.author.guild_permissions.administrator or message.author.id == eclipse_id:
        os.execl(sys.executable,__file__,'main.py')
    else:
        await message.channel.send('You do not have permission to turn me off!')


async def modmail(message):
    sender = message.author

    dm = await sender.create_dm()
    try:
        subject = await read_line(client, dm, 'Subject Line:', sender, delete_prompt=False, delete_response=False)
        subject = 'Modmail | ' + subject.content
        body = await read_line(client, dm, 'Body:', sender, delete_prompt=False, delete_response=False)
        await dm.send('Your message has been sent')
    except discord.Forbidden:
        message.reply('Unable to DM. Check your privacy settings')

    mail = discord.Embed(title=subject, color=0xadd8ff)
    mail.set_author(name=sender.name, icon_url=sender.avatar_url)
    mail.add_field(name='Message', value=body.content)
    await message.guild.get_channel(mail_inbox).send(embed=mail)


async def help(message):
    # square brackets are optional arguments, angle brackets are required
    command = message.content[1:].split(' ')
    if len(command) == 1:
        embed = discord.Embed(title="SunReek Command list", description='Square brackets are optional arguments. Angle brackets are required arguments', color=0x45FFFF)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        embed.add_field(name='`'+prefix+'help`', value="That's this command!", inline=False)
        embed.add_field(name='`'+prefix+'verify`', value='Verifies an un verified member.', inline=False)
        embed.add_field(name='`'+prefix+'modmail`', value='Sends a private message to the moderators.', inline=False)
        embed.add_field(name='`'+prefix+'version_num`', value='What version the bot is currently on', inline=False)
        embed.add_field(name='`'+prefix+'profile [member tag/member id]/[edit]`', value="Gets a tagged user's profile or your profile", inline=False)
        embed.add_field(name='`'+prefix+'ref [member tag/member id]`', value="gets a user's ref sheet", inline=False)
        embed.add_field(name='`'+prefix+'setref <attachment>`', value="Sets a user's ref. Overwrites all current ref data", inline=False)
        embed.add_field(name='`'+prefix+'addref <attachment>`', value="Adds another ref to your file.", inline=False)
        embed.add_field(name='`'+prefix+'crsdky [arguments]`', value='commands for the CursedKeys game. will show the list of cursed keys if argument is left off', inline=False)
        embed.add_field(name='`'+prefix+'OC`', value="Manages a users OCs", inline=False)
        embed.add_field(name='Moderator Commands', value='Commands that only mods can use', inline=False)
        embed.add_field(name='`'+prefix+'quit`', value='quits the bot', inline=False)
        embed.add_field(name='`' + prefix + 'join_pos [target ID]`', value='Shows the position a member joined in. shows message author if target is left blank', inline=False)
        embed.add_field(name='`' + prefix + 'artfight', value='Commands for the annual artfight')
        await message.channel.send(embed=embed)
    elif command[1] == 'help':
        help_embed = discord.Embed(title="SunReek Command list", color=0x45FFFF)
        help_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        help_embed.add_field(name='`' + prefix + 'help [bot command]`', value="That's this command!", inline=False)
        await message.channel.send(embed=help_embed)
    elif command[1] == 'profile':
        profile_embed = discord.Embed(title='Profile Command list',description='Displays a users profile', color=0x45FFFF,)
        profile_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        profile_embed.add_field(name='No argument', value='Displays your profile', inline=False)
        profile_embed.add_field(name='`User ID/Tagged User/Nickname`', value='Searches for a user\'s profile. Tagging the desired user, or using their member ID yeilds the most accurate results.', inline=False)
        profile_embed.add_field(name='`edit <string>`', value='Changes your profile to say what you want. Only emotes from this server can be used.', inline=False)
        await message.channel.send(embed=profile_embed)
    elif command[1] == 'crsdky':
        crsdky_embed = discord.Embed(title="`}crsdky Command list", color=0x45FFFF)
        crsdky_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        crsdky_embed.add_field(name='Notes', value='Used by going `}crsdky [argument]`, ', inline=False)
        crsdky_embed.add_field(name='`join`', value='Joins the game of crsdky. Users cannot join after the game starts.', inline=False)
        crsdky_embed.add_field(name='`leave`', value='leaves the game of crsdky', inline=False)
        crsdky_embed.add_field(name='`numleft`', value='Shows the number of players left.', inline=False)
        await message.channel.send(embed=crsdky_embed)
        if message.author.guild_permissions.manage_roles:
            mod_crsdky_embed = discord.Embed(title='`}crsdky` Mod Commands',color=message.author.color)
            mod_crsdky_embed.add_field(name='Notes', value='All these commands require the user to have moderator permissions.', inline=False)
            mod_crsdky_embed.add_field(name='`set <char list>`', value='Sets the cursed keys. Takes lowercase letters and symbols.', inline=False)
            mod_crsdky_embed.add_field(name='`start`', value='Starts the round, and prevents new players from joining', inline=False)
            mod_crsdky_embed.add_field(name='`stop`', value='Pauses the round until the `start` command is recieved', inline=False)
            mod_crsdky_embed.add_field(name='`resetPlayer`', value='Removes all players from the game', inline=False)
            await message.channel.send(embed=mod_crsdky_embed)
    elif command[1] == 'ref':
        ref_embed = discord.Embed(title='`'+prefix+'ref` Command List', description='Displays a users primary ref.', color=0x45FFFF)
        ref_embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        ref_embed.add_field(name='No argument', value='Displays your ref', inline=False)
        ref_embed.add_field(name='`User ID/Tagged User/Nickname`', value='Searches for a user\'s profile. Tagging the desired user, or using their member ID yeilds the most accurate results.', inline=False)
        ref_embed.add_field(name='`set <string/ref>`', value='Changes your ref to say what you want. Only emotes from this server can be used.', inline=False)
        await message.channel.send(embed=ref_embed)
    elif command[1] == 'OC':
        embed = discord.Embed(title='`' + prefix + 'OC` Command List', description='Manages a users OC\'s ref.',
                                  color=0x45FFFF)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        embed.add_field(name='add [OC name] [description/attachment]', value='Adds a new OC', inline=False)
        embed.add_field(name='edit [OC name] [description/attachment]', value='Edits an existing OC', inline=False)
        embed.add_field(name='show [OC owner ID/tagged] [OC name]', value='Shows an OC', inline=False)
        embed.add_field(name='tree [OC owner ID/tagged]', value='Shows a user\'s OCs', inline=False)
        await message.channel.send(embed=embed)
    elif command[1] == 'artfight':
        artfight_embed = discord.Embed(title='`'+prefix+'artfight` Command List', description='This is the commands for the annual Art Fight')
        artfight_embed.add_field(name='join', value='this command is disabled', inline=False)
        artfight_embed.add_field(name='scores', value='shows the team scores', inline=False)
        artfight_embed.add_field(name='submit', value='This is how you submit art. See <#787316128614973491> for scoring.', inline=False)
        await message.channel.send(embed=artfight_embed)



async def profile(message):
    command = message.content.split(' ', 2)
    if len(command) == 1:
        await display_profile(message)
    elif command[1] == 'edit':
        try:
            set_bio(message.author, command[2])
            await message.channel.send('Bio set')
        except ValueError:
            await message.channel.send('Error. Bio not set, please use ASCII characters and custom emotes.')
    else:
        await display_profile(message)


cursed_keys_running = False
crsd_keys = []
player_role_id = 863630913686077450


async def cursed_keys(message):
    global cursed_keys_running
    global crsd_keys

    command = message.content[1:].split(' ', 2)
    if len(command) == 1:
        if len(crsd_keys) == 0:
            await message.reply('there are no cursed keys')
        else:
            await message.reply('cursed keys are: '+str(crsd_keys))
    elif command[1] == 'join':
        # either by command or by some other mechanism
        if not cursed_keys_running:
            if message.guild.get_role(player_role_id) in message.author.roles:
                await message.reply('You are already a part of this game!')
            else:
                await message.author.add_roles (message.guild.get_role(player_role_id))
                await message.reply('Joined the game!')
        else:
            await message.reply("Unable to join. a game is already running")
    elif command[1] == 'leave':
        await message.author.remove_roles(message.guild.get_role(player_role_id))
        await message.reply('You have been removed from the game')
    elif command[1] == 'set':
        chars = command[2].split(' ')
        keys = []
        for char in chars:
            if len(char) > 1:
                pass
            else:
                keys.append(char.lower())
                crsd_keys = keys
        await message.reply('Cursed Keys set: '+ str(crsd_keys))
    elif command[1] == 'start':
        if message.author.guild_permissions.manage_roles:
            cursed_keys_running = True
            if len(crsd_keys) == 0:
                await message.reply('Unable to start game! No Cursed Keys set!')
            else:
                await message.reply('<@&863630913686077450> The game is starting! Cursed Keys are ' + str(crsd_keys))
        else:
            await message.reply('Invalid permissions')
    elif command[1] == 'auto-enroll':
        if message.author.guild_permissions.manage_roles:
            if command[2] == all:
                for member in message.guild.members:
                    await member.add_roles(player_role_id)
            else:
                roles = message.role_mentions
                for role in roles:
                    for member in role.members:
                        await member.add_roles(player_role_id)
                await message.reply('members added')
        else:
            await message.reply('invalid permissions')
    elif command[1] == 'resetPlayers':
        if message.author.guild_permissions.manage_roles:
            for member in message.guild.get_role(player_role_id).members:
                await member.remove_roles(message.guild.get_role(player_role_id))
        await message.reply('Players reset')
    elif command[1] == 'stop':
        if message.author.guild_permissions.manage_roles:
            cursed_keys_running = False
            await message.reply('Game Stopped')
        else:
            await message.reply('Invalid Permissions')
    elif command[1] == 'numleft':
        await message.reply(str(len(message.guild.get_role(player_role_id).members)))


async def purge(message):
    '''method removes all members with the unverified role from Rikoland'''
    if message.author.guild_permissions.manage_roles:
        unverified_ppl = message.guild.get_role(unverified).members
        num_kicked = 0
        for member in unverified_ppl:
            try:
                await member.kick(reason='Server purge.')
                num_kicked += 1
            except Forbidden:
                await message.channel.send('unable to ban <@' + str(member.id) + '>')
        await message.reply(str(len(unverified_ppl)) + ' members purged from Rikoland')
    else:
        await message.reply('Error 403: Forbidden\nInsufficient Permissions')


async def join_pos(message):
    command = message.content.split(' ')
    if len(command) == 1:
        target = message.author.id
    else:
        try:
            target = int(command[1])
        except ValueError:
            await message.reply('Value Error: Please make sure the ID is a number')

    join_pos = getJoinRank(target, message.guild)
    if join_pos == -1:
        await message.reply('Member <@%d> is not in the guild'%(target))
    else:
        name = guild.get_member(target).name
        await message.reply('Member %s joined in position %d' % (name, join_pos))


def getJoinRank(ID, guild):# Call it with the ID of the user and the guild
    members = guild.members

    def sortby(a):
        return a.joined_at.timestamp()


    members.sort(key=sortby)

    i = 0
    for member in members:
        i += 1
        if member.id == ID:
            return i
    return -1


def get_member_position(position, guild):
    members = guild.members

    def sortby(a):
        return a.joined_at.timestamp()

    members.sort(key=sortby)

    return members[position-1]


async def member_num(message):
    command = message.content.split(' ')
    if len(command) == 1:
        await message.reply('Missing Argument: Member number')
    else:
        try:
            position = int(command[1])
        except ValueError:
            await message.reply('Value Error: Please make sure the positon is a number')

    join_pos = get_member_position(position, message.guild)
    if join_pos == -1:
        await message.reply('There is no member in position %d' % (position))
    else:
        name = join_pos.name
        await message.reply('Member in postion %d has the ID %d' % (postion, name))


artfight_team1 = 918673949557129227     # coal factories
artfight_team2 = 918673909266645022     # black nosed reindeers

artfight_team1_score = 1760
artfight_team2_score = 1795

artfight_channel = 918673017549238283


async def artfight_submit(message, team_num):
    global artfight_team1_score
    global artfight_team2_score

    dm = await message.author.create_dm()

    questions = ['What type of submission is this?\n1:Black&White Sketch\n2:Color Sketch\n3:Black&White Lineart\n4:Flat colored\nPlease reply with the corrosponding number',
                 'Please reply with the number of OCs/characters in your submission',
                 'Is this shaded? Respond "Y" if yes, anything else for no',
                 'Is there a background? Respond "Y" if yes, anything else for no',
                 'What is the title of this piece?']
    responses = []
    try:
        image = await read_line(client, dm, 'What image are you submitting? Only submit one image.', message.author, delete_prompt=False, delete_response=False)
        link = image.attachments[0].url

        for question in questions:
            question = '<@!' + str(message.author.id) + '> ' + question
            response = await read_line(client, dm, question, message.author, delete_prompt=False, delete_response=False)
            responses.append(response)
    except discord.Forbidden as er:
        message.reply('Unable to DM You, please change your privacy settings.')
        return


    if int(responses[0].content) == 1:
        base = 5
    elif int(responses[0].content) == 2:
        base = 10
    elif int(responses[0].content) == 3:
        base = 20
    elif int(responses[0].content) == 4:
        base = 30
    else:
        await dm.send('Unable to score your submission')
        return -2

    num_chars = int(responses[1].content)

    if responses[2].content.lower() == 'y':
        shaded = 10
    else:
        shaded = 0

    if responses[3].content.lower() == 'y':
        bg = 20
    else:
        bg = 0

    score = (base + shaded) * num_chars + bg

    embed = discord.Embed(title=responses[4].content, description='A Submission from <@'+str(message.author.id)+'>')
    embed.add_field(name='Score', value=str(score)+' ornaments')
    embed.set_image(url=link)
    embed.color = message.author.color

    await dm.send(embed=embed)
    response = await read_line(client, dm, 'Do you want to submit this? "Y" for yes.', message.author, delete_prompt=False, delete_response=False)

    if response.content.lower() == 'y':

        if team_num == 1:
            artfight_team1_score += score
            pass
        elif team_num == 2:
            artfight_team2_score += score
            pass
        await dm.send('Submission sent!')
        return embed
    else:
        await dm.send('Submission cancelled. please redo')
        return -2


async def artfight(message):
    if not artfight_enabled:
        message.reply('This command is currently disabled')
        return
    command = message.content[1:].split(' ', 2)

    if len(command) == 1:
        await help(Message('}help artfight', message.channel))
    elif command[1] == 'join':
        await message.reply('This command is not functional')
        return
    elif command[1] == 'scores':
        score_embed = discord.Embed(title='Team scores')
        score_embed.add_field(name='Coal Factories Score', value=str(artfight_team1_score))
        score_embed.add_field(name='Black Nosed Rendeers Score', value=str(artfight_team2_score))
        await message.reply(embed=score_embed)
        return
    elif command[1] == 'submit':
        roles = message.author.roles
        role_ids = []

        for role in roles:
            role_ids.append(role.id)

        if message.channel.id == artfight_channel:
            if artfight_team1 in role_ids:
                embed = await artfight_submit(message, 1)

                if embed == -1:
                    await message.reply('Error: Please retry your submission')
                    return
            elif artfight_team2 in role_ids:
                embed = await artfight_submit(message, 2)

                if embed == -1:
                    await message.reply('Error: Please retry your submission')
                    return
            else:
                await message.reply('You are not on an artfight team!')
                return
            await message.reply(embed=embed)
        else:
            await message.reply('You can only use this in <#' + str(artfight_channel) + '>!')


async def numforms(message):
    await message.reply(str(active_forms) + ' active forms \n' +
                        str(incomplete_forms) + ' incomplete \n' +
                        str(submitted_forms) + ' forms Submitted')




@client.event
async def on_ready():
    global guild

    print('We have logged in as {0.user}'.format(client))

    guild = client.get_guild(840181552016261170)
    await client.change_presence(activity=game)
    await guild.get_member(eclipse_id).send('Running, and active')


switcher = {'help': help, 'ping': ping, 'version_num': version, 'verify': verify, 'modmail': modmail, 'quit': quit,
            'profile': profile, 'restart': restart, 'setref': set_ref, 'ref': ref, 'addref': add_ref,
            'crsdky': cursed_keys, 'oc': oc, 'purge': purge, 'join_pos': join_pos, 'activeforms': numforms,
            'artfight': artfight}


@client.event
async def on_message(message):
    global cursed_keys_running
    global application_channel
    global verified_role
    global questioning_role

    if message.author.bot:
        return
    if message.content.find('@here') != -1 or message.content.find('@everyone') != -1:
        pass
    if message.content.startswith(prefix):
        command = message.content[1:].lower().split(' ', 1)
        try:
            method = switcher[command[0]]
            await method(message)
        except KeyError:
            pass
        if command[0] == 'print':
            print(message.content)
    elif cursed_keys_running:
        if message.guild.get_role(player_role_id) in message.author.roles:
            for key in crsd_keys:
                if key in message.content.lower():
                    await message.author.remove_roles(message.guild.get_role(player_role_id))
                    await message.reply('You have been cursed for using the key: ' + key)
                    if len(message.guild.get_role(player_role_id).members) == 1:
                        cursed_keys_running = False
                        await message.channel.send('<@!' + str(message.guild.get_role(player_role_id).members[0].id) + '> wins the game!')
                    break


token = os.getenv('SUNREEK')
client.run(token)