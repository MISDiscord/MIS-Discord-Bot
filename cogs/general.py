from discord.ext import commands
import pandas as pd
import os

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


def setup(bot):
    bot.add_cog(General(bot))
