
async def mute(message, mute_role_id):
    target = get_user_id(message)
    await message.guild.get_member(target).add_roles(message.guild.get_role(mute_role_id))
    await message.channel.send(content='<@!'+target+'> was muted.' ''',file=open('resources\\mute.jpg','rb')''')