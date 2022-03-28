"""
Main class. Contains basic methods used by all bots
"""
version_num = '2.0.0'


async def read_line(client, channel, prompt, target, delete_prompt=True, delete_response=True):
    show = await channel.send(prompt)

    def check(msg):
        return msg.author != client.user and msg.author == target and msg.channel == channel

    msg = await client.wait_for('message', check=check)

    if delete_response:
        try:
            await msg.delete()
        finally:
            pass
    if delete_prompt:
        await show.delete()

    return msg


# NOTE: THIS METHOD NEEDS MEMBERS INTENT ACTIVE
def get_user_id(message, arg=1):
    """

    :param message:
    :param arg:
    :return:
    """
    command = message.content.split(' ')
    if len(command) == arg:
        target = message.author.id
    elif len(command[arg]) == 18:
        target = int(command[arg])
    elif len(message.mentions) == 1:
        target = message.mentions[0].id
    else:
        target = message.guild.get_member_named(command[1]).id

    return target

'''RNG base on a string a human creates then converts each word into an int by using its position on the list of words.
add each int and mod '''