from discord.ext import commands
import pandas as pd
import os
import discord
from PIL import Image, ImageOps
import requests
from io import BytesIO, StringIO
from datetime import datetime

"""
General commands
"""


async def has_permission(ctx):
    # Restrict command.
    t_mod = discord.utils.get(ctx.guild.roles, name="Trial Moderator")
    mod = discord.utils.get(ctx.guild.roles, name="Moderator")
    sr_mod = discord.utils.get(ctx.guild.roles, name="Senior Moderator")
    if t_mod or mod or sr_mod in ctx.author.roles:
        return True
    else:
        return False


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="channellogs", aliases=["logs"])
    @commands.check(has_permission)
    async def channellogs(self, ctx, count: int, *selected_channel: discord.TextChannel):
        start = datetime.now()
        if count > 1000:
            await ctx.send("Error! Please do not log more than 1,000 messages!")
            return

        if selected_channel:
            channel = selected_channel[0]
        else:
            channel = ctx.channel
        try:
            with open(f"logs/{channel.id}-{channel.name}.txt", "r", encoding="utf8") as f:
                lines = f.readlines()[-1*count:]
                f.close()
        except FileNotFoundError:
            await ctx.send("There do not seem to be any logs for that channel!")
            return

        with StringIO() as file_binary:
            for line in lines:
                print(line)
                file_binary.write(line)
            file_binary.seek(0)
            await ctx.send(f"Returned last {count} messages from {channel.mention} in "
                           f"{str(datetime.now() - start)[6:]} seconds.")
            await ctx.send(file=discord.File(fp=file_binary,
                                             filename=f"{str(datetime.now())[:-7]}-{channel.name}-message-logs.txt"))
            file_binary.close()

    @channellogs.error
    async def messagelog_error(self, ctx, err):
        if isinstance(err, discord.ext.commands.MissingRequiredArgument):
            await ctx.send("Please provide a number of messages to retrieve the logs for!")
        if isinstance(err, discord.ext.commands.BadArgument):
            await ctx.send("Input could not be understood! "
                           "Please be sure to provide an integer value for the number of messages to retrieve logs for, "
                           "as well as the specified channel.")

    @commands.command(name="messagelog")
    @commands.check(has_permission)
    async def messagelog(self, ctx, count: int, *channel: discord.TextChannel):
        await ctx.message.delete()

        if count > 1000:
            await ctx.send("Error! Please do not log more than 1,000 messages.")
            return

        with StringIO() as file_binary:
            async for message in ctx.channel.history(limit=count):
                time = message.created_at
                user = f"{message.author.name}#{message.author.discriminator}"
                file_binary.write(f"[{time}] ({message.author.id}) {user}: {message.system_content}\n")
            file_binary.seek(0)
            if channel:
                print(channel[0])
                await channel[0].send(file=discord.File(fp=file_binary, filename=f"{str(datetime.now())[:-7]}-log.txt"))
            else:
                await ctx.send(file=discord.File(fp=file_binary, filename=f"{str(datetime.now())[:-7]}-log.txt"))
            file_binary.close()

    @messagelog.error
    async def messagelog_error(self, ctx, err):
        print(err)
        if isinstance(err, discord.ext.commands.MissingRequiredArgument):
            await ctx.send("Please provide a number of messages to log!")
        if isinstance(err, discord.ext.commands.BadArgument):
            await ctx.send("Input could not be understood! "
                           "Please be sure to provide an integer value for the number of messages to log.")

    @commands.command(name="joinvc")
    @commands.check(has_permission)
    async def joinvc(self, ctx):
        channel = ctx.author.voice.channel
        await channel.connect()

    @commands.command(name="leavevc")
    @commands.check(has_permission)
    async def leavevc(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command(name="send")
    @commands.check(has_permission)
    async def send(self, ctx, channel: discord.TextChannel, *content):
        await channel.send(str(' '.join(content)))
        await ctx.message.delete()

    @send.error
    async def send_error(self, ctx, err):
        print(err)
        if isinstance(err, discord.ext.commands.MissingRequiredArgument):
            await ctx.send("Please provide a text channel to send the message to!")

    @commands.command(name="topic")
    async def topic(self, ctx):

        # Make the bot "start typing" until it grabs a random topic and then replies to the channel.
        async with ctx.channel.typing():
            file = pd.read_excel(str(os.getcwd()) + "/topics.xlsx", header=0, index_col=False, keep_default_na=True)
            topic = file.sample().iloc[0]['Topics']

        await ctx.send(topic)

    @commands.command(name="sparkleheart")
    async def sparkleheart(self, ctx, *users: discord.Member):
        mask = Image.open('images/userheart_mask.png').convert('L')
        sparkles = Image.open('images/userheart_sparkles.png')

        for user in users:
            avatar_url = user.avatar_url

            response = requests.get(avatar_url)

            img = ImageOps.fit(Image.open(BytesIO(response.content)).convert('RGBA'), mask.size)
            img.putalpha(mask)
            img.paste(sparkles, (0, 0), sparkles)

            with BytesIO() as image_binary:
                img.save(image_binary, 'PNG')
                image_binary.seek(0)
                await ctx.send(file=discord.File(fp=image_binary, filename="userheart.png"))

    @sparkleheart.error
    async def sparkleheart_error(self, ctx, err):
        print(err)
        if isinstance(err, discord.ext.commands.MissingRequiredArgument):
            await ctx.send("Please mention a user!")
        if isinstance(err, discord.ext.commands.MemberNotFound):
            await ctx.send("Please provide a valid member!")

    @commands.command(name="userheart")
    async def userheart(self, ctx, *users: discord.Member):
        mask = Image.open('images/userheart_mask.png').convert('L')
        sparkles = Image.open('images/userheart_sparkles.png')

        for user in users:
            avatar_url = user.avatar_url

            response = requests.get(avatar_url)

            img = ImageOps.fit(Image.open(BytesIO(response.content)).convert('RGBA'), mask.size)
            img.putalpha(mask)

            with BytesIO() as image_binary:
                img.save(image_binary, 'PNG')
                image_binary.seek(0)
                await ctx.send(file=discord.File(fp=image_binary, filename="userheart.png"))

    @userheart.error
    async def userheart_error(self, ctx, err):
        print(err)
        if isinstance(err, discord.ext.commands.MissingRequiredArgument):
            await ctx.send("Please mention a user!")
        if isinstance(err, discord.ext.commands.MemberNotFound):
            await ctx.send("Please provide a valid member!")


def setup(bot):
    bot.add_cog(General(bot))
