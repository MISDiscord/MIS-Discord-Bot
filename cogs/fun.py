from discord.ext import commands
import discord
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gayimage")
    async def gay(self, ctx):
        if ctx.message.reference:
            for attachment in ctx.message.reference.resolved.attachments:
                height = attachment.height
                width = attachment.width

                url = f"https://some-random-api.ml/canvas/gay?avatar={attachment.url}"
                response = requests.get(url)

                img = Image.open(BytesIO(response.content))
                img = img.resize((width, height))

                with BytesIO() as image_binary:
                    img.save(image_binary, 'PNG')
                    image_binary.seek(0)
                    await ctx.send(file=discord.File(fp=image_binary, filename="image0.png"))


def setup(bot):
    bot.add_cog(Fun(bot))
