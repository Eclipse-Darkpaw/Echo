import os

import discord
from discord.ext import commands
from fileManagement import ref_path, nsfw_ref_path


class RefManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def set_ref(self, ctx: discord.Interaction):
        try:
            trim = ctx.message.content[8:]
            command = trim.split('\n')

            if ctx.channel.nsfw:
                path = nsfw_ref_path(ctx.author.id)
            else:
                path = ref_path(ctx.author.id)

            with open(path, 'w') as refs:
                for line in command:
                    try:
                        refs.write(line + '\n')
                    except UnicodeEncodeError:
                        await ctx.send('Line failed to save. Please use ASCII characters\n> ' + line)
                for ref in ctx.message.attachments:
                    refs.write(ref.url + '\n')
            await ctx.reply(content='Refs set! Do not delete that message or the refs wont appear!')
        except IndexError:
            await ctx.send('No ref_sheet attached!')

    @commands.hybrid_command()
    async def add_ref(self, ctx):
        """add_ref method
        adds a ref to a user's ref document"""
        try:

            if ctx.channel.nsfw:
                path = nsfw_ref_path(ctx.author.id)
            else:
                path = ref_path(ctx.author.id)

            with open(path, 'a') as refs:
                for line in ctx.message.content:
                    try:
                        refs.write(line + '\n')
                    except UnicodeEncodeError:
                        for char in line:
                            try:
                                refs.write(char)
                            except UnicodeEncodeError:
                                await ctx.send('Line failed to save. Please use ASCII characters\n> ' + char)
                for ref_sheet in ctx.message.attachments:
                    refs.write(ref_sheet.url + '\n')
            await ctx.reply(content='Refs added!')
        except IndexError:
            await ctx.send('No ref attached!')

    @commands.hybrid_command()
    async def ref(self, ctx: discord.Interaction, user: discord.User = None):

        if user is None:
            target = ctx.author.id
        else:
            target = user.id

        msg = await ctx.send('Finding ref, please wait')
        try:

            if ctx.channel.nsfw:
                path = nsfw_ref_path(target)
            else:
                path = ref_path(target)
            ref_sheet = open(path)
            await msg.edit(content='Ref Found! Uploading, Please wait!')
            await ctx.reply(content=ref_sheet.read())
        except FileNotFoundError:
            if ctx.channel.nsfw:
                await msg.edit(content='User has not set NSFW ref. Retrieving SFW ref')
                path = ref_path(target)
                ref_sheet = open(path)
                await msg.edit(content='Ref Found! Uploading, Please wait!')
                await ctx.reply(content=ref_sheet.read())
            else:
                await msg.edit(content='User has not set their SFW ref.')
