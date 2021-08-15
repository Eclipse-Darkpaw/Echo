import discord
import os
from fileManagement import ref_path, ref_folder_path
from main import get_user_id
# TODO: allow for multiple OCs


async def set_ref(message):
    try:
        trim = message.content[8:]
        command = trim.split('\n')

        with open(ref_path(message.author.id), 'w') as refs:
            for line in command:
                try:
                    refs.write(line + '\n')
                except UnicodeEncodeError:
                    await message.channel.send('Line failed to save. Please use ASCII characters\n> ' + line)
            for ref in message.attachments:
                refs.write(ref.url + '\n')
        await message.reply(content='Refs set! Do not delete that message or the refs wont appear!' )
    except IndexError:
        await message.channel.send('No ref_sheet attached!')


async def add_ref(message):
    '''addref method
    adds a ref to a user's ref document'''
    try:
        trim = message.content[8:]
        command = trim.split('\n')

        with open(ref_path(message.author.id), 'a') as refs:
            for line in command:
                try:
                    refs.write(line + '\n')
                except UnicodeEncodeError:
                    for char in line:
                        try:
                            refs.write(char)
                        except UnicodeEncodeError:
                            await message.channel.send('Line failed to save. Please use ASCII characters\n> ' + char)
            for ref in message.attachments:
                refs.write(ref.url + '\n')
        await message.reply(content='Refs added!')
    except IndexError:
        await message.channel.send('No ref_sheet attached!')


async def add_char(message):
    #>refs add_char <name> <description/ref>
    '''creates a new characters ref file'''
    command = message.content.split(' ',3)
    target = message.author.id
    target_folder = ref_folder_path(target)
    target_file = target_folder + '\\' + command[2] + '.ref'
    try:
        open(target_file, 'x')
    except FileExistsError:
        return -1
    if len(command) == 4:
        with open(target_file, 'w') as file:
            try:
                file.write(command[3] + '\n')
            except UnicodeEncodeError:
                await message.channel.send('Line failed to save. Please use ASCII characters\n> ' + line)
            attachments = message.attachments
            for attachment in attachments:
                file.write(attachment.url)
    message.reply('OC created.')


    os.mkdir(command[2],)


async def list_chars_in_dir(message):
    # shows a list of the chars/folders in the current directory
    # >OC
    pass


async def ref(message):
    # NOTE: THIS METHOD NEEDS MEMBERS INTENT ACTIVE
    command = message.content.split(' ', 2)
    if command[1] == 'set':
        set_ref(message)
    elif command[1] == 'add':
        add_ref()
    else:
        target = get_user_id(message)

        if target == None:
            await message.channel.send('User not found.')
            return

        msg = await message.channel.send('Finding ref, please wait')
        try:
            ref_sheet = open(ref_path(target))
            await msg.edit(content='Ref Found! Uploading, Please wait!')
            await message.reply(content=ref_sheet.read())
        except FileNotFoundError:
            await msg.edit(content='User has not set their ref.')


async def create_OC(message):
    #>OC create_folder <folder> <name> <path>
    command = message.content.split(' ',4)
    os.mkdir()


async def file_tree(message):
    await message.reply('Traversing the file tree. This may take a while')
    file = 'C:\\Users\\leebe\\Desktop\\Bot-files\\' + str(message.author.id)
    os.chdir(file)
    tree = '```'
    #pre-order algorithm
    #foldername
    def preorder(root, tree, depth, is_last_branch):
        children = os.listdir()
        # folder names cannot contain .
        if len children > 0:
            for child in children:
                predorder(child, depth + 1)

    folder =

    tree = tree + #file name
    #pre order


    tree = tree + '```'
    children = None

    await
    '''
    root
    ├───folder 1
    │   ├───OC1
    │   │   ├───images.ref
    │   │   └───description.txt
    │   └───sub 2
    ├───folder 2
    ├───folder 3
    └───folder 4
        ├───sub 1
        └───sub 2
    '''
