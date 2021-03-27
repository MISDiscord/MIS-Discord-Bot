from discord.ext import commands
import pandas as pd
import os
import discord
from PIL import Image, ImageOps
import requests
from io import BytesIO

"""
Picks a random conversation topic from a spreadsheet and sends it to the channel.
"""


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="topic")
    async def topic(self, ctx):

        # Make the bot "start typing" until it grabs a random topic and then replies to the channel.
        async with ctx.channel.typing():
            file = pd.read_excel(str(os.getcwd()) + "/topics.xlsx", header=0, index_col=False, keep_default_na=True)
            topic = file.sample().iloc[0]['Topics']

        await ctx.send(topic)

    @commands.command(name="userheart")
    async def userheart(self, ctx, user: discord.Member):
        mask = Image.open('images/userheart_mask.png').convert('L')
        avatar_url = user.avatar_url
        sparkles = Image.open('images/userheart_sparkles.png')

        response = requests.get(avatar_url)

        img = ImageOps.fit(Image.open(BytesIO(response.content)).convert('RGBA'), mask.size)
        img.putalpha(mask)
        img.paste(sparkles, (0, 0), sparkles)

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
