import discord

# !!!: DO NOT MAKE ACTUAL CHANGES HERE. THIS FILE DOES NOT DO ANYTHING. MAKE CHANGES IN sunreek.py TO
# CHANGE BOT FILES.
counter = 0
questions = ['Password?\n**NOT YOUR DISCORD PASSWORD**', 'What is your name?', 'How old are you?', 'Where did you get the link from? Please be specific. If it was a user, please use the full name and numbers(e.g. Echo#0109)', 'Why do you want to join?']


class Application:
    def __init__(self, applicant, channel, guild):
        global counter
        counter += 1
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


async def verify(message):
    guild = message.guild

    if verified_role in message.guild.get_member(message.author.id).roles:
        await message.channel.send('You are already verified')
        return
    try:
        applicant = guild.get_member(message.author.id)
        application = Application(applicant, message.channel, message.guild)
        channel = guild.get_channel(application_channel)
    except discord.errors.Forbidden:
        await message.channel.send('<@!'+str(message.author.id)+'> I cannot send you a message. Change your privacy settings in User Settings->Privacy & Safety')
        return

    await application.question()

    applied = await channel.send(embed=application.gen_embed())
    emojis = ['✅', '❓', '🚫', '❗']
    for emoji in emojis:
        await applied.add_reaction(emoji)

    def check(reaction, user):
        return user != client.user and user.guild_permissions.manage_roles and str(reaction.emoji) in emojis and reaction.message == applied

    while True:
        reaction, user = await client.wait_for('reaction_add', check=check)
        # TODO: allow multiple mods to react at once
        if str(reaction.emoji) == '✅':
            await application.applicant.add_roles(guild.get_role(verified_role))
            try:
                await message.author.send('You have been approved.')
            except Forbidden:
                await channel.send('Unable to DM <@!'+str(message.author.id)+'>')
            await application.applicant.remove_roles(guild.get_role(questioning_role))
            await application.applicant.remove_roles(guild.get_role(unverified))
            await channel.send('<@!'+str(message.author.id)+'> approved')
            break
        elif str(reaction.emoji) == '❓':
            await application.applicant.add_roles(guild.get_role(questioning_role))
            await channel.send('<@!'+str(message.author.id)+'>  is being questioned')
            await message.author.send('You have been pulled into questioning.')
        elif str(reaction.emoji) == '🚫':
            reason = await read_line(client, guild.get_channel(application_channel), 'Why was <@!'+str(message.author.id)+'> denied?', user,
                                     delete_prompt=False, delete_response=False)
            await message.author.send('Your application denied for:\n> ' + reason.content)
            await channel.send('<@!'+str(message.author.id)+'> was denied for:\n> '+reason.content)
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
                    break
                except discord.HTTPException:
                    await channel.send('Ban failed. Please try again, by reacting to the message again.')
                except discord.Forbidden:
                    await channel.send('Error 403: Forbidden. Insufficient permissions.')