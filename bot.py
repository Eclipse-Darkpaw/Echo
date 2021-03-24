import sys

client = None

def import_from_file(file_name, clientA):
    bot = open(file_name,'r')
    lines = bot.readlines()
    client = clientA
    return Bot(lines[0], lines[1])

class Bot:
    def __init__(self, name, prefix = '>'):
        self._name = name
        self._prefix = prefix

    '''Exports the Bot to a .bot file
    First line is the bot name
    second line is prefix'''
    def export_to_file(self):
        file = open(self._name + '.bot', 'w')
        lines = [self._name, self._prefix]
        file.writelines(lines)
        file.close()

    async def help(self, message):
        command = message.content[len(self._prefix):].split()
        if len(command) == 1:
            await message.channel.send('`help {command}` - thats this command.\n'
                                       '`repeat [phrase]` - repeats the user input\n'
                                       '***__Moderator Commands__***'
                                       '`quit` - quits the bot\n'
                                       '`ban [member] - bans a member`')
        else:
            pass


    async def verify(self, message):
        application = []
        application.append(message.author)
        application.append(message.channel)
        application.append(message.guild)
        await message.delete()

        await message.channel.send('Where did you get the link from?')
        where = await readMessage(message.channel, client)
        application.append(where.content)
        '''
        Status code
        0 = awaiting approval
        1 = approved
        2 = denied
        3 = Secondary role/questioning
        '''
        status = 0
        application = application_channel.send()
        emojis = ['✅', '❓', '🚫', '❗']
        for emoji in emojis:
            await application.add_reaction(emoji)
        await client.wait_for('reaction')

        def check(reaction):
            return

        reaction = await client.wait_for('reaction_add')
        if str(reaction.emoji) == '✅':
            await application[0].add_roles(application[2].get_role(811522721824374834))
            await application[0].remove_roles(application[2].get_role(612958044132737025))
        elif str(reaction.emoji) == '❓':
            pass
        elif str(reaction.emoji) == '🚫':
            message.channel.send('')
        elif str(reaction.emoji) == '❗':
            pass


    async def quit(self, message):
        # only niko and my main can quit the bot
        if message.author.id == 440232487738671124:
            print('quitting program')
            await message.channel.send('Goodbye :wave:')
            sys.exit()
        else:
            await displayMessage(message.channel, 'Only <@' + str(440232487738671124) + '> has permission to turn me off!')


    async def warn(self, message):
        command = message.content[1:].lower().split(' ', 3)
        if message.author.guild_permissions.kick_members:
            target = message.mentions[0]
            if target == None:
                await message.channel.send('null target')
                return
            elif message.author == target:
                await message.channel.send('You cannot kick yourself')
                return

            await message.channel.send(target + ' was not warned. Unable to comply')

        else:
            await message.channel.send('You do not have the permissions to do that.')


    async def kick(self, message):
        command = message.content[1:].lower().split(' ', 2)
        if message.author.guild_permissions.kick_members:
            target = message.mentions[0]
            print(target)
            if target == None:
                await message.channel.send('null target')
                return
            # if message.author == target:
            # await message.channel.send('You cannot kick yourself')
            # return
            elif client.user == target:
                await message.channel.send('You cannot kick me like this!')
                return
            try:
                await target.kick(command[2])
                await message.channel.send(target + ' was kicked.\n Reason: ' + command[2])
            except IndexError:
                await target.kick()
                await message.channel.send(str(target) + ' was kicked.')
            else:
                await message.channel.send('An Error occured.')
        else:
            await message.channel.send('You do not have the permissions to do that.')


    async def ban(self, message):
        command = message.content[1:].lower().split(' ', 2)
        if message.author.guild_permissions.ban_members:
            target = message.mentions[0]
            print(target)
            if target == None:
                await message.channel.send('null target')
                return
            if message.author == target:
                await message.channel.send('You cannot ban yourself')
                return
            elif client.user == target:
                await message.channel.send('You cannot ban me like this!')
                return
            try:
                await target.ban(command[2])
                await message.channel.send(target + ' was banned.\n Reason: ' + command[2])
            except:
                await target.ban()
                await message.channel.send(str(target) + ' was banned.')
        else:
            await message.channel.send('You do not have the permissions to do that.')