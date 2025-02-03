import time

# todo: add a master prefix only applicable to you as a back door

async def read_line(client, channel, prompt, target, delete_prompt=True, delete_response=True):
    """
    Asks for a response from a target user. Waits for a response
    Last docstring edit: -Autumn V3.2.0
    Last method edit: -Autumn V3.5.2
    :param client: bot client
    :param channel: Channel to send a message in
    :param prompt: prompt to be sent
    :param target: What user should we read responses from
    :param delete_prompt: Do we delete the prompt?
    :param delete_response: Do we delete the response?
    :return:
    """
    show = await channel.send(prompt)
    
    def check(message):
        return message.author != client.user and message.author == target and message.channel == channel
    
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
    Extracts a user ID from a message
    Last docstring edit: -Autumn V3.5.2
    Last method edit: -Autumn V3.5.2
    :param message:
    :param arg:
    :return: Returns a user ID as an int. returns -1 if unable to complete task.
    """
    command = message.content.split(' ')
    if len(command) == arg:
        return message.author.id
    elif command[arg].isnumeric():
        return int(command[arg])
    elif len(message.mentions) == 1:
        return message.mentions[0].id
    elif message.guild is not None:
        return message.guild.get_member_named(command[1]).id
    else:
        return -1
