import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

"""
Still being worked on. Can probably be made much
more efficient when I have time.

Counts up previous messages in the channel where
the command was executed, and dms the user a
graph of message frequency over time.
"""


class Count(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="count")
    async def count(self, ctx, args):

        # Still being worked on; restrict command to a single user ID so people don't break it by mistake
        if ctx.author.id != 222479899808628736:
            return

        # Delete message that executed the command
        await ctx.message.delete()

        # Object containing previous messages
        messages = await ctx.channel.history(limit=int(args)).flatten()
        dates = []
        frequency_dictionary = {}

        # Create big array with send date of messages
        for message in messages:
            if len(str(message.created_at)[:-16]) == 10:
                # print(str(m.created_at)[:-16])
                dates.append(str(message.created_at)[:-16])

        # Create an intermediate array with sorted list of unique dates
        # noinspection PyUnresolvedReferences
        new_dates = np.sort(np.unique(dates))

        # Convert all of this to a dictionary
        for d in new_dates:
            frequency_dictionary[d] = dates.count(d)

        # Create data frame object
        d = {'Messages': [*frequency_dictionary.values()], 'Time': [*frequency_dictionary]}
        df = pd.DataFrame(data=d).set_index("Time")
        df.plot(title=f'Discord Messages in {ctx.channel.name}', figsize=(16, 7))

        # Change axis labels
        plt.xlabel("Time")  # labeling
        plt.ylabel("Messages")  # labeling

        # Draw the plot, save the image, and send to the user
        plt.draw()
        plt.savefig("image.png", dpi=300)
        await ctx.author.send(file=discord.File("image.png"))


def setup(bot):
    bot.add_cog(Count(bot))
